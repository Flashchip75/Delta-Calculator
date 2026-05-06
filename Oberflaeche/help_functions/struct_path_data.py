# Struct zum Speichern der Patheingaben

# Stefan Fragen was wie übergeben wird


from dataclasses import dataclass
from typing import List


@dataclass
class PathPoint:
    x: float
    y: float
    z: float


@dataclass
class PathStruct:
    trajectory: List[PathPoint]


import json
from typing import List


def write_path_struct(json_path: str) -> PathStruct:
    """
    Liest die JSON-Datei ein und wandelt sie in ein PathStruct um.

    Übergangslösung: nutzt dieselbe testfahrt.json wie KinStruct,
    extrahiert aber nur Positionen.
    """

    with open(json_path, "r") as f:
        data = json.load(f)

    trajectory: List[PathPoint] = []

    for point in data:
        pp = PathPoint(
            x=point["x"],
            y=point["y"],
            z=point["z"]
        )

        trajectory.append(pp)

    return PathStruct(trajectory=trajectory)