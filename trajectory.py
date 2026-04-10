import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.ndimage import gaussian_filter1d


class Trajectory:
    def __init__(self, curves, dur_s, pts=101, gain=50.0, blend=5.0, scale_m=1.0):
        raw = np.vstack(
            [[c.f(ti) for ti in np.linspace(0, 1, 300)] for c in curves]) * scale_m  # Skalierung auf SI (Meter)!
        pr = raw[np.append([True], np.linalg.norm(np.diff(raw, axis=0), axis=1) > 1e-6)]
        if blend > 0: pr = gaussian_filter1d(pr, sigma=blend, axis=0)

        sr = np.insert(np.cumsum(np.linalg.norm(np.diff(pr, axis=0), axis=1)), 0, 0)
        vk = np.gradient(pr, sr, axis=0)
        kp = np.linalg.norm(np.cross(vk, np.gradient(vk, sr, axis=0)), axis=1)
        sm = np.cumsum(1.0 + gain * (kp / np.max(kp) if np.max(kp) > 0 else kp))
        s_adp = np.interp(np.linspace(sm[0], sm[-1], pts), sm, sr)

        self.p, self.t = CubicSpline(sr, pr)(s_adp), s_adp / s_adp[-1] * dur_s

    def export(self, fname, phys, force, exportCsv=True):
        v, a, j, T, N, B, K = phys.compute(self.p, self.t)
        data = np.column_stack((self.t, self.p, v, a, j, T, N, B, K, *force.get_forces(a, T, N)))
        if exportCsv:
            pd.DataFrame(data,
                        columns='t x y z vx vy vz ax ay az jx jy jz tx ty tz nx ny nz bx by bz kappa ftx fty ftz fnx fny fnz fx fy fz'.split()).to_csv(
                fname, index=False)
        return self.p, T
    
    def toDictVar(self, phys, force) -> dict[str, np.ndarray]:
        """
        Compute trajectory kinematics and forces and return them as named numpy arrays.

        Args:
            phys:  PhysicsEngine instance to compute velocity, acceleration, jerk, and Frenet frame.
            force: FrenetForceCalculator instance to compute tangential, normal, and total forces.

        Returns:
            Dictionary mapping field names to 1D numpy arrays of length pts, with keys:
            - t              ; time
            - x, y, z        ; position
            - vx, vy, vz     ; velocity
            - ax, ay, az     ; acceleration
            - jx, jy, jz     ; jerk
            - tx, ty, tz     ; Frenet tangent vector
            - nx, ny, nz     ; Frenet normal vector
            - bx, by, bz     ; Frenet binormal vector
            - kappa          ; curvature
            - ftx, fty, ftz  ; tangential force components
            - fnx, fny, fnz  ; normal force components
            - fx,  fy,  fz   ; total force components
        """
        v, a, j, T, N, B, K = phys.compute(self.p, self.t)
        fx, fy, fz = force.get_forces(a, T, N)
        return {
            't':     self.t,
            'x':     self.p[:, 0], 'y':     self.p[:, 1], 'z':     self.p[:, 2],
            'vx':    v[:, 0],      'vy':    v[:, 1],       'vz':    v[:, 2],
            'ax':    a[:, 0],      'ay':    a[:, 1],       'az':    a[:, 2],
            'jx':    j[:, 0],      'jy':    j[:, 1],       'jz':    j[:, 2],
            'tx':    T[:, 0],      'ty':    T[:, 1],       'tz':    T[:, 2],
            'nx':    N[:, 0],      'ny':    N[:, 1],       'nz':    N[:, 2],
            'bx':    B[:, 0],      'by':    B[:, 1],       'bz':    B[:, 2],
            'kappa': K,
            'ftx':   fx[:, 0],     'fty':   fx[:, 1],      'ftz':   fx[:, 2],
            'fnx':   fy[:, 0],     'fny':   fy[:, 1],      'fnz':   fy[:, 2],
            'fx':    fz[:, 0],     'fy':    fz[:, 1],      'fz':    fz[:, 2],
        }