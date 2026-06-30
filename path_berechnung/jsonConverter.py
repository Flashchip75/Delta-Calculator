import math


class UIProfileConverter:
    def __init__(self, default_N=100, debug=True):
        self.default_N = default_N
        self.DEBUG = debug

    # -------------------------
    # Debug helper
    # -------------------------
    def _log(self, msg, **kwargs):
        if not self.DEBUG:
            return
        print(f"[UIProfileConverter] {msg}")
        if kwargs:
            for k, v in kwargs.items():
                print(f"    {k}: {v}")

    # -------------------------
    # Public API
    # -------------------------
    def convert(self, geometries, timeLaws, profile_name):
        self._log("convert() called",
                  profile_name=profile_name,
                  n_geometries=len(geometries))

        if profile_name is None:
            raise ValueError("profile_name must be provided for convert() method.")

        result = {
            profile_name: [
                self._map_geometry(g, timeLaws)
                for g in geometries
            ]
        }

        self._log("convert() finished")
        return result

    def convert_flat(self, geometries, timeLaws):
        self._log("convert_flat() called", n=len(geometries))

        out = []
        for i, g in enumerate(geometries):
            self._log(f"geometry[{i}] input", type=type(g).__name__, repr=str(g))

            mapped = self._map_geometry(g, timeLaws)

            self._log(f"geometry[{i}] mapped", result=mapped)
            out.append(mapped)

        self._log("convert_flat() finished")
        return out

    # -------------------------
    # Internal helpers
    # -------------------------
    def _val(self, x):
        return x[0] if isinstance(x, tuple) else x

    def _vec3(self, p):
        return [p[0], p[1], p[2]]

    # -------------------------
    # Arc helper
    # -------------------------
    def _get_arc_axes(self, plane: str):
        self._log("get_arc_axes()", plane=plane, type=type(plane).__name__)

        if not isinstance(plane, str):
            raise TypeError(f"Plane must be string, got {type(plane)}")

        plane = plane.lower().strip()
        self._log("normalized plane", plane=plane)

        if plane == "xy":
            return 0, 1
        elif plane == "xz":
            return 0, 2
        elif plane == "yz":
            return 1, 2

        if len(plane) == 1:
            fallback = {
                "x": (1, 2),
                "y": (0, 2),
                "z": (0, 1),
            }
            result = fallback.get(plane, (0, 1))
            self._log("fallback plane used", result=result)
            return result

        raise ValueError(f"Unknown plane: {plane}")

    # -------------------------
    # Time law mapping
    # -------------------------
    def _map_time_law(self, tl):
        self._log("map_time_law()", type=type(tl).__name__ if tl else None)

        if tl is None:
            return {"type": "konstant"}

        name = tl.__class__.__name__
        self._log("time law resolved", name=name)

        if name == "ConstantVelocity":
            return {"type": "konstant"}

        if name == "Polynomial5":
            out = {
                "dauer": self._val(tl.duration),
                "ziel_v": self._val(tl.end_velocity),
                "ziel_a": self._val(tl.end_acceleration),
            }
            self._log("Polynomial5 mapped", out=out)
            return out

        if name == "Polynomial7":
            out = {
                "dauer": self._val(tl.duration),
                "ziel_v": self._val(tl.end_velocity),
                "ziel_a": self._val(tl.end_acceleration),
                "ziel_j": self._val(tl.end_jerk),
            }
            self._log("Polynomial7 mapped", out=out)
            return out

        raise ValueError(f"Unknown time law: {name}")

    # -------------------------
    # Geometry mapping
    # -------------------------
    def _map_geometry(self, g, timeLaws):
        if g is None:
            self._log("geometry is None")
            return None

        raw_type = type(g).__name__

        TYPE_MAP = {
            "Line": "line",
            "Arc": "arc",
            "Bezier": "bezier",
            "LINE": "line",
            "ARC": "arc",
            "BEZIER": "bezier",
        }

        typ = TYPE_MAP.get(raw_type)

        self._log("map_geometry()",
                  raw_type=raw_type,
                  mapped_type=typ,
                  object=str(g))

        if typ is None:
            raise ValueError(f"Unsupported geometry type: {raw_type}")

        # ---------------- LINE ----------------
        if typ == "line":
            out = {
                "type": "line",
                "pts": [list(g.start), list(g.end)],
                "time_law": int(g.time_law_ref),
            }

            self._log("line output", out=out)
            return out

        # ---------------- ARC ----------------
        elif typ == "arc":
            u_idx, v_idx = self._get_arc_axes(g.plane)

            # unit vectors in 3D
            axes = [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
            ]

            u = axes[u_idx]
            v = axes[v_idx]

            return {
                "type": "arc",
                "c": list(g.center),
                "r": float(g.radius[0]),
                "u": u,
                "v": v,
                "a": [
                    float(g.start_angle[0]),
                    float(g.end_angle[0])
                ],
                "time_law": int(g.time_law_ref),
            }

        # ---------------- BEZIER ----------------
        elif typ == "bezier":
            out = {
                "type": "bezier",
                "pts": [
                    list(g.p0),
                    list(g.p1),
                    list(g.p2),
                    list(g.p3),
                ],
                "time_law": int(g.time_law_ref),
            }

            self._log("bezier output", out=out)
            return out

        raise ValueError(f"Unsupported geometry type: {typ}")

    # -------------------------
    # Safety helper
    # -------------------------
    def _is_nan(self, x):
        try:
            return math.isnan(x)
        except:
            return False