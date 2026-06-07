import numpy as np; from scipy.interpolate import interp1d

class PathKinematics:
    def __init__(self, pts, T):
        s_in = np.insert(np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1)), 0, 0)
        s_max = s_in[-1]; t_ref = np.linspace(0, T, 10000); tau = t_ref / T
        self.t = interp1d(s_max * (10*tau**3 - 15*tau**4 + 6*tau**5),
                          t_ref,
                          fill_value="extrapolate")(s_in)
        tau_v = self.t / T
        self.s = s_max * (10*tau_v**3 - 15*tau_v**4 + 6*tau_v**5)
        self.v = (s_max/T) * (30*tau_v**2 - 60*tau_v**3 + 30*tau_v**4)
        self.a = (s_max/T**2) * (60*tau_v - 180*tau_v**2 + 120*tau_v**3)