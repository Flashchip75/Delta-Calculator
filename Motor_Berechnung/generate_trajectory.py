"""
generate_trajectory.py  –  INTERNES HILFSSKRIPT (wird von run_all.py gerufen)
Generiert Spiraltrajektorie mit Minimum-Jerk-Profil und speichert:
  trajectory.csv          Eingangsdaten fuer die Transformationsfunktion
  output/trajectory_plots.png   Grafiken
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os


# ==============================================================================
# Minimum-Jerk Skalierungsfunktion s(tau), tau in [0,1]
# ==============================================================================

def _mj(tau):
    """Minimum-Jerk Polynom 5. Grades: s, ds, dds."""
    s   = 10*tau**3 - 15*tau**4 + 6*tau**5
    ds  = 30*tau**2 - 60*tau**3 + 30*tau**4
    dds = 60*tau   - 180*tau**2 + 120*tau**3
    return s, ds, dds


def generate_spiral(
    center_xy: np.ndarray,   # [x, y] Kreismittelpunkt
    z_start:   float,        # z bei t=0
    z_end:     float,        # z bei t=T
    r_start:   float,        # Startradius
    r_end:     float,        # Endradius
    n_turns:   float,        # Anzahl Umdrehungen
    T:         float,        # Gesamtzeit [s]
    N:         int,          # Zeitschritte
    mass:      float,        # Payload [kg]
    gravity:   np.ndarray,   # [m/s^2]
    theta_0:   float = 0.0,  # Startwinkel [rad]
) -> np.ndarray:
    """
    Spiralbahn mit Minimum-Jerk-Geschwindigkeitsprofil.

    Parametrisierung: theta(t) = theta_0 + 2*pi*n_turns * s(t/T)
    Radius:           R(t) = r_start + (r_end - r_start) * s(t/T)
    z(t):             z_start + (z_end - z_start) * s(t/T)

    s(tau) = Minimum-Jerk-Polynom (v=0, a=0 bei tau=0 und tau=1)

    Rueckgabe: (N, 16) Matrix
      [t, sx,sy,sz, vx,vy,vz, ax,ay,az, jx,jy,jz, Fx,Fy,Fz]
    """
    t   = np.linspace(0.0, T, N)
    tau = t / T

    s_val, ds_val, dds_val = _mj(tau)

    # dds/dt und d3s/dt3
    ds_dt   = ds_val  / T
    dds_dt2 = dds_val / T**2

    # dddS: numerisch
    ddds = np.zeros(N)
    ddds[1:-1] = (dds_val[2:] - dds_val[:-2]) / (2 * (tau[1] - tau[0]))
    ddds[0]    = ddds[1]; ddds[-1] = ddds[-2]
    dds_dt3 = ddds / T**3

    # Winkel und Ableitungen
    theta     = theta_0 + 2*np.pi*n_turns * s_val
    dtheta    = 2*np.pi*n_turns * ds_dt
    ddtheta   = 2*np.pi*n_turns * dds_dt2
    dddtheta  = 2*np.pi*n_turns * dds_dt3

    # Radius und z
    R      = r_start + (r_end   - r_start)   * s_val
    dR     = (r_end  - r_start)  * ds_dt
    ddR    = (r_end  - r_start)  * dds_dt2
    dddR   = (r_end  - r_start)  * dds_dt3

    z      = z_start + (z_end   - z_start)   * s_val
    dz     = (z_end  - z_start)  * ds_dt
    ddz    = (z_end  - z_start)  * dds_dt2
    dddz   = (z_end  - z_start)  * dds_dt3

    cx, cy = center_xy

    # Position
    sx = cx + R * np.cos(theta)
    sy = cy + R * np.sin(theta)
    sz = z

    # Geschwindigkeit  (Produktregel)
    vx = dR*np.cos(theta) - R*dtheta*np.sin(theta)
    vy = dR*np.sin(theta) + R*dtheta*np.cos(theta)
    vz = dz

    # Beschleunigung
    ax = (ddR*np.cos(theta)
          - 2*dR*dtheta*np.sin(theta)
          - R*ddtheta*np.sin(theta)
          - R*dtheta**2*np.cos(theta))
    ay = (ddR*np.sin(theta)
          + 2*dR*dtheta*np.cos(theta)
          + R*ddtheta*np.cos(theta)
          - R*dtheta**2*np.sin(theta))
    az = ddz

    # Ruck
    jx = (dddR*np.cos(theta)
          - 3*ddR*dtheta*np.sin(theta)
          - 3*dR*ddtheta*np.sin(theta)
          - 3*dR*dtheta**2*np.cos(theta)
          - R*dddtheta*np.sin(theta)
          - 3*R*ddtheta*dtheta*np.cos(theta)
          + R*dtheta**3*np.sin(theta))
    jy = (dddR*np.sin(theta)
          + 3*ddR*dtheta*np.cos(theta)
          + 3*dR*ddtheta*np.cos(theta)
          - 3*dR*dtheta**2*np.sin(theta)
          + R*dddtheta*np.cos(theta)
          - 3*R*ddtheta*dtheta*np.sin(theta)
          - R*dtheta**3*np.cos(theta))
    jz = dddz

    # Kraftvektor: F = m*a + m*g
    Fx = mass * ax + mass * gravity[0]
    Fy = mass * ay + mass * gravity[1]
    Fz = mass * az + mass * gravity[2]

    return np.column_stack([t,
                             sx, sy, sz,
                             vx, vy, vz,
                             ax, ay, az,
                             jx, jy, jz,
                             Fx, Fy, Fz])


def save_csv(matrix: np.ndarray, path: str = "trajectory.csv"):
    header = "t,sx,sy,sz,vx,vy,vz,ax,ay,az,jx,jy,jz,Fx,Fy,Fz"
    np.savetxt(path, matrix, delimiter=",", header=header, comments="")
    print(f"  Gespeichert: {path}  {matrix.shape}")


def plot_trajectory(matrix: np.ndarray, out_dir: str = "output"):
    t   = matrix[:, 0]
    pos = matrix[:, 1:4]
    vel = matrix[:, 4:7]
    acc = matrix[:, 7:10]
    jrk = matrix[:, 10:13]
    F   = matrix[:, 13:16]

    colors = ["tab:red", "tab:green", "tab:blue"]
    axlbls = ["x", "y", "z"]

    fig = plt.figure(figsize=(15, 16))
    gs  = fig.add_gridspec(5, 2, hspace=0.50, wspace=0.30)

    rows = [
        (pos, "Position s [m]",         "s"),
        (vel, "Geschwindigkeit v [m/s]", "v"),
        (acc, "Beschleunigung a [m/s²]", "a"),
        (jrk, "Ruck j [m/s³]",          "j"),
        (F,   "Kraftvektor F [N]",       "F"),
    ]
    for row, (data, ylabel, sym) in enumerate(rows):
        ax = fig.add_subplot(gs[row, 0])
        for i in range(3):
            ax.plot(t, data[:, i], color=colors[i],
                    label=f"${sym}_{axlbls[i]}$", lw=1.6)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.legend(ncol=3, fontsize=8, loc="upper right")
        ax.grid(True, alpha=0.3)
        ax.set_xlim(t[0], t[-1])
        if row == 4:
            ax.set_xlabel("Zeit t [s]")

    # 3D-Bahn
    ax3d = fig.add_subplot(gs[0:3, 1], projection="3d")
    v_mag = np.linalg.norm(vel, axis=1)
    v_max = v_mag.max() + 1e-9
    for k in range(len(t) - 1):
        col = plt.cm.plasma(v_mag[k] / v_max)
        ax3d.plot(pos[k:k+2, 0], pos[k:k+2, 1], pos[k:k+2, 2],
                  color=col, lw=2.0)
    ax3d.scatter(*pos[0],  color="green", s=70, label="Start")
    ax3d.scatter(*pos[-1], color="red",   s=70, label="Ende")
    sm = plt.cm.ScalarMappable(cmap="plasma",
                                norm=plt.Normalize(0, v_max * 1000))
    sm.set_array([])
    plt.colorbar(sm, ax=ax3d, label="|v| [mm/s]", shrink=0.5)
    ax3d.set_xlabel("x [m]", fontsize=8)
    ax3d.set_ylabel("y [m]", fontsize=8)
    ax3d.set_zlabel("z [m]", fontsize=8)
    ax3d.set_title("3D-Spiralbahn (Farbe = |v|)", fontsize=10)
    ax3d.legend(fontsize=8)

    # |v|(t)
    ax_v = fig.add_subplot(gs[3, 1])
    ax_v.plot(t, v_mag * 1000, color="tab:orange", lw=1.8)
    ax_v.set_ylabel("|v| [mm/s]", fontsize=9)
    ax_v.set_title("Bahngeschwindigkeit", fontsize=9)
    ax_v.grid(True, alpha=0.3); ax_v.set_xlim(t[0], t[-1])

    # XY-Projektion
    ax_xy = fig.add_subplot(gs[4, 1])
    ax_xy.plot(pos[:, 0], pos[:, 1], color="tab:blue", lw=1.8)
    ax_xy.scatter(pos[0,0], pos[0,1], color="green", s=50)
    ax_xy.scatter(pos[-1,0], pos[-1,1], color="red", s=50)
    ax_xy.set_xlabel("x [m]", fontsize=9); ax_xy.set_ylabel("y [m]", fontsize=9)
    ax_xy.set_title("XY-Projektion", fontsize=9)
    ax_xy.set_aspect("equal"); ax_xy.grid(True, alpha=0.3)

    fig.suptitle("Spiraltrajektorie – Minimum-Jerk-Profil",
                 fontsize=13, fontweight="bold")
    path = f"{out_dir}/trajectory_plots.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Gespeichert: {path}")


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    from robot_geometry import RobotGeometry
    robot = RobotGeometry("config.txt")

    # Workspace-Mittelpunkt als Kreiszentrum
    z_mid = (robot.ws_range_z[0] + robot.ws_range_z[1]) / 2
    R_max = 0.08   # Kreisradius [m] – passt sicher in den Workspace

    matrix = generate_spiral(
        center_xy = np.array([0.0, 0.0]),
        z_start   = z_mid + 0.15,
        z_end     = z_mid - 0.15,
        r_start   = R_max * 0.5,
        r_end     = R_max,
        n_turns   = 2.0,
        T         = 6.0,
        N         = 400,
        mass      = robot.payload_mass,
        gravity   = robot.gravity,
    )

    save_csv(matrix, path="trajectory.csv")
    plot_trajectory(matrix, out_dir="output")
