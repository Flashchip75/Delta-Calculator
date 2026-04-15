"""
inverse_kinematics.py
=====================
Liest Trajektorie aus CSV, berechnet fuer jeden Zeitschritt:
  phi   : Motorwinkel        [rad]   (3,)
  omega : Winkelgeschw.      [rad/s] (3,)
  alpha : Winkelbeschl.      [rad/s²](3,)

Methode differentielle Kinematik (Jacobi):
  Schleifengleichung differenziert -> A * e_dot = B * phi_dot
  phi_dot = B^-1 * A * e_dot
  phi_ddot aus zentraler Differenz von phi_dot.

Speichert output/kinematics.npz mit t, phi, omega, alpha, pos.
"""

import numpy as np
import os
from .robot_geometry import RobotGeometry


def _jacobian_matrices(robot: RobotGeometry,
                       phi_vec: np.ndarray,
                       end_pos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Berechnet A (3x3) und B (3x3) fuer A * e_dot = B * phi_dot.

    Fuer jeden Motor i:
      u_hat_i = (e - k_i) / |e - k_i|           Unterarm-Richtung
      b_i = Lo * (-sin(phi)*u.r + cos(phi)*u.d)  Skalierung
      Zeile i von A: u_hat_i^T
      B[i,i] = b_i
    """
    A = np.zeros((3, 3))
    B = np.zeros((3, 3))
    for i, mc in enumerate(robot.motors):
        phi_i = phi_vec[i]
        Lo    = mc.upper.length
        r     = mc.radial_vec
        d     = mc.drop_vec
        k_i   = robot.joint_pos(i, phi_i)

        u_vec  = end_pos - k_i
        u_norm = np.linalg.norm(u_vec)
        u_hat  = u_vec / u_norm if u_norm > 1e-12 else np.zeros(3)

        A[i, :] = u_hat
        B[i, i] = Lo * (-np.sin(phi_i) * np.dot(u_hat, r)
                        + np.cos(phi_i) * np.dot(u_hat, d))
    return A, B


def compute_kinematics(robot: RobotGeometry,
                       matrix: np.ndarray) -> dict:
    """
    Berechnet phi, omega, alpha fuer alle Zeitschritte.

    Parameter:
        matrix : (N, >=7) - Spalten: t, sx,sy,sz, vx,vy,vz, ...

    Rueckgabe:
        dict mit t, pos, vel, phi, omega, alpha, valid (alle shape (N,...))
    """
    N   = matrix.shape[0]
    t   = matrix[:, 0]
    pos = matrix[:, 1:4]
    vel = matrix[:, 4:7]
    acc = matrix[:, 7:10] if matrix.shape[1] > 9 else np.zeros((N, 3))

    phi   = np.zeros((N, 3))
    omega = np.zeros((N, 3))
    alpha = np.zeros((N, 3))
    valid = np.ones(N, dtype=bool)

    # ---- IK ----
    print("  IK berechnen...")
    for k in range(N):
        ok, ph = robot.ik_all(pos[k])
        if ok:
            phi[k] = ph
        else:
            valid[k] = False
            phi[k]   = phi[k-1] if k > 0 else 0.0

    # ---- omega via Jacobi ----
    print("  Jacobi (omega)...")
    for k in range(N):
        if not valid[k]:
            continue
        A, B = _jacobian_matrices(robot, phi[k], pos[k])
        if abs(np.linalg.det(B)) < 1e-12:
            valid[k] = False
            continue
        omega[k] = np.linalg.solve(B, A @ vel[k])

    # ---- alpha: zentrale Differenz von omega ----
    print("  Winkelbeschleunigung (numerisch)...")
    for k in range(N):
        if k == 0 or k == N - 1:
            alpha[k] = np.zeros(3)
            continue
        if not valid[k]:
            continue
        dt = t[k+1] - t[k-1]
        if dt > 1e-12:
            alpha[k] = (omega[k+1] - omega[k-1]) / dt

    n_valid = np.sum(valid)
    print(f"  Gueltige Zeitschritte: {n_valid}/{N}")

    return dict(t=t, pos=pos, vel=vel, phi=phi,
                omega=omega, alpha=alpha, valid=valid)


def save_kinematics(result: dict, out_dir: str = "output"):
    os.makedirs(out_dir, exist_ok=True)
    path = f"{out_dir}/kinematics.npz"
    np.savez(path, **result)
    print(f"  Gespeichert: {path}")

    # ---- CSV Export ----
    csv_path = f"{out_dir}/kinematics.csv"

    t     = result["t"].reshape(-1, 1)
    pos   = result["pos"]
    vel   = result["vel"]
    phi   = result["phi"]
    omega = result["omega"]
    alpha = result["alpha"]
    valid = result["valid"].astype(int).reshape(-1, 1)

        # optional torque
    torque = result.get("torque", None)

    if torque is not None:
        data = np.hstack([t, pos, vel, phi, omega, alpha, torque, valid])
        header = (
            "t,"
            "x,y,z,"
            "vx,vy,vz,"
            "phi1,phi2,phi3,"
            "omega1,omega2,omega3,"
            "alpha1,alpha2,alpha3,"
            "tau1,tau2,tau3,"
            "valid"
        )
    else:
        data = np.hstack([t, pos, vel, phi, omega, alpha, valid])
        header = (
            "t,"
            "x,y,z,"
            "vx,vy,vz,"
            "phi1,phi2,phi3,"
            "omega1,omega2,omega3,"
            "alpha1,alpha2,alpha3,"
            "valid"
        )

    np.savetxt(csv_path, data, delimiter=",", header=header, comments="")
    print(f"  CSV gespeichert: {csv_path}")

def load_kinematics(out_dir: str = "output") -> dict:
    path = f"{out_dir}/kinematics.npz"
    d = np.load(path)
    return {k: d[k] for k in d.files}


if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    robot  = RobotGeometry("config.txt")
    matrix = np.loadtxt(robot.trajectory_csv, delimiter=",", skiprows=1)
    result = compute_kinematics(robot, matrix)
    save_kinematics(result)
