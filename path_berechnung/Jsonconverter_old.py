import math
import numpy as np


class UIProfileConverter:
    def __init__(self, default_N=100, add_N=True, include_polynomial_type=False):
        self.default_N = default_N
        self.add_N = add_N
        self.include_polynomial_type = include_polynomial_type

    # =====================================================
    # Public API
    # =====================================================

    def convert_ui_data_to_solver_input(self, ui_data):
        """
        Wandelt UI-Daten in gruppierte alte Profil-Daten um.

        Input:
            ui_data = (pfade, zeitgesetze)

        Output:
            pfad_config_liste:
                Liste von Kurvengruppen.
                Jede Gruppe ist eine Liste alter Kurven-Dictionaries.
                Diese Gruppen koennen danach einzeln in die Punktewolken-
                Funktion gegeben werden.

            dynamik_liste:
                Liste von Dynamik-Dictionaries.
                dynamik_liste[i] gehoert zu pfad_config_liste[i].
        """

        pfade, zeitgesetze = ui_data

        pfad_config_liste = []
        dynamik_liste = []

        current_ref = None
        current_group = []

        last_position = [0.0, 0.0, 0.0]

        def close_current_group():
            nonlocal current_ref, current_group

            if not current_group:
                return

            time_law = self._get_time_law_by_ref(current_ref, zeitgesetze)
            dynamik = self._map_time_law(time_law)

            pfad_config_liste.append(current_group)
            dynamik_liste.append(dynamik)

            current_ref = None
            current_group = []

        for curve in pfade:
            curve_name = curve.__class__.__name__

            if curve_name == "Wait":
                close_current_group()

                wait_cfg = self._map_wait(curve, last_position)

                pfad_config_liste.append([wait_cfg])
                dynamik_liste.append({
                    "type": "warten",
                    "dauer": self._val(curve.duration)
                })

                continue

            ref = getattr(curve, "time_law_ref", None)

            if ref is None or self._is_nan(ref):
                raise ValueError(
                    f"Moving curve {curve_name} has no valid time_law_ref."
                )

            ref = int(ref)

            curve_cfg = self._map_curve(curve)
            last_position = self._get_curve_end_position(curve)

            if not current_group:
                current_ref = ref
                current_group = [curve_cfg]
                continue

            if ref == current_ref:
                current_group.append(curve_cfg)
            else:
                close_current_group()
                current_ref = ref
                current_group = [curve_cfg]

        close_current_group()

        return pfad_config_liste, dynamik_liste

    def convert_ui_data_to_grouped_profile(self, ui_data, base_name="profile"):
        """
        Optional zum Debuggen.

        Gibt jede Gruppe als eigenes altes Profil aus:

        {
            "profile_1": [...],
            "profile_2": [...],
            ...
        }

        Die Dynamik wird separat mitgegeben.
        """

        pfad_config_liste, dynamik_liste = self.convert_ui_data_to_solver_input(ui_data)

        profiles = {}

        for i, group in enumerate(pfad_config_liste):
            profiles[f"{base_name}_{i + 1}"] = group

        return profiles, dynamik_liste

    def convert_ui_data_to_flat_profile(self, ui_data, profile_name="profile"):
        """
        Optional zum Anschauen oder Speichern.

        Gibt ein flaches altes Profil zurueck.
        Dabei wird die Dynamik in jede Kurve geschrieben.

        Wichtig:
        Fuer den echten MainSolve mit gemeinsamer Dynamik pro Pfadgruppe
        ist convert_ui_data_to_solver_input() sauberer.
        """

        pfad_config_liste, dynamik_liste = self.convert_ui_data_to_solver_input(ui_data)

        flat_profile = []

        for group, dynamik in zip(pfad_config_liste, dynamik_liste):
            for curve_cfg in group:
                cfg = dict(curve_cfg)
                cfg["dynamik"] = dynamik
                flat_profile.append(cfg)

        return {
            profile_name: flat_profile
        }

    # =====================================================
    # Geometry mapping: UI curve -> old curve dict
    # =====================================================

    def _map_curve(self, curve):
        curve_name = curve.__class__.__name__

        if curve_name == "Line":
            cfg = {
                "type": "Line",
                "pts": [
                    self._vec3(curve.start),
                    self._vec3(curve.end)
                ]
            }

            self._add_N_if_enabled(cfg)
            return cfg

        if curve_name == "Bezier":
            cfg = {
                "type": "Bezier",
                "pts": [
                    self._vec3(curve.p0),
                    self._vec3(curve.p1),
                    self._vec3(curve.p2),
                    self._vec3(curve.p3)
                ]
            }

            self._add_N_if_enabled(cfg)
            return cfg

        if curve_name == "Arc":
            plane = self._get_plane_value(curve.plane)
            u, v = self._get_arc_axes(plane)

            cfg = {
                "type": "Arc",
                "c": self._vec3(curve.center),
                "r": self._val(curve.radius),
                "u": u,
                "v": v,
                "a": [
                    self._val(curve.start_angle),
                    self._val(curve.end_angle)
                ]
            }

            self._add_N_if_enabled(cfg)
            return cfg

        raise ValueError(f"Unknown curve type: {curve_name}")

    def _map_wait(self, curve, last_position):
        cfg = {
            "type": "Line",
            "pts": [
                list(last_position),
                list(last_position)
            ]
        }

        if self.add_N:
            cfg["N"] = 2

        return cfg

    # =====================================================
    # Time law mapping: UI time law -> old dynamics dict
    # =====================================================

    def _map_time_law(self, time_law):
        if time_law is None:
            return {
                "type": "konstant"
            }

        name = time_law.__class__.__name__

        if name == "ConstantVelocity":
            return {
                "type": "konstant"
            }

        if name == "Polynomial5":
            data = {}

            if self.include_polynomial_type:
                data["type"] = "polynom5"

            data["dauer"] = self._val(time_law.duration)
            data["ziel_v"] = self._val(time_law.end_velocity)
            data["ziel_a"] = self._val(time_law.end_acceleration)

            if hasattr(time_law, "start_acceleration"):
                data["start_a"] = self._val(time_law.start_acceleration)

            return data

        if name == "Polynomial7":
            data = {}

            if self.include_polynomial_type:
                data["type"] = "polynom7"

            data["dauer"] = self._val(time_law.duration)
            data["ziel_v"] = self._val(time_law.end_velocity)
            data["ziel_a"] = self._val(time_law.end_acceleration)
            data["ziel_j"] = self._val(time_law.end_jerk)

            if hasattr(time_law, "start_acceleration"):
                data["start_a"] = self._val(time_law.start_acceleration)

            if hasattr(time_law, "start_jerk"):
                data["start_j"] = self._val(time_law.start_jerk)

            return data

        raise ValueError(f"Unknown time law: {name}")

    # =====================================================
    # Helpers
    # =====================================================

    def _get_time_law_by_ref(self, ref, time_laws):
        if ref is None or self._is_nan(ref):
            return None

        ref = int(ref)

        if ref < 0 or ref >= len(time_laws):
            raise IndexError(
                f"time_law_ref {ref} is out of range for time_laws "
                f"with length {len(time_laws)}."
            )

        return time_laws[ref]

    def _get_curve_end_position(self, curve):
        curve_name = curve.__class__.__name__

        if curve_name == "Line":
            return self._vec3(curve.end)

        if curve_name == "Bezier":
            return self._vec3(curve.p3)

        if curve_name == "Arc":
            center = np.array(self._vec3(curve.center), dtype=float)
            radius = float(self._val(curve.radius))

            plane = self._get_plane_value(curve.plane)
            u, v = self._get_arc_axes_np(plane)

            end_angle = float(self._val(curve.end_angle))

            point = center + radius * (
                math.cos(end_angle) * u
                + math.sin(end_angle) * v
            )

            return point.tolist()

        raise ValueError(f"Unknown curve type: {curve_name}")

    def _add_N_if_enabled(self, cfg):
        if self.add_N:
            cfg["N"] = self.default_N

    def _val(self, x):
        if isinstance(x, tuple):
            return x[0]

        return x

    def _vec3(self, p):
        return [
            self._val(p[0]),
            self._val(p[1]),
            self._val(p[2])
        ]

    def _is_nan(self, x):
        try:
            return math.isnan(x)
        except TypeError:
            return False

    def _get_plane_value(self, plane):
        if isinstance(plane, list):
            if len(plane) == 0:
                raise ValueError("Plane list is empty.")

            return plane[0]

        return plane

    def _get_arc_axes(self, plane):
        if plane == "xy":
            return [1, 0, 0], [0, 1, 0]

        if plane == "xz":
            return [1, 0, 0], [0, 0, 1]

        if plane == "yz":
            return [0, 1, 0], [0, 0, 1]

        raise ValueError(f"Unknown plane: {plane}")

    def _get_arc_axes_np(self, plane):
        u, v = self._get_arc_axes(plane)

        return (
            np.array(u, dtype=float),
            np.array(v, dtype=float)
        )