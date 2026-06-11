import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.optimize import brentq

class TrajectoryMath:
    @staticmethod
    def solve_coefficients(bedingungen):
        n = len(bedingungen)
        M = np.zeros((n, n))
        b = np.zeros(n)
        for i, (k, t_lokal, wert) in enumerate(bedingungen):
            b[i] = wert
            for j in range(n):
                if j >= k:
                    faktor = math.factorial(j) / math.factorial(j - k)
                    M[i, j] = faktor * (t_lokal ** (j - k))
        return np.linalg.solve(M, b)

    @staticmethod
    def get_poly_val(koeff, t, k=0):
        wert = 0.0
        for j in range(k, len(koeff)):
            faktor = math.factorial(j) / math.factorial(j - k)
            wert += koeff[j] * faktor * (t ** (j - k))
        return wert