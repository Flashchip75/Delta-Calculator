from dataclasses import dataclass, field
from typing import Tuple, List, Dict
import math

# =====================================================
# Listing Function
# =====================================================

def get_path_models():
    return (Line, Bezier, Arc, Wait), (Polynomial5, Polynomial7, ConstantVelocity)

# =====================================================
# Geometries
# =====================================================

@dataclass
class Debug: # For UI Debugging only, do not include in get_path_models()
    ff1: float = 0.0

    ft1: Tuple[float] = (1.0,)
    ft2: Tuple[float,float] = (2.0, 3.0)
    ft3: Tuple[float,float,float] = (4.0, 5.0, 6.0)
    ft4: Tuple[float,float,float,float] = (7.0, 8.0, 9.0, 10.0)

    fu1: Tuple[float,str] = (42.0,"deg")
    fu2: Tuple[float,float,str] = (67.0, 69.0, "um")
    fu3: Tuple[float,float,float,str] = (-273.15, 299792458.0, 6.022E23, "km/h")
    fu4: Tuple[float,float,float,float,str] = (0.0, -0.0, 0.0, -0.0, "m/s^2")

    ii: int = 90
    iu: Tuple[int, str] = (180, "deg")

    dl: List[str] = field(default_factory=lambda: ["X", "Y", "Z"])
    dd: Dict[str, int] = field(default_factory=lambda: {"A": 1, "B": 2, "C": 3})

    cb: bool = False
    st: str = "Hello World"

    time_law_ref: int = 0


@dataclass
class Line:
    start: Tuple[float, float, float, str] = (0.0, 0.0, 0.0, "mm")
    end: Tuple[float, float, float, str] = (0.0, 0.0, 0.0, "mm")

    time_law_ref: int = 0


@dataclass
class Bezier:
    p0: Tuple[float, float, float, str] = (0.0, 0.0, 0.0, "mm")
    p1: Tuple[float, float, float, str] = (0.0, 0.0, 0.0, "mm")
    p2: Tuple[float, float, float, str] = (0.0, 0.0, 0.0, "mm")
    p3: Tuple[float, float, float, str] = (0.0, 0.0, 0.0, "mm")

    time_law_ref: int = 0


@dataclass
class Arc:
    center: Tuple[float, float, float, str] = (0.0, 0.0, 0.0, "mm")
    radius: Tuple[float, str] = (0.0, "mm")

    plane: List[str] = field(default_factory=lambda: ["xy", "xz", "yz"])

    start_angle: Tuple[float, str] = (0.0, "deg")
    end_angle: Tuple[float, str] = (0.0, "deg")

    time_law_ref: int = 0


@dataclass
class Wait:
    duration: Tuple[float, str] = (1.0, "s")

    time_law_ref: float = math.nan


# =====================================================
# Time Laws
# =====================================================

@dataclass
class Polynomial5:
    duration: Tuple[float, str] = (1.0, "s")

    start_acceleration: Tuple[float, str] = (0.0, "m/s^2")

    end_velocity: Tuple[float, str] = (0.0, "m/s")
    end_acceleration: Tuple[float, str] = (0.0, "m/s^2")


@dataclass
class Polynomial7:
    duration: Tuple[float, str] = (1.0, "s")

    start_acceleration: Tuple[float, str] = (0.0, "m/s^2")
    start_jerk: Tuple[float, str] = (0.0, "m/s^3")

    end_velocity: Tuple[float, str] = (0.0, "m/s")
    end_acceleration: Tuple[float, str] = (0.0, "m/s^2")
    end_jerk: Tuple[float, str] = (0.0, "m/s^3")


@dataclass
class ConstantVelocity:
    pass