import dataclasses
from dataclasses import dataclass
from math import pi

def string_to_field(str) -> str:
    return str.replace("/", "_").replace("^2", "2").replace("^3", "3").replace("^4", "4")

def field_to_string(str) -> str:
    return str.replace("_", "/").replace("2", "^2").replace("3", "^3").replace("4", "^4")

def get_unit_type(unitString: str) -> dataclass:
    allUnits = IUnit.__subclasses__()
    for unit in allUnits:
        try:
            getattr(unit, string_to_field(unitString))
            return unit
        except AttributeError:
            pass

class IUnit:
    def getValue(self, key: str) -> float:
        return getattr(self, string_to_field(key))

    def getIndex(self, key: str) -> int:
        d = dataclasses.asdict(self)
        key = string_to_field(key)
        idx = -1
        for i, k in enumerate(d):
            if k == key:
                idx = i
                break
        return idx

    def getLists(self) -> tuple:
        d = dataclasses.asdict(self)
        return [field_to_string(k) for k in d.keys()], list(d.values())


@dataclass(frozen=True)
class Unitless(IUnit):
    _: float = 1

    def getDefault(self) -> str: return "_"


@dataclass(frozen=True)
class UnitAngle(IUnit):
    rad: float = 1.0
    deg: float = pi/180
    deg: float = pi/180

    def getDefault(self) -> str: return "rad"


@dataclass(frozen=True)
class UnitTime(IUnit):
    h: float = 3600.0
    min: float = 60.0
    s: float = 1.0
    ms: float = 0.001

    def getDefault(self) -> str: return "s"


@dataclass(frozen=True)
class UnitLength(IUnit):
    m: float = 1.0
    dm: float = 0.1
    cm: float = 0.01
    mm: float = 0.001
    um: float = 0.000001

    def getDefault(self) -> str: return "mm"


@dataclass(frozen=True)
class UnitVelocity(IUnit):
    m_s: float = 1.0
    km_h: float = 1 / 3.6

    def getDefault(self) -> str: return "m_s"


@dataclass(frozen=True)
class UnitAcceleration(IUnit):
    m_s2: float = 1.0

    def getDefault(self) -> str: return "m_s2"


@dataclass(frozen=True)
class UnitJerk(IUnit):
    m_s3: float = 1.0

    def getDefault(self) -> str: return "m_s3"