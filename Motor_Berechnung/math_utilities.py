import numpy as np

def norm(v):
    return np.linalg.norm(v)

def unit(v):
    n = norm(v)
    if n == 0:
        raise ValueError("Nullvektor kann nicht normiert werden.")
    return v / n

def sphere_sphere_intersection(A, RA, B, RB):
    AB = B - A
    c = norm(AB)

    if c == 0:
        raise ValueError("Die Kugelmittelpunkte A und B dürfen nicht identisch sein.")

    if c > RA + RB:
        raise ValueError(
            f"Die Kugeln schneiden sich nicht: Abstand {c:.6f} > RA+RB {RA + RB:.6f}"
        )

    if c < abs(RA - RB):
        raise ValueError(
            f"Eine Kugel liegt in der anderen: Abstand {c:.6f} < |RA-RB| {abs(RA - RB):.6f}"
        )

    e = unit(AB)
    d = (RA**2 - RB**2 + c**2) / (2 * c)
    h2 = RA**2 - d**2
    h = np.sqrt(max(h2, 0.0))
    N = A + d * e

    return N, e, h

def plane_plane_intersection(n1, p1, n2, p2):
    u = np.cross(n1, n2)
    u_norm = np.dot(u, u)

    if u_norm == 0:
        raise ValueError("Die Ebenen sind parallel oder identisch.")

    c1 = np.dot(n1, p1)
    c2 = np.dot(n2, p2)
    P0 = (c1 * np.cross(n2, u) + c2 * np.cross(u, n1)) / u_norm

    return P0, u

def line_circle_intersection(P0, u, center, r):
    w = P0 - center
    A = np.dot(u, u)
    Bq = 2 * np.dot(w, u)
    C = np.dot(w, w) - r**2
    disc = Bq**2 - 4 * A * C

    if disc < 0:
        raise ValueError("Gerade schneidet den Kreis nicht.")

    disc = max(disc, 0.0)
    lam1 = (-Bq + np.sqrt(disc)) / (2 * A)
    lam2 = (-Bq - np.sqrt(disc)) / (2 * A)

    P1 = P0 + lam1 * u
    P2 = P0 + lam2 * u

    return P1, P2

def get_circle_basis(normal):
    normal = unit(normal)

    if abs(normal[0]) < 0.9:
        v = np.cross(normal, [1.0, 0.0, 0.0])
    else:
        v = np.cross(normal, [0.0, 1.0, 0.0])

    v = unit(v)
    w = unit(np.cross(normal, v))

    return v, w
