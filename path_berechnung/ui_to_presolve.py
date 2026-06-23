import math


def plane_to_uv(plane: str):
    """
    Converts the selected plane into the two unit vectors u and v
    required by the presolver for Arc curves.
    """
    if plane == "xy":
        return [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]

    if plane == "xz":
        return [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]

    if plane == "yz":
        return [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]

    raise ValueError(f"Unknown plane: {plane}")


def get_duration_from_time_law(curve, time_laws):
    """
    Gets the duration T from the time law referenced by the curve.
    If no valid duration exists, None is returned.
    """
    ref = getattr(curve, "time_law_ref", None)

    # Wait uses NaN as time_law_ref
    if ref is None:
        return None

    if isinstance(ref, float) and math.isnan(ref):
        return None

    if not isinstance(ref, int):
        return None

    if ref < 0 or ref >= len(time_laws):
        return None

    time_law = time_laws[ref]

    if hasattr(time_law, "duration"):
        return time_law.duration

    return None


def curve_to_presolve_config(curve, time_laws=None):
    """
    Converts one UI curve dataclass into the dictionary format
    required by PreCurve/Presolver.
    """
    curve_type = curve.__class__.__name__

    if time_laws is None:
        time_laws = []

    T = get_duration_from_time_law(curve, time_laws)

    if curve_type == "Line":
        cfg = {
            "type": "Line",
            "pts": [
                list(curve.start),
                list(curve.end)
            ]
        }

        if T is not None:
            cfg["T"] = T

        return cfg

    if curve_type == "Bezier":
        cfg = {
            "type": "Bezier",
            "pts": [
                list(curve.p0),
                list(curve.p1),
                list(curve.p2),
                list(curve.p3)
            ]
        }

        if T is not None:
            cfg["T"] = T

        return cfg

    if curve_type == "Arc":
        u, v = plane_to_uv(curve.plane)

        cfg = {
            "type": "Arc",
            "c": list(curve.center),
            "r": curve.radius,
            "u": u,
            "v": v,
            "a": [
                curve.start_angle,
                curve.end_angle
            ]
        }

        if T is not None:
            cfg["T"] = T

        return cfg

    if curve_type == "Wait":
        return {
            "type": "Wait",
            "T": curve.duration,
            "approx_length": 0.0,
            "N": 1
        }

    raise TypeError(f"Unsupported curve type: {curve_type}")


def path_to_presolve_config(path, time_laws=None, include_wait=False):
    """
    Converts a complete UI path into a list of presolver configurations.

    If include_wait is False, Wait elements are ignored because the current
    Presolver cannot calculate a curve length for Wait.
    """
    if time_laws is None:
        time_laws = []

    configs = []

    for curve in path:
        curve_type = curve.__class__.__name__

        if curve_type == "Wait" and not include_wait:
            continue

        configs.append(curve_to_presolve_config(curve, time_laws))

    return configs


def single_curve_to_presolve_config(curve, time_laws=None):
    """
    Converts a single curve for presolve usage.
    Useful if the UI calls the presolver for only one curve at a time.
    """
    return curve_to_presolve_config(curve, time_laws)
