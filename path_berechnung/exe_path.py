from __future__ import annotations
import numpy as np

from config import cfg
from .track import Trajectory
from .physics import PhysicsEngine
from .PathFrenet import PathFrenet
from .PathKinematics import PathKinematics
from path_berechnung import cVision


class exePath:
    def run(
        self,
        geometry: list[dict] | None = None,
        p1: tuple[float, float, float] | None = None,
        p2: tuple[float, float, float] | None = None,
        source: str | None = None,
    ) -> dict[str, np.ndarray]:
        """
        Priority:
          1. geometry given directly            -> use raw j_data list as-is
          2. p1 & p2 given directly             -> use as-is
          3. source given                       -> try ArUco, fallback to YOLO
          4. none                               -> raise ValueError
        """

        path = cfg.path

        # 1. Geometrie
        print("=== Definiere Pfad-Geometrie ===")

        if geometry is not None:
            print("=== Geometrie (direkt übergeben) ===")
            j_data = geometry
        elif p1 is not None and p2 is not None:
            print("=== Geometrie (direkte Punkte) ===")
            j_data = [{"type": "Line", "pts": [list(p1), list(p2)]}]
        elif source is not None:
            print(f"=== Geometrie (Vision: {source}) ===")
            p1, p2 = cVision.detect_points(source)
            print(f"  Erkannt: p1={p1}, p2={p2}")
            j_data = [{"type": "Line", "pts": [list(p1), list(p2)]}]
        else:
            raise ValueError("Entweder geometry, p1/p2 oder source muss angegeben werden.")

        # 2. Trajektorie
        print("=== Berechne Trajektorie ===")
        pts = Trajectory(j_data).cloud
        frenet= PathFrenet(pts)
        kin = PathKinematics(pts, T=path.duration_s)

        # 3. Forces
        print("=== Berechne Kraefte ===")
        data = PhysicsEngine.compute(pts, frenet, kin)
        
        return data