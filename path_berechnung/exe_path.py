from __future__ import annotations
import numpy as np
from pathlib import Path

from config import cfg
from .geometry import Bezier, Line
from .physics import PhysicsEngine, FrenetForceCalculator
from .trajectory import Trajectory
from .visualization import Visualizer
from path_berechnung import cVision


class exePath:
    def run(
        self,
        p1: tuple[float, float, float] | None = None,
        p2: tuple[float, float, float] | None = None,
        source: str | None = None,
    ) -> dict:
        """
        Priority:
          1. p1 & p2 given directly           -> use as-is
          2. source given                     -> try ArUco, fallback to YOLO
          3. neither                          -> raise ValueError
        """

        # 1. Geometrie
        print("=== Definiere Pfad-Geometrie ===")

        if p1 is not None and p2 is not None:
            print("=== Definiere Pfad-Geometrie (direkte Eingabe) ===")
        elif source is not None:
            print(f"=== Definiere Pfad-Geometrie (Vision: {source}) ===")
            p1, p2 = cVision.detect_points(source)
        else:
            raise ValueError("Entweder p1/p2 oder source muss angegeben werden.")

        # 2. Trajektorie
        c = Line(p1, p2)
        p = cfg.path
        traj = Trajectory(
            [c],
            dur_s   = p.duration_s,
            pts     = p.points,
            gain    = p.gain,
            blend   = p.blend,
            scale_m = p.scale_m,
            offset_mm = p.offset_mm,
        )

        # 3. Physik & Export
        print("=== Berechne Trajektorie & Kräfte ===")
        g = cfg.global_cfg

        phys  = PhysicsEngine()
        force = FrenetForceCalculator(m_kg=g.mass_kg, gravity=g.gravity)

        P, T = traj.export(g.trajectory_csv, g.output_dir, phys, force)
        d    = traj.toDictVar(phys, force)

        
        # 4. Visualisierung
        print("\n=== Visualisiere Ergebnisse ===")
        viz = Visualizer()
        viz.plot_matlab_style(P, T, g.output_dir)
        viz.plot_forces(g.trajectory_csv, g.output_dir)

        return d