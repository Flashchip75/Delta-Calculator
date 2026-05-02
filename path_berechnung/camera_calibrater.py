import cv2
import numpy as np
from pathlib import Path
from numpy.typing import NDArray
from typing import Optional

class CameraCalibrator:

    def __init__(self, boardSize: tuple[int, int] = (9, 6)) -> None:
        self.boardSize = boardSize
        self.cameraMatrix: Optional[NDArray] = None
        self.distCoeffs: Optional[NDArray] = None


    def calibrateProcess(self, source: str) -> None:
        """
        Calibrate the camera from a video file or a folder of images.

        Args:
            source: Path to a video file or a folder containing images.

        Raises:
            ValueError: If no valid calibration frames are found.
        """
        path = Path(source)
        ext = path.suffix.lower().lstrip('.')

        if path.is_dir():
            self._calibrateFromImages(path)
        elif ext in ('avi', 'mp4', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'mpeg', 'mpg'):
            self._calibrateFromVideo(path)
        elif ext in ('jpg', 'jpeg', 'png', 'bmp', 'tiff'):
            raise ValueError("Single images are not supported. Provide a folder of images or a video.")
        else:
            raise ValueError(f"Unsupported source: {source}")

    def undistortProcess(self, source: str) -> None:
        """
        Undistort a single image or every frame of a video and display the result.

        Args:
            source: Path to an image or video file.

        Raises:
            RuntimeError: If camera has not been calibrated yet.
        """
        if self.cameraMatrix is None or self.distCoeffs is None:
            raise RuntimeError("Camera not calibrated. Run calibrateProcess() first.")
        path = Path(source)
        ext = path.suffix.lower().lstrip('.')

        if ext in ('jpg', 'jpeg', 'png', 'bmp', 'tiff'):
            image = cv2.imread(str(path))
            if image is None:
                raise FileNotFoundError(f"Could not read image: {source}")
            self._undistortImage(image)
        else:
            self._undistortVideo(str(path))

    def _calibrateFromImages(self, folder: Path) -> None:
        imagePaths = list(folder.glob("*.png")) + list(folder.glob("*.jpg"))
        frames: list[NDArray] = [f for p in imagePaths
                             if (f := cv2.imread(str(p))) is not None]
        self._runCalibration(frames)

    def _calibrateFromVideo(self, path: Path) -> None:
        cap = cv2.VideoCapture(str(path))
        frames: list[NDArray] = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        self._runCalibration(frames)

    def _runCalibration(self, frames: list[NDArray]) -> None:
        objPoints: list[NDArray] = []
        imgPoints: list[NDArray] = []
        objp = np.zeros((self.boardSize[0] * self.boardSize[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.boardSize[0], 0:self.boardSize[1]].T.reshape(-1, 2)

        grayShape: tuple[int, int] = (0, 0)

        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            grayShape = (gray.shape[0], gray.shape[1])
            ret, corners = cv2.findChessboardCorners(gray, self.boardSize)
            if ret:
                objPoints.append(objp)
                imgPoints.append(corners)

        if not objPoints:
            raise ValueError("No valid calibration frames found.")
        
        imageSize = (grayShape[1], grayShape[0])
        initMatrix = np.zeros((3, 3), dtype=np.float64)
        initDist = np.zeros((5, 1), dtype=np.float64)

        _, self.camera_matrix, self.distCoeffs, _, _ = cv2.calibrateCamera(
        objPoints, imgPoints, imageSize, initMatrix, initDist
        )

        print(f"Calibrated from {len(objPoints)} frames.")

    def _undistortImage(self, image: NDArray) -> None:
        assert self.cameraMatrix is not None and self.distCoeffs is not None
        result = cv2.undistort(image, self.cameraMatrix, self.distCoeffs)
        cv2.imshow("Undistorted", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def _undistortVideo(self, path: str) -> None:
        assert self.cameraMatrix is not None and self.distCoeffs is not None
        cap = cv2.VideoCapture(path)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            result = cv2.undistort(frame, self.cameraMatrix, self.distCoeffs)
            cv2.imshow("Undistorted", result)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def displayResults(self, display: NDArray) -> None:
        """
        Display the annotated image in a window until a key is pressed.

        Args:
            display: Image array to display.

        Raises:
            ValueError: If display is None or empty.
        """
        if display is None or display.size == 0:
            raise ValueError("No display image to show.")
        cv2.imshow("Camera Calibration", display)
        cv2.waitKey(0)
        cv2.destroyAllWindows()