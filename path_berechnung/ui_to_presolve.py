class UIToPresolveConverter:
    def __init__(self, default_N=100):
        self.default_N = default_N

    def convert_ui_data(self, ui_data):
        pfade, zeitgesetze = ui_data
        return self.convert_path(pfade)

    def convert_curve(self, curve):
        name = curve.__class__.__name__

        if name == "Line":
            return {
                "type": "Line",
                "pts": [
                    self._vec3(curve.start),
                    self._vec3(curve.end)
                ],
                "N": self.default_N
            }

        if name == "Bezier":
            return {
                "type": "Bezier",
                "pts": [
                    self._vec3(curve.p0),
                    self._vec3(curve.p1),
                    self._vec3(curve.p2),
                    self._vec3(curve.p3)
                ],
                "N": self.default_N
            }

        if name == "Arc":
            plane = self._plane_value(curve.plane)
            u, v = self._plane_to_uv(plane)

            return {
                "type": "Arc",
                "c": self._vec3(curve.center),
                "r": self._val(curve.radius),
                "u": u,
                "v": v,
                "a": [
                    self._val(curve.start_angle),
                    self._val(curve.end_angle)
                ],
                "N": self.default_N
            }

        if name == "Wait":
            return None

        raise ValueError(f"Unknown curve type: {name}")

    def convert_path(self, path):
        configs = []

        for curve in path:
            cfg = self.convert_curve(curve)

            if cfg is not None:
                configs.append(cfg)

        return configs

    def _val(self, x):
        if isinstance(x, tuple):
            return x[0]
        return x

    def _vec3(self, p):
        return [p[0], p[1], p[2]]

    def _plane_value(self, plane):
        if isinstance(plane, list):
            if len(plane) == 0:
                raise ValueError("Plane list is empty.")
            return plane[0]

        return plane

    def _plane_to_uv(self, plane):
        if plane == "xy":
            return [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]

        if plane == "xz":
            return [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]

        if plane == "yz":
            return [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]

        raise ValueError(f"Unknown plane: {plane}")
