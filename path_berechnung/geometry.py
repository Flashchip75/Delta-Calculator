import numpy as np

class Bezier:
    def __init__(self, p): self.p = np.array(p)
    def f(self, t): return (1-t)**3*self.p[0] + 3*t*(1-t)**2*self.p[1] + 3*t**2*(1-t)*self.p[2] + t**3*self.p[3]

class Line:
    def __init__(self, p0, p1): self.p0, self.dp = np.array(p0), np.array(p1) - np.array(p0)
    def f(self, t): return self.p0 + t * self.dp

class Arc:
    def __init__(self, c, r, u, v, a1=0, a2=2*np.pi):
        self.c, self.r, self.u, self.v = np.array(c), r, np.array(u), np.array(v)
        self.a1, self.da = a1, a2 - a1
    def f(self, t):
        th = self.a1 + t * self.da
        return self.c + self.r * (np.cos(th) * self.u + np.sin(th) * self.v)

class Circle:
    def __init__(self, c, r, u, v): super().__init__(c, r, u, v)