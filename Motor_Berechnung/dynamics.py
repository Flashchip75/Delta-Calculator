"""
dynamics.py
===========
Berechnet Drehmoment an jedem Motor via Lagrange-Methode.

Lagrange-Funktion L = T - V:

  Kinetische Energie T:
    T = sum_i [ 1/2 * I_o,i * omega_i^2          (Oberarm, Stabtraegheit)
              + 1/2 * m_u,i * Lo,i^2 * omega_i^2  (Unterarm-Masse am Gelenk)
              ]
      + 1/2 * m_E * |v_E|^2                        (Payload)

  Potenzielle Energie V:
    V = sum_i [ m_o,i * g . s_o,i(phi_i)           (Oberarm-SP bei Lo/2)
              + m_u,i * g . k_i(phi_i)              (Unterarm-Masse am Gelenk)
              ]
      + m_E * g . e

  Euler-Lagrange (diagonal, da Ketten kinematisch entkoppelt):
    tau_i = I_ges,i * alpha_i + dV/dphi_i - Q_ext,i

  dV/dphi_i : analytisch (Ableitung der Schwerpunkts-z-Koordinaten)
  Q_ext,i   : generalisierte externe Kraft via virtuelle Arbeit
               Q_ext,i = (dk_i/dphi_i) . F_ext (projiziert auf Unterarm)

Ausgabe:
  output/kinematics.npz  wird um 'torque' ergaenzt
  output/motor_results.png
"""

import numpy as np
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .robot_geometry import RobotGeometry
from .inverse_kinematics import load_kinematics, save_kinematics


# ==============================================================================
# Drehmoment Lagrange
# ==============================================================================

def _torque_lagrange(
    robot:     RobotGeometry,
    motor_idx: int,
    phi_i:     float,
    omega_i:   float,
    alpha_i:   float,
    end_pos:   np.ndarray,
    F_ext:     np.ndarray,
) -> float:
    """
    Drehmoment an Motor motor_idx via Lagrange.

    tau_i = I_ges * alpha_i  +  dV/dphi_i  -  Q_ext,i

    I_ges,i = 1/3 * m_o * Lo^2   (Oberarm, Stabtraegheit um Motorende)
            + m_u * Lo^2          (Unterarmasse als Punktmasse bei Lo)

    dV/dphi_i wird analytisch aus der z-Koordinate der Schwerpunkte berechnet.

    Q_ext,i: generalisierte Kraft des externen Kraftvektors F_ext.
      dk_i/dphi_i = Lo*(-sin(phi)*r_hat + cos(phi)*d_hat)
      Unterarm uebertraegt Kraft entlang seiner Achse:
      u_hat = (e - k_i)/|e - k_i|
      Q_ext,i = (dk_i/dphi_i . u_hat) * (F_ext . u_hat)
    """
    mc   = robot.motors[motor_idx]
    Lo   = mc.upper.length
    mo   = mc.upper.mass
    Io   = mc.upper.inertia      # 1/3 * mo * Lo^2
    mu   = mc.lower.mass
    r    = mc.radial_vec
    d    = mc.drop_vec
    g    = robot.gravity

    I_ges = Io + mu * Lo**2

    # Gelenk-Endpunkt und Ableitung nach phi
    k_i      = mc.position + Lo * (np.cos(phi_i) * r + np.sin(phi_i) * d)
    dk_dphi  = Lo * (-np.sin(phi_i) * r + np.cos(phi_i) * d)

    # Oberarm-Schwerpunkt und Ableitung
    s_i      = mc.position + 0.5 * Lo * (np.cos(phi_i) * r + np.sin(phi_i) * d)
    ds_dphi  = 0.5 * dk_dphi

    # dV/dphi_i = -( m_o * g . ds/dphi  +  m_u * g . dk/dphi )
    #  Vorzeichen: V = m*g.r, dV/dphi = m*g . dr/dphi
    #  Im Lagrange-Term: tau = ... + dV/dphi (da L = T - V -> -dL/dphi = +dV/dphi)
    dV_dphi = (float(np.dot(mo * g, ds_dphi))
             + float(np.dot(mu * g, dk_dphi)))

    # Externe Kraft (Payload-Kraft via Unterarm)
    u_vec  = end_pos - k_i
    u_norm = np.linalg.norm(u_vec)
    if u_norm > 1e-9:
        u_hat   = u_vec / u_norm
        # Jacobi-Projektion: wie viel von dk/dphi entlang u_hat
        jac_col = float(np.dot(dk_dphi, u_hat))
        Q_ext   = jac_col * float(np.dot(F_ext, u_hat))
    else:
        Q_ext = 0.0

    tau = I_ges * alpha_i + dV_dphi - Q_ext
    return float(tau)


def compute_torques(robot: RobotGeometry,
                    kin: dict,
                    matrix: np.ndarray) -> np.ndarray:
    """
    Berechnet Drehmomente fuer alle Zeitschritte.

    Parameter:
        kin    : Ergebnis aus inverse_kinematics.compute_kinematics()
        matrix : (N, 16) Trajektorienmatrix (Spalten 13-15: Fx,Fy,Fz)

    Rueckgabe:
        torque : (N, 3) Drehmoment [Nm] an Motor A, B, C
    """
    N      = kin["t"].shape[0]
    torque = np.zeros((N, 3))

    has_force = matrix.shape[1] >= 16
    F_grav    = robot.payload_mass * robot.gravity   # Schwerkraft auf Payload

    for k in range(N):
        if not kin["valid"][k]:
            continue
        # Externe Kraft = Traegheitskraft + Schwerkraft des Payloads
        if has_force:
            F_ext = matrix[k, 13:16]
        else:
            # Fallback: nur Schwerkraft
            F_ext = F_grav

        for i in range(3):
            torque[k, i] = _torque_lagrange(
                robot, i,
                kin["phi"][k, i],
                kin["omega"][k, i],
                kin["alpha"][k, i],
                kin["pos"][k],
                F_ext,
            )

    return torque


# ==============================================================================
# Plot
# ==============================================================================

def plot_motor_results(kin: dict, torque: np.ndarray, out_dir: str = "output"):
    """
    4-Panel-Plot: phi, omega, alpha, torque fuer alle 3 Motoren.
    """
    t      = kin["t"]
    phi    = np.rad2deg(kin["phi"])
    omega  = np.rad2deg(kin["omega"])
    alpha  = np.rad2deg(kin["alpha"])
    names  = ["A", "B", "C"]
    colors = ["tab:red", "tab:green", "tab:blue"]

    fig, axes = plt.subplots(4, 1, figsize=(12, 14), sharex=True)
    fig.suptitle("Motor-Ergebnisse", fontsize=13, fontweight="bold")

    datasets = [
        (phi,    "Winkel φ [°]"),
        (omega,  "Winkelgeschw. ω [°/s]"),
        (alpha,  "Winkelbeschl. α [°/s²]"),
        (torque, "Drehmoment T [Nm]"),
    ]

    for ax, (data, ylabel) in zip(axes, datasets):
        for i in range(3):
            ax.plot(t, data[:, i], color=colors[i],
                    label=f"Motor {names[i]}", linewidth=1.8)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.legend(ncol=3, fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(t[0], t[-1])

    axes[-1].set_xlabel("Zeit t [s]")
    plt.tight_layout()
    path = f"{out_dir}/motor_results.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Gespeichert: {path}")


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    robot  = RobotGeometry("config.txt")
    matrix = np.loadtxt(robot.trajectory_csv, delimiter=",", skiprows=1)
    kin    = load_kinematics()
    torque = compute_torques(robot, kin, matrix)
    kin["torque"] = torque
    save_kinematics(kin)
    plot_motor_results(kin, torque)
