from geometry import Bezier, Line
from physics import PhysicsEngine, FrenetForceCalculator
from trajectory import Trajectory
from visualization import Visualizer

# 1. Geometrien (Punkte z.B. aus CAD in Millimetern mm ausgelesen)
c1 = Line([0, 0, 0], [100, 0, 0])


# 2. Pfad berechnen. scale_m=0.001 rechnet die mm sofort in SI-Meter um!
# dur_s = 5.0 Sekunden
traj = Trajectory([c1], dur_s=5, pts=1000, gain=50.0, blend=0, scale_m=0.001)

# 3. Physik injizieren (m_kg = 1.0 kg) und Export
fname = "robot_path.csv"
P, T = traj.export(fname, PhysicsEngine(), FrenetForceCalculator(m_kg=1))

# 4. Daten plotten
viz = Visualizer()
viz.plot_matlab_style(P, T)
viz.plot_forces(fname)