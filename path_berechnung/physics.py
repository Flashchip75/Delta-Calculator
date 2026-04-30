import os
import json
import numpy as np

class PhysicsEngine:
    def compute(self, p, t):
        v, a = np.gradient(p, t, axis=0), np.gradient(np.gradient(p, t, axis=0), t, axis=0) # in m/s und m/s^2
        nv = np.linalg.norm(v, axis=1, keepdims=True)
        T = np.divide(v, nv, out=np.zeros_like(v), where=nv!=0)
        dT = np.gradient(T, t, axis=0)
        nn = np.linalg.norm(dT, axis=1, keepdims=True)
        N = np.divide(dT, nn, out=np.zeros_like(dT), where=nn!=0)
        K = np.divide(np.linalg.norm(np.cross(v, a), axis=1, keepdims=True), nv**3, out=np.zeros_like(nv), where=nv!=0)
        return v, a, np.gradient(a, t, axis=0), T, N, np.cross(T, N), K # K in 1/m, j in m/s^3

class FrenetForceCalculator:
    def __init__(self, m_kg, gravity):
        self.m = m_kg
        self.g = np.array(gravity) if gravity is not None else np.array([0, 0, 9.81])

    def get_forces(self, a, T, N):
        Ft = self.m * np.sum(a*T, axis=1, keepdims=True) * T
        Fn = self.m * np.sum(a*N, axis=1, keepdims=True) * N
        return Ft, Fn, self.m * (a + self.g) # a + g (beides zwingend in m/s^2), F in Newton