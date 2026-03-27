import cv2
import cv2.aruco as aruco
import numpy as np

image = cv2.imread("image/test5.PNG")

if image is None:
    print("ERROR: image not found")
    exit()
print(f"Image loaded: {image.shape}")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
display = image.copy()

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
aruco_detector = aruco.ArucoDetector(dictionary)
corners, ids, rejected = aruco_detector.detectMarkers(gray)

print(f"Raw ArUco markers found: {len(corners)}")
print(f"Rejected candidates: {len(rejected)}")

# draw detections in red and labels in green
if ids is not None:
    print(f"Marker IDs found: {ids.flatten()}")
    for corner, id in zip(corners, ids.flatten()):
        cx = int(corner[0][:, 0].mean())
        cy = int(corner[0][:, 1].mean())

        cv2.circle(display, (cx, cy), 6, (0, 0, 255), -1)          # red dot
        cv2.putText(display, str(id), (cx + 8, cy - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)  # green label

# draw rejected in yellow
for r in rejected:
    cx = int(r[0][:, 0].mean())
    cy = int(r[0][:, 1].mean())
    cv2.circle(display, (cx, cy), 4, (0, 255, 255), -1)  # yellow dot

cv2.imshow("detections", display)
cv2.waitKey(0)