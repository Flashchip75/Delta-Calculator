import numpy as np; from scipy.signal import savgol_filter

class PathFrenet:
    def __init__(self, pts):
        ds = np.maximum(np.linalg.norm(np.gradient(pts, axis=0), axis=1, keepdims=True), 1e-9)
        self.T = np.gradient(pts, axis=0) / ds
        dT_ds = np.gradient(self.T, axis=0) / ds
        self.kappa = np.clip(savgol_filter(np.linalg.norm(dT_ds, axis=1), 51, 3), 0, None)
        self.N = dT_ds / np.maximum(self.kappa[:, None], 1e-9)
        for i in range(3): self.N[:, i] = savgol_filter(self.N[:, i], 51, 3)
        self.N /= np.maximum(np.linalg.norm(self.N, axis=1, keepdims=True), 1e-9)