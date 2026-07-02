from dataclasses import dataclass
from typing import List


@dataclass
class KinPoint:
    # Zeit
    t: float

    # Position
    x: float
    y: float
    z: float

    # Geschwindigkeit
    vx: float
    vy: float
    vz: float

    # Beschleunigung
    ax: float
    ay: float
    az: float

    # Ruck (Jerk)
    jx: float
    jy: float
    jz: float

    # Erreichbarkeit
    reachable: bool


@dataclass
class KinStruct:
    trajectory: List[KinPoint]


import json
from typing import List


def write_kin_struct(json_path: str) -> KinStruct:
    """
    Liest die JSON-Datei ein und wandelt sie in ein KinStruct um.

    Wird später ersetzt durch echte Kinematik-Berechnung,
    dient aktuell zum Testen der Pipeline.
    """

    with open(json_path, "r") as f:
        data = json.load(f)

    trajectory: List[KinPoint] = []

    for point in data:
        kp = KinPoint(
            t=point["t"],

            x=point["x"],
            y=point["y"],
            z=point["z"],

            vx=point["vx"],
            vy=point["vy"],
            vz=point["vz"],

            ax=point["ax"],
            ay=point["ay"],
            az=point["az"],

            jx=point["jx"],
            jy=point["jy"],
            jz=point["jz"],

            reachable=point["reachable"]
        )

        trajectory.append(kp)

    return KinStruct(trajectory=trajectory)