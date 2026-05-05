import numpy as np

class PathTangents:
    def __init__(self, pts):
        d = np.gradient(pts, axis=0)
        self.tangents = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)