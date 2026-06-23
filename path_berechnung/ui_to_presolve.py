import math


def _vector_without_unit(vector):
    return [vector[0], vector[1], vector[2]]


def _value_without_unit(value):
    return value[0]


def _angle_to_rad(angle):
    value = angle[0]
    unit = angle[1]

    if unit == "deg":
        return math.radians(value)

    if unit == "rad":
        return value

    raise ValueError(f"Unsupported angle unit: {unit}")


def _plane_to_uv(plane):
    if plane == "xy":
        return [1, 0, 0], [0, 1, 0]

    if plane == "xz":
        return [1, 0, 0], [0, 0, 1]

    if plane == "yz":
        return [0, 1, 0], [0, 0, 1]

    raise ValueError(f"Unsupported plane: {plane}")


def curve_to_presolve_config(curve):
    curve_type = curve.__class__.__name__

    if curve_type == "Line":
        return {
            "type": "Line",
            "pts": [
                _vector_without_unit(curve.start),
                _vector_without_unit(curve.end)
            ]
        }

    if curve_type == "Bezier":
        return {
            "type": "Bezier",
            "pts": [
                _vector_without_unit(curve.p0),
                _vector_without_unit(curve.p1),
                _vector_without_unit(curve.p2),
                _vector_without_unit(curve.p3)
            ]
        }

    if curve_type == "Arc":
        u, v = _plane_to_uv(curve.plane)

        return {
            "type": "Arc",
            "c": _vector_without_unit(curve.center),
            "r": _value_without_unit(curve.radius),
            "u": u,
            "v": v,
            "a": [
                _angle_to_rad(curve.start_angle),
                _angle_to_rad(curve.end_angle)
            ]
        }

    if curve_type == "Wait":
        return {
            "type": "Wait",
            "approx_length": 0.0,
            "N": 1
        }

    raise TypeError(f"Unsupported curve type: {curve_type}")


def curves_to_presolve_config(curves):
    return [
        curve_to_presolve_config(curve)
        for curve in curves
    ]