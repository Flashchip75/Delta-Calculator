import dataclasses
from dataclasses import dataclass
from math import pi


class IUnit:
    def getValue(self, key: str) -> float:
        return getattr(self, key.replace("/", "_"))

    def getIndex(self, key: str) -> int:
        d = dataclasses.asdict(self)
        idx = -1
        for i, k in enumerate(d):
            if k == key:
                idx = i
                break
        return idx

    def getLists(self) -> tuple:
        d = dataclasses.asdict(self)
        return [k.replace("_", "/") for k in d.keys()], list(d.values())


@dataclass(frozen=True)
class Unitless(IUnit):
    _: float = 1

    def getDefault(self) -> str: return "_"


@dataclass(frozen=True)
class UnitAngle(IUnit):
    rad: float = 1
    deg: float = pi/180

    def getDefault(self) -> str: return "rad"


@dataclass(frozen=True)
class UnitTime(IUnit):
    h: float = 3600
    min: float = 60
    s: float = 1
    ms: float = 0.001

    def getDefault(self) -> str: return "s"


@dataclass(frozen=True)
class UnitLength(IUnit):
    m: float = 1
    dm: float = 0.1
    cm: float = 0.01
    mm: float = 0.001
    um: float = 0.000001

    def getDefault(self) -> str: return "mm"


@dataclass(frozen=True)
class UnitVelocity(IUnit):
    m_s: float = 1
    km_h: float = 1 / 3.6

    def getDefault(self) -> str: return "m_s"
