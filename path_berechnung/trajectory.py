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

    def export(self, fname, phys, force):
        v, a, j, T, N, B, K = phys.compute(self.p, self.t)
        data = np.column_stack((self.t, self.p, v, a, j, T, N, B, K, *force.get_forces(a, T, N)))
        pd.DataFrame(data,
                     columns='t x y z vx vy vz ax ay az jx jy jz tx ty tz nx ny nz bx by bz kappa ftx fty ftz fnx fny fnz fx fy fz'.split()).to_csv(
            fname, index=False)
        return self.p, T