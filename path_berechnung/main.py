import os
import json
from pathlib import Path

from geometry import Bezier, Line
from physics import PhysicsEngine, FrenetForceCalculator
from trajectory import Trajectory
from visualization import Visualizer

# 1. Geometrien (Punkte z.B. aus CAD in Millimetern mm ausgelesen)
c1 = Line([0, 0, 0], [100, 0, 0])

currentDir = Path(__file__).parent
configPath = currentDir.parent / "config.json"

with open(configPath, 'r') as f:
    config = json.load(f)

globalConfig = config.get('global', {})
pathConfig = config.get('path', {})

# 2. Pfad berechnen. scale_m=0.001 rechnet die mm sofort in SI-Meter um!
dur_s = pathConfig.get('duration_s')
pts = pathConfig.get('points')
gain = pathConfig.get('gain')
blend = pathConfig.get('blend')
scale_m = pathConfig.get('scale_m')

if dur_s is None: raise KeyError("Missing config: global.duration_s")
if pts is None: raise KeyError("Missing config: global.points")
if gain is None: raise KeyError("Missing config: global.gain")
if blend is None: raise KeyError("Missing config: global.blend")
if scale_m is None: raise KeyError("Missing config: global.scale_m")

traj = Trajectory([c1], dur_s=dur_s, pts=pts, gain=gain, blend=blend, scale_m=scale_m)

# 3. Physik injizieren (m_kg = 1.0 kg) und Export
gravity = globalConfig.get('gravity')
mass = globalConfig.get('mass_kg')
fname = globalConfig.get('trajectory_csv')
outputDir = globalConfig.get('output_dir', 'output')

if gravity is None: raise KeyError("Missing config: global.gravity")
if fname is None: raise KeyError("Missing config: global.trajectory_csv")
if mass is None: raise KeyError("Missing config: global.mass_kg")
if outputDir is None: raise KeyError("Missing config: global.output_dir")

P, T = traj.export(fname, outputDir, PhysicsEngine(), FrenetForceCalculator(m_kg=mass, gravity=gravity))

# 4. Daten plotten
viz = Visualizer()
viz.plot_matlab_style(P, T)
viz.plot_forces(fname, outputDir)