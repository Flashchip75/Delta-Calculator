"""
workspace.py
============
Berechnet und visualisiert den Arbeitsbereich des Deltaroboters.

Methode: 3D-Gitter wird abgetastet. Jeder Punkt wird auf IK-Gueltigkeit
geprueft (alle drei Motoren, Winkelgrenzen, Singularitaet).

Ausgabe:
  output/workspace_3d.png   - perspektivische 3D-Ansicht
  output/workspace_side.png - Seitenansicht (XZ- und YZ-Schnitt)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from robot_geometry import RobotGeometry


def compute_workspace(robot: RobotGeometry) -> np.ndarray:
    """
    Gibt alle erreichbaren Gitterpunkte als (N, 3)-Array zurueck.
    Optimierung: vektorisierte Diskriminanten-Vorpruefung vor IK.
    """
    xs = np.linspace(*robot.ws_range_x, robot.ws_res)
    ys = np.linspace(*robot.ws_range_y, robot.ws_res)
    zs = np.linspace(*robot.ws_range_z, robot.ws_res)

    # Alle Gitterpunkte als Matrix (N, 3)
    XX, YY, ZZ = np.meshgrid(xs, ys, zs, indexing="ij")
    pts = np.column_stack([XX.ravel(), YY.ravel(), ZZ.ravel()])

    total = len(pts)
    print(f"Workspace: teste {total} Punkte...")

    # Vorfilter pro Motor: Punkt muss im Ringbereich [|Lo-Lu|, Lo+Lu] liegen
    reachable_mask = np.ones(total, dtype=bool)
    for mc in robot.motors:
        dist = np.linalg.norm(pts - mc.position[np.newaxis, :], axis=1)
        Lo, Lu = mc.upper.length, mc.lower.length
        reachable_mask &= (dist >= abs(Lo - Lu) + 1e-3) & (dist <= Lo + Lu - 1e-3)

    candidates = pts[reachable_mask]
    print(f"  Nach Vorfilter: {len(candidates)} Kandidaten")

    # IK-Pruefung fuer Kandidaten
    good = []
    for pt in candidates:
        ok, _ = robot.ik_all(pt)
        if ok:
            good.append(pt)

    points = np.array(good) if good else np.empty((0, 3))
    print(f"  Erreichbar: {len(points)} ({100*len(points)/total:.1f}%)")
    return points


def plot_workspace(points: np.ndarray, robot: RobotGeometry, out_dir: str = "output"):
    """Erstellt 3D-Ansicht und Seitenansicht des Arbeitsbereichs."""

    motor_colors = ["tab:red", "tab:green", "tab:blue"]

    # ----------------------------------------------------------------
    # 3D-Ansicht
    # ----------------------------------------------------------------
    fig = plt.figure(figsize=(11, 8))
    ax  = fig.add_subplot(111, projection="3d")

    if len(points) > 0:
        sc = ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                        c=points[:, 2], cmap="viridis", s=6, alpha=0.35)
        plt.colorbar(sc, ax=ax, label="z [m]", shrink=0.55)

    for i, mc in enumerate(robot.motors):
        ax.scatter(*mc.position, color=motor_colors[i], s=120, zorder=5,
                   label=f"Motor {mc.name}")
        ax.quiver(*mc.position, *(mc.axis_vec * 0.07),
                  color=motor_colors[i], linewidth=2)
    ax.scatter(*robot.center, color="black", s=70, marker="x", label="Zentrum")

    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_zlabel("z [m]")
    ax.set_title("Arbeitsbereich - 3D")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{out_dir}/workspace_3d.png", dpi=150)
    plt.close()
    print(f"  Gespeichert: {out_dir}/workspace_3d.png")

    # ----------------------------------------------------------------
    # Seitenansicht: XZ und YZ nebeneinander
    # ----------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    views = [
        (points[:, 0], points[:, 2], "x [m]", "z [m]", "Seitenansicht XZ"),
        (points[:, 1], points[:, 2], "y [m]", "z [m]", "Seitenansicht YZ"),
    ]
    for ax, (xd, yd, xl, yl, title) in zip(axes, views):
        if len(points) > 0:
            ax.scatter(xd, yd, c=yd, cmap="viridis", s=4, alpha=0.3)
        # Motorpositionen als Dreiecke
        for i, mc in enumerate(robot.motors):
            ax.scatter(mc.position[0 if "X" in title else 1],
                       mc.position[2],
                       color=motor_colors[i], s=100, marker="^",
                       label=f"Motor {mc.name}", zorder=5)
        ax.set_xlabel(xl); ax.set_ylabel(yl)
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal")

    plt.suptitle("Arbeitsbereich - Seitenansichten", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{out_dir}/workspace_side.png", dpi=150)
    plt.close()
    print(f"  Gespeichert: {out_dir}/workspace_side.png")


if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    robot  = RobotGeometry("config.txt")
    robot.summary()
    points = compute_workspace(robot)
    plot_workspace(points, robot)
