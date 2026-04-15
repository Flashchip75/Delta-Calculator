from config import cfg
from pathlib import Path

from .aruco_detector import ArucoDetector
from .yolo_detector import YoloDetector

def detect_points(
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