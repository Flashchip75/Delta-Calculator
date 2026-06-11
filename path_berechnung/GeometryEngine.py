import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.optimize import brentq

class GeometryEngine:
    @staticmethod
    def berechne_kumulierte_pfadlaengen(punkte_3d):
        pts = np.array(punkte_3d)
        if len(pts) < 2: return np.array([0.0])
        distanzen = np.sqrt(np.sum(np.diff(pts, axis=0) ** 2, axis=1))
        return np.concatenate(([0.0], np.cumsum(distanzen)))