from aruco_detector import ArucoDetector
from yolo_detector import YoloDetector

ASOURCE = "tests/media/test5.png"
YSOURCE  = "tests/media/test6.jpg"

ad = ArucoDetector()
aDetections, aDisplay = ad.process(ASOURCE)
#detections, display = ad.process(ASOURCE)

print(f"ArUco — Found {len(aDetections)} markers:")
for d in aDetections:
    center = ad.centerPxToMM(d['center'], 1.45)
    print(f"  ID {d['id']}: {center}mm")

#ad.displayResults(aDisplay)

yd = YoloDetector()
yDetections, yDisplay = yd.process(YSOURCE)
print(f"YOLO — found {len(yDetections)} objects:")
for d in yDetections:
    center = ad.centerPxToMM(d['center'], 1.45)
    print(f"  Class {d['classId']}: {center}mm, confidence={d['confidence']:.2f}")

#yd.displayResults(yDisplay)