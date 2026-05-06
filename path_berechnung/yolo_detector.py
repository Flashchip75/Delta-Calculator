import cv2
from ultralytics import YOLO
from numpy.typing import NDArray
from typing import Optional, TypeAlias, Sequence, cast

from config import cfg

Detection: TypeAlias = dict[str, int | float | tuple[int, int] | tuple[int, int, int, int] | NDArray]
DetectionList: TypeAlias = list[Detection]

class YoloDetector:
    def __init__(self) -> None:
        self._model     = YOLO(cfg.cVision.model_path)
        self._vis       = cfg.cVision.visiualisations
        self._outDir    = cfg.global_cfg.output_dir

    def process(self, source: str | NDArray) -> tuple[DetectionList, NDArray]:
        """
        Process an image file and detect objects using YOLO.

        Args:
            source: File path (str) or image array (NDArray).
                    Supports image formats: jpg, jpeg, png, bmp, tiff.

        Returns:
            A tuple containing the list of detections and the annotated image array.
        """
        if isinstance(source, str):
            image = cv2.imread(source)
            if image is None:
                raise FileNotFoundError(f"Could not read image: {source}")
        else:
            image = source

        detections = self._detect(source)
        display = self._drawDetections(image, detections)
        return detections, display

    def _detect(self, source: str | NDArray) -> DetectionList:
        results = self._model(source)
        detections: DetectionList = []
        for result in results:
            for box in result.boxes:
                x, y, w, h = box.xywh[0].tolist()
                detections.append({
                    "center": (int(x), int(y)),
                    "box": (int(x), int(y), int(w), int(h)),
                    "confidence": float(box.conf[0]),
                    "classId": int(box.cls[0])
                })
        return detections

    def _drawDetections(self, source: NDArray, detections: DetectionList) -> NDArray:
        display = source.copy()

        colorRec        = self._vis["colorRec"]
        thicknessRec    = self._vis["thicknessRec"]
        colorCirc       = self._vis["colorCirc"]
        thicknessCirc   = self._vis["thicknessCirc"]
        radiusCirc      = self._vis["radiusCirc"]
        
        for d in detections:
            x, y, w, h = cast(tuple[int, int, int, int], d["box"])
            cx, cy = cast(tuple[int, int], d["center"])
            cv2.rectangle(display,
                        (x - w // 2, y - h // 2),
                        (x + w // 2, y + h // 2),
                        colorRec, thicknessRec)
            cv2.circle(display, (cx, cy), radiusCirc, colorCirc, thicknessCirc)
        return display
    
    def displayResults(self, display: NDArray) -> None:
        """
        Display the annotated image in a window until a key is pressed.

        Args:
            display: Annotated image array from draw_detections().

        Raises:
            ValueError: If display is None or empty.
        """
        if display is None or display.size == 0:
            raise ValueError("No display image to show.")
        cv2.imshow("YOLO Detections", display)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def saveResults(self, display: NDArray, fname: str) -> None:
        """
        Save the annotated image to disk.

        Args:
            display: Annotated image array from process().
            fname: Name of the file to save (e.g. "result.jpg").

        Raises:
            ValueError: If display is None or empty.
            OSError: If the image could not be written to the given path.
        """
        path = f"{self._outDir}/{fname}"
        if display is None or display.size == 0:
            raise ValueError("No display image to save.")
        if not cv2.imwrite(path, display):
            raise OSError(f"Could not write image to: {path}")