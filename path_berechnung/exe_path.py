from __future__ import annotations
import numpy as np

from config import cfg
from pathlib import Path
from .track import Trajectory
from .physics import PhysicsEngine
from .PathFrenet import PathFrenet
from .PathKinematics import PathKinematics
from .ProfileManager import ProfileManager


class exePath:
    def run(
        self,
        geometry: str | None = None,
        p1: tuple[float, float, float] | None = None,
        p2: tuple[float, float, float] | None = None,
        source: str | None = None,
        gcode: str | None = None,
    ) -> dict[str, np.ndarray]:
        """
        Priority:
          1. geometry given directly            -> load from JSON via ProfileManager
          2. p1 & p2 given directly             -> use as-is
          3. source given                       -> try ArUco, fallback to YOLO
          4. gcode given                         -> parse GCode file for path
          5. none                               -> raise ValueError
        """

        path = cfg.path
        g = cfg.global_cfg

        # 1. Geometrie
        print("=== Definiere Pfad-Geometrie ===")

        if geometry is not None:
            print("=== Geometrie (direkt übergeben) ===")
            filepath = path.path_profiles
            if filepath is None:
                raise ValueError("Kein Pfad für path_profiles in config.json angegeben.")
            print(f"  Lade Profil '{geometry}' aus '{filepath}'")
            manager = ProfileManager(filepath=filepath)
            j_data = manager.get_profile(geometry)
        elif p1 is not None and p2 is not None:
            print("=== Geometrie (direkte Punkte) ===")
            j_data = [{"type": "Line", "pts": [list(p1), list(p2)]}]
        elif source is not None:
            ext = Path(source).suffix.lower()
            if ext in ['.png', '.jpg', '.jpeg']:
                print(f"=== Geometrie (Vision: {source}) ===")
                from path_berechnung import cVision
                p1, p2 = cVision.detect_points(source)
                print(f"  Erkannt: p1={p1}, p2={p2}")
                j_data = [{"type": "Line", "pts": [list(p1), list(p2)]}]
            else:
                raise ValueError(f"Unbekannte Dateiendung '{ext}' für Vision-Quelle.")
        elif gcode is not None:
            ext = Path(gcode).suffix.lower()
            if ext in ['.gcode', '.gc', '.g']:
                print(f"=== Geometrie (GCode: {gcode}) ===")
                from .gcode_reader import read_gcode
                j_data = read_gcode(gcode)
                print(f"  GCode '{gcode}' mit {len(j_data)} Segmenten geladen.")
            else:
                raise ValueError(f"Unbekannte Dateiendung '{ext}' für GCode-Datei.")
        else:
            raise ValueError("Entweder geometry, p1/p2, source oder gcode muss angegeben werden.")

        # 2. Trajektorie
        print("=== Berechne Trajektorie ===")
        pts = Trajectory(j_data).cloud
        frenet= PathFrenet(pts)
        kin = PathKinematics(pts, T=path.duration_s)

        # 3. Forces
        print("=== Berechne Kraefte ===")
        data = PhysicsEngine.compute(pts, frenet, kin)

        # 4. Export
        print("=== Exportiere Daten ===")
        csvPath = Path(__file__).parent.parent / g.output_dir / g.trajectory_csv
        PhysicsEngine.export_to_csv(data, csvPath)
        
        return data