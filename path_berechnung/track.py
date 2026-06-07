import numpy as np

class Curve:
    def __init__(self, cfg): self.c = cfg
    def __call__(self, t):
        c = self.c; typ, p = c['type'], np.array(c.get('pts', []))
        if typ == 'Line': return p[0]*(1-t) + p[1]*t
        if typ == 'Bezier': return (1-t)**3*p[0] + 3*t*(1-t)**2*p[1] + 3*t**2*(1-t)*p[2] + t**3*p[3]
        if typ in ['Arc', 'Circle']:
            a = c.get('a', [0, 2*np.pi]); ang = a[0] + t*(a[1]-a[0])
            return np.array(c['c']) + c['r'] * (np.cos(ang)*np.array(c['u']) + np.sin(ang)*np.array(c['v']))

class Trajectory:
    def __init__(self, json_data, ppm=10000):
        r = np.vstack([[Curve(c)(t) for t in np.linspace(0, 1, 200)] for c in json_data])
        r = r[np.append([True], np.linalg.norm(np.diff(r, axis=0), axis=1) > 1e-6)]
        s = np.insert(np.cumsum(np.linalg.norm(np.diff(r, axis=0), axis=1)), 0, 0)
        self.cloud = np.array([np.interp(np.linspace(0, s[-1], int(s[-1]*ppm)), s, r[:, i]) for i in range(3)]).T