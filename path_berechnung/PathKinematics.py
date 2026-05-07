import numpy as np
from scipy.interpolate import interp1d


class PathKinematics:
    def __init__(self, pts, T, v0=0.0, v1=0.0, a0=0.0, a1=0.0):
        # ... (Bestehende Pfadberechnung bleibt gleich) ...
        s_in = np.insert(np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1)), 0, 0)
        L = s_in[-1]
        t_ref = np.linspace(0, T, 10000);
        tau = t_ref / T

        # Polynom-Lösung (wie gehabt)
        c0 = 0.0;
        c1 = v0 * T;
        c2 = 0.5 * a0 * T ** 2
        A = np.array([[1, 1, 1], [3, 4, 5], [6, 12, 20]])
        B = np.array([L - c0 - c1 - c2, v1 * T - c1 - 2 * c2, a1 * T ** 2 - 2 * c2])
        c3, c4, c5 = np.linalg.solve(A, B)

        self.t = interp1d(c0 + c1 * tau + c2 * tau ** 2 + c3 * tau ** 3 + c4 * tau ** 4 + c5 * tau ** 5, t_ref,
                          fill_value="extrapolate")(s_in)
        tau_v = self.t / T
        self.s = c0 + c1 * tau_v + c2 * tau_v ** 2 + c3 * tau_v ** 3 + c4 * tau_v ** 4 + c5 * tau_v ** 5
        self.v = (c1 + 2 * c2 * tau_v + 3 * c3 * tau_v ** 2 + 4 * c4 * tau_v ** 3 + 5 * c5 * tau_v ** 4) / T
        self.a = (2 * c2 + 6 * c3 * tau_v + 12 * c4 * tau_v ** 2 + 20 * c5 * tau_v ** 3) / (T ** 2)

    def calculate_forces(self, frenet, mass=1.0, g=9.81):
        """Berechnet die Gesamtkraft inklusive Gravitation direkt hier."""[cite: 1]
        # Tangentialkraft (Beschleunigung entlang der Bahn)
        F_t = self.a[:, None] * frenet.T

        # Normalkraft (Zentripetalkraft durch Kurve)
        F_n = (self.v ** 2)[:, None] * frenet.kappa[:, None] * frenet.N

        # Gewichtskraft (immer in negative Z-Richtung wirkend)
        F_g = np.array([0, 0, -mass * g])

        # Gesamtkraft-Vektor (Vektorielle Summe)
        self.F_vec = F_t + F_n - F_g  # Minus F_g, da g nach unten zieht
        self.F_mag = np.linalg.norm(self.F_vec, axis=1)
        return self.F_vec, self.F_mag