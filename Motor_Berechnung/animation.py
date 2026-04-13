"""
animation.py
============
Erstellt ein GIF des Deltaroboters entlang der Trajektorie.

Zeigt pro Frame:
  - Motorpositionen (Marker)
  - Motorachsen (kurze Pfeile)
  - Oberarme (Motor → Gelenk)
  - Unterarme (Gelenk → Endeffektor)
  - Endeffektor-Spur

Eingabe: output/kinematics.npz
Ausgabe: output/delta_robot.gif
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import os

from .robot_geometry import RobotGeometry
from .inverse_kinematics import load_kinematics


def _draw_frame(ax, robot: RobotGeometry, phi_vec: np.ndarray,
                end_pos: np.ndarray, trail: np.ndarray, t_val: float):
    ax.cla()
    colors = ["#e84c3c", "#2ecc71", "#3498db"]

    # Endeffektor-Spur
    if trail.shape[0] > 1:
        ax.plot(trail[:, 0], trail[:, 1], trail[:, 2],
                color="gray", lw=0.8, alpha=0.5)

    for i, mc in enumerate(robot.motors):
        col = colors[i]
        k_i = robot.joint_pos(i, phi_vec[i])

        # Motor-Marker + Achse
        ax.scatter(*mc.position, color=col, s=140, marker="s", zorder=5)
        ax.quiver(*mc.position, *(mc.axis_vec * 0.06),
                  color=col, linewidth=1.5, alpha=0.7)
        ax.text(mc.position[0], mc.position[1],
                mc.position[2] + 0.04, f"M{mc.name}",
                color=col, fontsize=8, ha="center")

        # Oberarm
        ax.plot([mc.position[0], k_i[0]],
                [mc.position[1], k_i[1]],
                [mc.position[2], k_i[2]],
                color=col, lw=3.0)

        # Unterarm (gestrichelt)
        ax.plot([k_i[0], end_pos[0]],
                [k_i[1], end_pos[1]],
                [k_i[2], end_pos[2]],
                color=col, lw=1.8, linestyle="--", alpha=0.85)

        # Gelenk
        ax.scatter(*k_i, color=col, s=50, zorder=4)

    # Endeffektor
    ax.scatter(*end_pos, color="black", s=110, zorder=6)
    ax.text(end_pos[0], end_pos[1], end_pos[2] - 0.05,
            "EE", color="black", fontsize=8, ha="center")

    

    ax.set_xlabel("x [m]", fontsize=7)
    ax.set_ylabel("y [m]", fontsize=7)
    ax.set_zlabel("z [m]", fontsize=7)
    ax.set_title(f"Delta Robot  t = {t_val:.2f} s", fontsize=9)
    ax.view_init(elev=18, azim=35)

    # Achsenlimits

    ax.set_xlim(-0.6, 0.6)
    ax.set_ylim(-0.6, 0.6)
    ax.set_zlim(-1, 0.0)
    ax.set_box_aspect([1, 1, 1])    # Aspect ratio


def create_gif(robot: RobotGeometry, kin: dict,
               out_dir: str = "output",
               n_frames: int = 80,
               fps: int = 20):

    os.makedirs(out_dir, exist_ok=True)
    N       = kin["t"].shape[0]
    indices = np.linspace(0, N - 1, n_frames, dtype=int)
    pos_all = kin["pos"]

    fig = plt.figure(figsize=(8, 7))
    ax  = fig.add_subplot(111, projection="3d")

    def update(frame_num):
        k        = indices[frame_num]
        phi_vec  = kin["phi"][k]
        end_pos  = pos_all[k]
        trail    = pos_all[:k + 1]
        t_val    = kin["t"][k]
        _draw_frame(ax, robot, phi_vec, end_pos, trail, t_val)
        return []

    ani    = animation.FuncAnimation(fig, update, frames=n_frames,
                                     interval=1000 // fps, blit=False)
    writer = animation.PillowWriter(fps=fps)
    path   = f"{out_dir}/delta_robot.gif"
    ani.save(path, writer=writer)
    plt.close()
    print(f"  Gespeichert: {path}")


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    robot = RobotGeometry("config.txt")
    kin   = load_kinematics()
    create_gif(robot, kin)
