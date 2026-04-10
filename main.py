from geometry import Bezier, Line
from physics import PhysicsEngine, FrenetForceCalculator
from trajectory import Trajectory
from visualization import Visualizer
from aruco_detector import ArucoDetector
from yolo_detector import YoloDetector

ASOURCE = "tests/media/test5.png"

ad = ArucoDetector()
aDetections, aDisplay = ad.process(ASOURCE)

#mmPerPx = ad.calibrate(ASOURCE, normMM=100.0, calibId=0)
mmPerPx = 1  # Beispielwert, da Kalibrierung nicht durchgeführt wird

start, end = ad.getPointsMM(aDetections, mmPerPx, 0, 29)
c1 = Line(start, end)
#c1 = Line([0, 0, 0], [100, 100, 0])

# 2. Pfad berechnen. scale_m=0.001 rechnet die mm sofort in SI-Meter um!
# dur_s = 5.0 Sekunden
traj = Trajectory([c1], dur_s=5, pts=100, gain=00.0, blend=0, scale_m=1)

# 3. Physik injizieren (m_kg = 1.0 kg) und Export
fname = "robot_path.csv"

phys  = PhysicsEngine()
force = FrenetForceCalculator(m_kg=1)

P, T = traj.export(fname, phys, force, exportCsv=True)
d    = traj.toDictVar(phys, force)

# 4. Daten plotten
viz = Visualizer()
viz.plot_matlab_style(P, T)
#viz.plot_forces(fname)