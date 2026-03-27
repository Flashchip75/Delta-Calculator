import cv2
import cv2.aruco as aruco

image = cv2.imread("image/test4.PNG")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
detector = aruco.ArucoDetector(dictionary)

corners, ids, _ = detector.detectMarkers(gray)

target_ids = {0, 1000}
coords = {}

if ids is not None:
    for corner, id in zip(corners, ids):
        print(f"ID {id[0]}")
    for corner, id in zip(corners, ids.flatten()):
        if id in target_ids:
            cx = corner[0][:, 0].mean()
            cy = corner[0][:, 1].mean()
            coords[id] = (cx, cy)

print(coords)