from __future__ import annotations
import numpy as np
from pathlib import Path

from config import cfg
from .geometry import Bezier, Line
from .physics import PhysicsEngine, FrenetForceCalculator
from .trajectory import Trajectory
from .visualization import Visualizer
from .aruco_detector import ArucoDetector
from .yolo_detector import YoloDetector


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
            p1, p2 = self._detect_points(source)
        else:
            raise ValueError("Entweder p1/p2 oder source muss angegeben werden.")

        # 2. Trajektorie
        print(f"  p1={p1}, p2={p2}")
        c = Line(p1,p2)
        p = cfg.path
        traj = Trajectory(
            [c],
            dur_s   = p.duration_s,
            pts     = p.points,
            gain    = p.gain,
            blend   = p.blend,
            scale_m = p.scale_m,
        )

        # 3. Physik & Export
        print("=== Berechne Trajektorie & Kräfte ===")
        g = cfg.global_cfg

        phys  = PhysicsEngine()
        force = FrenetForceCalculator(m_kg=g.mass_kg, gravity=g.gravity)

        P, T = traj.export(g.trajectory_csv, g.output_dir,phys,force)
        d    = traj.toDictVar(phys, force)

        
        # 4. Visualisierung
        print("\n=== Visualisiere Ergebnisse ===")
        viz = Visualizer()
        viz.plot_matlab_style(P, T, g.output_dir)
        viz.plot_forces(g.trajectory_csv, g.output_dir)

        return d
    
    def _detect_points(
        self, source: str
    ) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        """Try ArUco first, fall back to YOLO. Returns (p1, p2) in mm."""

        p = cfg.cVision

        if p.aruco_dict is not None:
            print(f"  Verwende ArUco-Dict: {p.aruco_dict}")
            ad = ArucoDetector(p.aruco_dict)
        else:
            raise ValueError("Kein ArUco-Dict angegeben. Bitte aruco_dict in config.json setzen.")

        if p.reCalibration:
            # --- Recalibration path: validate all calibration inputs first ---
            if not Path(p.calibration_source).is_file():
                raise FileNotFoundError(
                    f"Kalibrierungsbild nicht gefunden: {p.calibration_source}"
                )
            if p.calibration_norm_mm <= 0:
                raise ValueError(
                    f"Ungültiger calibration_norm_mm: {p.calibration_norm_mm}. Muss > 0 sein."
                )
            if p.calibration_id < 0:
                raise ValueError(
                    f"Ungültige calibration_id: {p.calibration_id}. Muss ≥ 0 sein."
                )

            print(f"  Kalibrierung mit Marker ID {p.calibration_id} ({p.calibration_norm_mm}mm)...")
            pxToMM = ad.calibrate(p.calibration_source, p.calibration_norm_mm, p.calibration_id)
            print(f"  Kalibrierung erfolgreich: {pxToMM:.4f} px/mm")

        else:
            if p.mmToPixel <= 0:
                raise ValueError(
                    f"Ungültiger mmToPixel-Wert: {p.mmToPixel}. Muss > 0 sein "
                    f"oder reCalibration auf true setzen."
                )
            pxToMM = p.mmToPixel
            print(f"  Verwende gespeicherten Wert: {pxToMM:.4f} px/mm")

        # Aruco detection
        ad = ArucoDetector()
        detections, _ = ad.process(source)
        if len(detections) >= 2:
            print(f"  ArUco: {len(detections)} Marker gefunden.")
            pts = [ad.centerPxToMM(d['center'], pxToMM) for d in detections[:2]]
            p1 = (*pts[0], 0)
            p2 = (*pts[1], 0)
            return p1, p2

        print(f"  ArUco: nur {len(detections)} Marker — versuche YOLO.")

        # YOLO fallback
        yd = YoloDetector()
        detections, _ = yd.process(source)
        valid = [d for d in detections if d['confidence'] >= 0.5]
        if len(valid) >= 2:
            print(f"  YOLO: {len(valid)} Objekte gefunden (confidence ≥ 0.5).")
            pts = [ad.centerPxToMM(d['center'], pxToMM) for d in valid[:2]]
            p1 = (*pts[0], 0)
            p2 = (*pts[1], 0)
            return p1, p2

        raise RuntimeError(
            f"Keine zwei Punkte erkannt. "
            f"ArUco: {len(detections)}, YOLO (≥0.5): {len(valid)}"
        )