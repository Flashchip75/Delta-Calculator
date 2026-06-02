from dataclasses import dataclass, field
from typing import Tuple, List
import math


# =====================================================
# Geometries
# =====================================================

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
    duration: Tuple[float, str] = (0.0, "s")

    time_law_ref: float = math.nan


# =====================================================
# Time Laws
# =====================================================

@dataclass
class Polynomial5:
    duration: Tuple[float, str] = (1.0, "s")

    start_acceleration: Tuple[float, str] = (0.0, "1/s^2")

    end_velocity: Tuple[float, str] = (0.0, "1/s")
    end_acceleration: Tuple[float, str] = (0.0, "1/s^2")


@dataclass
class Polynomial7:
    duration: Tuple[float, str] = (1.0, "s")

    start_acceleration: Tuple[float, str] = (0.0, "1/s^2")
    start_jerk: Tuple[float, str] = (0.0, "1/s^3")

    end_velocity: Tuple[float, str] = (0.0, "1/s")
    end_acceleration: Tuple[float, str] = (0.0, "1/s^2")
    end_jerk: Tuple[float, str] = (0.0, "1/s^3")


@dataclass
class ConstantVelocity:
    pass