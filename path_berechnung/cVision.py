from config import cfg
from pathlib import Path

from .aruco_detector import ArucoDetector
from .yolo_detector import YoloDetector

def detect_points(
        source: str
    ) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        """Detect two points from an image source using ArUco or YOLO.

        The function first tries to detect ArUco markers in the given source.
        If fewer than two markers are found, it falls back to YOLO-based object
        detection. Detected pixel coordinates are converted to millimeters using
        either a fresh calibration image or a configured conversion factor.

        Args:
            source: Path or source string passed to the detector for processing.

        Returns:
            A tuple ``(p1, p2)`` containing two detected 3D points in
            millimeters. Each point is returned as ``(x, y, z)`` with ``z``
            set to ``0``.

        Raises:
            ValueError: If required calibration-related configuration values are
                invalid, if no ArUco dictionary is configured, or if the stored
                ``mToPixel`` value is not greater than zero when recalibration
                is disabled.
            FileNotFoundError: If recalibration is enabled and the configured
                calibration image does not exist.
            RuntimeError: If fewer than two valid points are detected by both
                ArUco and YOLO.
        """
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
            if p.calibration_norm_m <= 0:
                raise ValueError(
                    f"Ungültiger calibration_norm_m: {p.calibration_norm_m}. Muss > 0 sein."
                )
            if p.calibration_id < 0:
                raise ValueError(
                    f"Ungültige calibration_id: {p.calibration_id}. Muss ≥ 0 sein."
                )

            print(f"  Kalibrierung mit Marker ID {p.calibration_id} ({p.calibration_norm_m}m)...")
            pxToM = ad.calibrate(p.calibration_source, p.calibration_norm_m, p.calibration_id)
            print(f"  Kalibrierung erfolgreich: {pxToM:.4f} px/m")

        else:
            if p.mToPixel <= 0:
                raise ValueError(
                    f"Ungültiger mToPixel-Wert: {p.mToPixel}. Muss > 0 sein "
                    f"oder reCalibration auf true setzen."
                )
            pxToM = p.mToPixel
            print(f"  Verwende gespeicherten Wert: {pxToM:.4f} px/m")

        # Aruco detection

        detections, _ = ad.process(source)
        if len(detections) >= 2:
            print(f"  ArUco: {len(detections)} Marker gefunden.")
            pts = [ad.centerPxToM(d['center'], pxToM) for d in detections[:2]]
            p1 = (*pts[0], 0)
            p2 = (*pts[1], 0)
            return p1, p2

        print(f"  ArUco: nur {len(detections)} Marker — versuche YOLO.")

        # YOLO fallback
        yd = YoloDetector()
        detections, _ = yd.process(source)
        valid = [d for d in detections if d['confidence'] >= 0.5]
        if len(valid) >= 2:
            print(f"  YOLO: {len(valid)} Objekte gefunden (confidence >= 0.5).")
            pts = [ad.centerPxToM(d['center'], pxToM) for d in valid[:2]]
            p1 = (*pts[0], 0)
            p2 = (*pts[1], 0)
            return p1, p2

        raise RuntimeError(
            f"Keine zwei Punkte erkannt. "
            f"ArUco: {len(detections)}, YOLO (>=0.5): {len(valid)}"
        )