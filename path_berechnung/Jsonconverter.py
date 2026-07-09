import math


class UIProfileConverter:
    def __init__(self, default_N=100):
        self.default_N = default_N

    # =========================================================
    # PUBLIC API
    # =========================================================

    def convert_ui_data_to_solver_input(self, ui_data):
        """
        Erwartet:
            ui_data = (geometries, time_laws)

        Gibt das alte flache Format zurueck, das Trajectory(j_data) erwartet:
            [
                {"type": "Line", ...},
                {"type": "Bezier", ...},
                ...
            ]

        Die Zeitgesetze werden ueber time_law_ref zugeordnet und als
        "dynamik" in jedes Segment geschrieben.
        """

        geometries, time_laws = ui_data

        j_data = []

        current_position = [0.0, 0.0, 0.0]
        current_group_id = -1
        last_ref = None

        for obj in geometries:
            name = obj.__class__.__name__

            if name == "Wait":
                cfg = self._map_wait(obj, current_position)
                cfg["path_group"] = current_group_id + 1
                cfg["time_law_ref"] = None
                j_data.append(cfg)

                current_group_id += 1
                last_ref = None
                continue

            ref = self._get_time_law_ref(obj)

            if ref != last_ref:
                current_group_id += 1
                last_ref = ref

            cfg = self._map_geometry(obj)
            cfg["dynamik"] = self._map_time_law_by_ref(ref, time_laws)
            cfg["time_law_ref"] = ref
            cfg["path_group"] = current_group_id

            j_data.append(cfg)

            current_position = self._get_end_position(obj)

        return j_data

    def convert_flat(self, geometries, time_laws):
        """
        Falls irgendwo noch convert_flat(...) aufgerufen wird.
        """
        return self.convert_ui_data_to_solver_input((geometries, time_laws))

    def convert(self, geometries, time_laws, profile_name="profile"):
        """
        Falls irgendwo noch convert(...) aufgerufen wird.
        """
        return {
            profile_name: self.convert_flat(geometries, time_laws)
        }

    # =========================================================
    # GEOMETRY MAPPING
    # =========================================================

    def _map_geometry(self, obj):
        name = obj.__class__.__name__

        if name == "Line":
            return {
                "type": "Line",
                "pts": [
                    self._vec3(obj.start),
                    self._vec3(obj.end)
                ],
                "N": self.default_N,
            }

        if name == "Bezier":
            return {
                "type": "Bezier",
                "pts": [
                    self._vec3(obj.p0),
                    self._vec3(obj.p1),
                    self._vec3(obj.p2),
                    self._vec3(obj.p3),
                ],
                "N": self.default_N,
            }

        if name == "Arc":
            plane = self._get_plane_value(obj.plane)
            u, v = self._get_arc_axes(plane)

            return {
                "type": "Arc",
                "c": self._vec3(obj.center),
                "r": self._val(obj.radius),
                "u": u,
                "v": v,
                "a": [
                    self._val(obj.start_angle),
                    self._val(obj.end_angle),
                ],
                "N": self.default_N,
            }

        raise ValueError(f"Unknown geometry: {name}")

    def _map_wait(self, obj, current_position):
        """
        Wait wird fuer das alte Trajectory-Format als Null-Linie dargestellt.
        Dadurch kann Trajectory weiterhin mit type='Line' arbeiten.
        """

        return {
            "type": "Line",
            "pts": [
                list(current_position),
                list(current_position)
            ],
            "N": 2,
            "dynamik": {
                "type": "warten",
                "dauer": self._val(obj.duration),
            },
        }

    # =========================================================
    # TIME LAW MAPPING
    # =========================================================

    def _map_time_law_by_ref(self, ref, time_laws):
        if ref == -1:
            return {"type": "konstant"}
        
        if ref < 0 or ref >= len(time_laws):
            raise IndexError(
                f"time_law_ref {ref} is out of range for time_laws with length {len(time_laws)}."
            )

        return time_laws[ref]

    def _map_time_law(self, tl):
        if tl is None:
            return {
                "type": "konstant"
            }

        name = tl.__class__.__name__

        if name == "ConstantVelocity":
            return {
                "type": "konstant"
            }

        if name == "Polynomial5":
            data = {
                "type": "poly5",
                "dauer": self._val(tl.duration),
                "ziel_v": self._val(tl.end_velocity),
                "ziel_a": self._val(tl.end_acceleration),
            }

            if hasattr(tl, "start_acceleration"):
                data["start_a"] = self._val(tl.start_acceleration)

            return data

        if name == "Polynomial7":
            data = {
                "type": "poly7",
                "dauer": self._val(tl.duration),
                "ziel_v": self._val(tl.end_velocity),
                "ziel_a": self._val(tl.end_acceleration),
                "ziel_j": self._val(tl.end_jerk),
            }

            if hasattr(tl, "start_acceleration"):
                data["start_a"] = self._val(tl.start_acceleration)

            if hasattr(tl, "start_jerk"):
                data["start_j"] = self._val(tl.start_jerk)

            return data

        raise ValueError(f"Unknown time law: {name}")

    # =========================================================
    # POSITION HELPERS
    # =========================================================

    def _get_end_position(self, obj):
        name = obj.__class__.__name__

        if name == "Line":
            return self._vec3(obj.end)

        if name == "Bezier":
            return self._vec3(obj.p3)

        if name == "Arc":
            center = self._vec3(obj.center)
            radius = self._val(obj.radius)

            plane = self._get_plane_value(obj.plane)
            u, v = self._get_arc_axes(plane)

            end_angle = self._val(obj.end_angle)

            return [
                center[0] + radius * (
                    math.cos(end_angle) * u[0]
                    + math.sin(end_angle) * v[0]
                ),
                center[1] + radius * (
                    math.cos(end_angle) * u[1]
                    + math.sin(end_angle) * v[1]
                ),
                center[2] + radius * (
                    math.cos(end_angle) * u[2]
                    + math.sin(end_angle) * v[2]
                ),
            ]

        raise ValueError(f"Unknown geometry: {name}")

    # =========================================================
    # BASIC HELPERS
    # =========================================================

    def _get_time_law_ref(self, obj):
        if not hasattr(obj, "time_law_ref"):
            raise ValueError(
                f"{obj.__class__.__name__} has no time_law_ref."
            )

        ref = obj.time_law_ref

        if self._is_nan(ref):
            return None

        return int(ref)

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