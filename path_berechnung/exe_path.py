from config import cfg
from .geometry import Bezier, Line
from .physics import PhysicsEngine, FrenetForceCalculator
from .trajectory import Trajectory
from .visualization import Visualizer


class exePath:
    def run(self,p1:tuple[int,int,int], p2:tuple[int,int,int]):
        # 1. Geometrie
        print("=== Definiere Pfad-Geometrie ===")
        c = Line(p1,p2)

        # 2. Trajektorie
        p = cfg.path
        traj = Trajectory(
            [c],
            dur_s   = p.duration_s,
            pts     = p.points,
            gain    = p.gain,
            blend   = p.blend,
            scale_m = p.scale_m,
        )

        # 3. Physik & Export
        print("=== Berechne Trajektorie & Kräfte ===")
        g = cfg.global_cfg

        phys  = PhysicsEngine()
        force = FrenetForceCalculator(m_kg=g.mass_kg, gravity=g.gravity)

        P, T = traj.export(g.trajectory_csv, g.output_dir,phys,force)
        d    = traj.toDictVar(phys, force)

        
        # 4. Visualisierung
        print("\n=== Visualisiere Ergebnisse ===")
        viz = Visualizer()
        viz.plot_matlab_style(P, T, g.output_dir)
        viz.plot_forces(g.trajectory_csv, g.output_dir)

        return d