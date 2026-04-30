import numpy as np

class QuinticTrajectory3D:
    """
    Quintic 5. Ordnung Trajektorie von einem Startpunkt zu einem Endpunkt im 3D-Raum
    Dauer T vorgeben
    Liefert Position, Geschwindigkeit, Beschleunigung und Ruck
    """

    def __init__(self, start, end, T):
        self.start = np.array(start, dtype=float)
        self.end = np.array(end, dtype=float)
        self.T = T
        if T <= 0:
            raise ValueError("Dauer T muss > 0 sein.")
    # test
    def quintic_scalar(self, t):
        """Quintic 5. Ordnung für s(t) in [0,1]"""
        tau = np.clip(t, 0, self.T)
        s = 10*tau**3/self.T**3 - 15*tau**4/self.T**4 + 6*tau**5/self.T**5
        ds = 30*tau**2/self.T**3 - 60*tau**3/self.T**4 + 30*tau**4/self.T**5
        dds = 60*tau/self.T**3 - 180*tau**2/self.T**4 + 120*tau**3/self.T**5
        ddds = 60/self.T**3 - 360*tau/self.T**4 + 360*tau**2/self.T**5
        return s, ds, dds, ddds

    def evaluate(self, t):
        """Berechnet Position, Geschwindigkeit, Beschleunigung, Ruck im 3D-Raum"""
        s, ds, dds, ddds = self.quintic_scalar(t)
        delta = self.end - self.start
        r = self.start + s * delta
        v = ds * delta
        a = dds * delta
        j = ddds * delta
        return r, v, a, j

    def sample(self, num_points=100):
        """Liefert Arrays für Position, Geschwindigkeit, Beschleunigung und Ruck über die gesamte Dauer"""
        ts = np.linspace(0, self.T, num_points)
        r_list, v_list, a_list, j_list = [], [], [], []
        for t in ts:
            r, v, a, j = self.evaluate(t)
            r_list.append(r)
            v_list.append(v)
            a_list.append(a)
            j_list.append(j)
        return ts, np.array(r_list), np.array(v_list), np.array(a_list), np.array(j_list)