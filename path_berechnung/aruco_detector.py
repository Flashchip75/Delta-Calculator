import json

import cv2
import cv2.aruco as aruco
import numpy as np
from numpy.typing import NDArray
from typing import Optional, TypedDict, NotRequired, TypeAlias, Sequence

from config import cfg

class Detection(TypedDict):
    id:        int
    center:    tuple[int, int]
    corners:   NDArray
    timestamp: NotRequired[float]  # only for video

DetectionList: TypeAlias = list[Detection]
class ArucoDetector:

    def __init__(self, dictionaryId: str = "DICT_4X4_100") -> None:
        with open("path_berechnung/arucoFormats.json") as f:
            raw = json.load(f)
    
        DICTIONARIES = {k: getattr(aruco, k) for k in raw}

        if dictionaryId not in DICTIONARIES:
            raise ValueError(f"Unknown dictionary: {dictionaryId}. Choose from {list(DICTIONARIES.keys())}")
        dictionary = aruco.getPredefinedDictionary(DICTIONARIES[dictionaryId])
        self._detector  = aruco.ArucoDetector(dictionary)
        self._visRec       = cfg.cVision.visiualisations["Rectangle"]
        self._visCirc      = cfg.cVision.visiualisations["Circle"]
        self._visText      = cfg.cVision.visiualisations["Text"]

    def process(self, source: str | NDArray) -> tuple[DetectionList, NDArray]:
        """
        Process an image or video file and detect ArUco markers.

        Args:
            source: File path (str) or image array (NDArray).
                    Supports image formats: jpg, jpeg, png, bmp, tiff.
                    Supports video formats: mp4, avi, mov, mkv, wmv, flv, webm, mpeg, mpg.

        Returns:
            detections: List of dicts with keys 'id', 'center', 'corners', and 'timestamp' (video only).
            display:    Annotated image/last frame with markers drawn.

        Raises:
            FileNotFoundError: If the image file cannot be read.
            ValueError: If the video format is unsupported or cannot be opened.
        """

        if isinstance(source, str):
            ext = source.lower().split('.')[-1]
            if ext in ('jpg', 'jpeg', 'png', 'bmp', 'tiff'):
                image = cv2.imread(source)
                if image is None:
                    raise FileNotFoundError(f"Could not read image: {source}")
                return self._processImage(image)
            else:
                cap = self._openVideo(source)
                return self._processVideo(cap)
        else:
            return self._processImage(source)

    def _detect(self, frame: NDArray) -> tuple[Sequence, list[tuple[int, int]], Optional[NDArray], Sequence]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = self._detector.detectMarkers(gray)
        centers: list[tuple[int, int]] = []
        if ids is not None:
            for corner in corners:
                cx = int(corner[0][:, 0].mean())
                cy = int(corner[0][:, 1].mean())
                centers.append((cx, cy))
        return corners, centers, ids, rejected

    def _drawDetections(self, source: NDArray, corners: Sequence, centers: list[tuple[int, int]], ids: Optional[NDArray], rejected: Sequence) -> NDArray:
        display = source.copy()

        colorRecVal         = self._visRec["colorVal"]
        thicknessRecVal     = self._visRec["thicknessVal"]
        colorCircVal        = self._visCirc["colorVal"]
        thicknessCircVal    = self._visCirc["thicknessVal"]
        radiusCircVal       = self._visCirc["radiusVal"]
        colorCircRej        = self._visCirc["colorRej"]
        thicknessCircRej    = self._visCirc["thicknessRej"]
        radiusCircRej       = self._visCirc["radiusRej"]
        fontScaleMarker     = self._visText["fontScaleMarker"]
        colorMarker         = self._visText["colorMarker"]
        lineSizeMarker      = self._visText["lineSizeMarker"]

        if ids is not None:
            for corner, markerId, (cx, cy) in zip(corners, ids.flatten(), centers):
                pts = corner[0].astype(int)

                cv2.polylines(display, [pts],
                              isClosed=True,
                              color=colorRecVal,
                              thickness=thicknessRecVal)
                
                cx = int(corner[0][:, 0].mean())
                cy = int(corner[0][:, 1].mean())

                cv2.circle(display, (cx, cy), radiusCircVal, colorCircVal, -thicknessCircVal)

                textCx = cx + 8
                textCy = cy - 8
                cv2.putText(display, str(markerId), (textCx, textCy),
                            cv2.FONT_HERSHEY_SIMPLEX, fontScaleMarker, colorMarker, lineSizeMarker)
        for r in rejected:
            cx = int(r[0][:, 0].mean())
            cy = int(r[0][:, 1].mean())
            cv2.circle(display, (cx, cy), radiusCircRej, colorCircRej, -thicknessCircRej)
        return display

    def _processImage(self, source: NDArray) -> tuple[DetectionList, NDArray]:
        corners, centers, ids, rejected = self._detect(source)
        display = self._drawDetections(source, corners, centers, ids, rejected)

        detections = []
        if ids is not None:
            for corner, markerId, center in zip(corners, ids.flatten(), centers):
                detections.append({
                    "id": markerId,
                    "center": center,
                    "corners": corner[0]
                })

        detections = sorted(detections, key=lambda d: d["id"])
        return detections, display

    def _openVideo(self, path: str) -> cv2.VideoCapture:
        videoExtensions = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'mpeg', 'mpg'}
        ext = path.lower().split('.')[-1]
        if ext not in videoExtensions:
            raise ValueError(f"Unsupported video format: {ext}")
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {path}")
        return cap

    def _processVideo(self, source: cv2.VideoCapture) -> tuple[DetectionList, NDArray]:
        allDetections = []
        display = np.zeros((1, 1, 3), dtype=np.uint8)
        while True:
            ret, frame = source.read()
            if not ret:
                break
            timestamp = source.get(cv2.CAP_PROP_POS_MSEC)
            detections, display = self._processImage(frame)
            for d in detections:
                d["timestamp"] = timestamp
            allDetections.extend(detections)
        source.release()
        return allDetections, display

    def displayResults(self, display: NDArray) -> None:
        """
        Display the annotated image in a window until a key is pressed.

        Args:
            display: Annotated image array from process().

        Raises:
            ValueError: If display is None or empty.
        """
        if display is not None and display.size > 0:
            cv2.imshow("Aruco Detections", display)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            raise ValueError("No display image to show.")
        
    def calibrate(self, source: str | NDArray, normM: int, calibId: int) -> float:
        """
        Calculate a px-to-m scale factor using two ArUco markers of the same ID.

        Args:
            source:   Image path or NDArray.
            normM:  Known real-world distance in m between the two markers.
            calibId: ArUco marker ID to search for (expects exactly 2 matches).

        Returns:
            Scale factor in m/px.

        Raises:
            ValueError: If not exactly 2 markers with calibId are found.
        """
        detections, _ = self.process(source)

        points = [d["center"] for d in detections if d["id"] == calibId]

        if len(points) != 2:
            raise ValueError(f"Expected 2 markers with ID {calibId}, found {len(points)}.")

        (x1, y1), (x2, y2) = points
        distPX = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        mPerPx = normM / distPX

        return mPerPx
    
    def pxToM(self, px: float, mPerPx: float) -> float:
        """
        Convert a distance from pixels to millimeters using the scale factor.

        Args:
            px: Distance in pixels.
            mPerPx: Scale factor in m/px.
        Returns:
            Distance in millimeters.
        Raises:
            ValueError: If mPerPx is invalid or if px is negative or zero.
        """
        if mPerPx <= 0:
            raise ValueError("Scale factor mPerPx must be greater than zero.")
        if mPerPx == float('inf'):
            raise ValueError("Scale factor mPerPx is unreasonably large.")
        if px < 0:
            raise ValueError("Pixel distance cannot be negative.")
        if px == 0:
            raise ValueError("Pixel distance cannot be zero.")

        return px * mPerPx
    
    def centerPxToM(self, center: tuple[int, int], mPerPx: float) -> tuple[float, float]:
        """
        Convert a center point from pixels to millimeters.

        Args:
            center: Tuple of (x, y) in pixels.
            mPerPx: Scale factor in m/px.
        Returns:
            Tuple of (x, y) in millimeters.
        Raises:
            ValueError: If center is None, has negative coordinates, or if mPerPx is invalid.
        """
        if center is None:
            raise ValueError("Center point cannot be None.")
        if center[0] < 0 or center[1] < 0:
            raise ValueError("Center coordinates must be non-negative.")
        if center[0] == 0 and center[1] == 0:
            raise ValueError("Center coordinates cannot both be zero.")
        if mPerPx <= 0:
            raise ValueError("Scale factor mPerPx must be greater than zero.")
        
        xM = self.pxToM(center[0], mPerPx)
        yM = self.pxToM(center[1], mPerPx)
        return xM, yM
    
    def getPointsM(self, detections: DetectionList, mPerPx: float, *ids: int) -> list[list[int]]:
        """
        Extract center points in m for given marker IDs in order.

        Args:
            detections: Output from process().
            mPerPx:    Scale factor from calibrate().
            *ids:       Marker IDs in the order you want the points.

        Returns:
            List of [x, y, 0] points in m, one per ID.

        Raises:
            ValueError: If a requested ID is not found in detections.
        """
        lookup = {d["id"]: d["center"] for d in detections}
        points = []
        for markerId in ids:
            if markerId not in lookup:
                raise ValueError(f"Marker ID {markerId} not found in detections.")
            x, y = self.centerPxToM(lookup[markerId], mPerPx)
            points.append([x, y, 0])
        return points