import math


class UIProfileConverter:
    def __init__(self, default_N):
        self.default_N = default_N

    # =========================================================
    # PUBLIC API
    # =========================================================

    def convert_ui_data_to_solver_input(self, ui_data):
        """
        Liefert direkt das Format für Trajectory:
        → Liste von Segment-Dictionaries
        """
        geometries, time_laws = ui_data

        return [
            self._map_geometry(g, time_laws)
            for g in geometries
        ]

    # =========================================================
    # BASIC HELPERS
    # =========================================================

    def _val(self, x):
        return x[0] if isinstance(x, tuple) else x

    def _vec3(self, p):
        return [p[0], p[1], p[2]]

    def _is_nan(self, x):
        try:
            return math.isnan(x)
        except:
            return False

    # =========================================================
    # TIME LAW MAPPING
    # =========================================================

    def _map_time_law(self, tl):
        if tl is None:
            return {"type": "konstant"}

        name = tl.__class__.__name__

        if name == "ConstantVelocity":
            return {"type": "konstant"}

        if name == "Polynomial5":
            return {
                "type": "poly5",
                "dauer": self._val(tl.duration),
                "ziel_v": self._val(tl.end_velocity),
                "ziel_a": self._val(tl.end_acceleration),
            }

        if name == "Polynomial7":
            return {
                "type": "poly7",
                "dauer": self._val(tl.duration),
                "ziel_v": self._val(tl.end_velocity),
                "ziel_a": self._val(tl.end_acceleration),
                "ziel_j": self._val(tl.end_jerk),
            }

        raise ValueError(f"Unknown time law: {name}")

    # =========================================================
    # GEOMETRY MAPPING
    # =========================================================

    def _map_geometry(self, obj, time_laws):
        tl = None

        if hasattr(obj, "time_law_ref") and not self._is_nan(obj.time_law_ref):
            tl = time_laws[int(obj.time_law_ref)]

        dynamik = self._map_time_law(tl)
        name = obj.__class__.__name__

        # ---- Line ----
        if name == "Line":
            return {
                "type": "Line",
                "pts": [self._vec3(obj.start), self._vec3(obj.end)],
                "N": self.default_N,
                "dynamik": dynamik,
            }

        # ---- Bezier ----
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
                "dynamik": dynamik,
            }

        # ---- Arc ----
        if name == "Arc":
            plane = obj.plane
            if isinstance(plane, list):
                plane = plane[0]

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
                "dynamik": dynamik,
            }

        # ---- Wait ----
        if name == "Wait":
            return {
                "type": "Line",
                "pts": [[0, 0, 0], [0, 0, 0]],
                "N": 2,
                "dynamik": {
                    "type": "warten",
                    "dauer": self._val(obj.duration),
                },
            }

        raise ValueError(f"Unknown geometry: {name}")

    def _get_arc_axes(self, plane):
        if plane == "xy":
            return [1, 0, 0], [0, 1, 0]
        if plane == "xz":
            return [1, 0, 0], [0, 0, 1]
        if plane == "yz":
            return [0, 1, 0], [0, 0, 1]
        raise ValueError(f"Unknown plane: {plane}")