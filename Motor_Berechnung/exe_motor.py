import numpy as np
import pandas as pd
from pathlib import Path

from config import cfg
from .robot_geometry import RobotGeometry
from .workspace import compute_workspace, plot_workspace
from .inverse_kinematics import compute_kinematics, save_kinematics
from .dynamics import compute_torques, plot_motor_results
from .animation import create_gif


class exeMotor:
    def run(self,d):
        g = cfg.global_cfg
        csv_path = Path(__file__).parent.parent / g.output_dir / g.trajectory_csv

        # 1. Geometrie
        print("=== 1. Lade Geometrie ===")
        robot = RobotGeometry()
        robot.summary()

        # 2. Arbeitsbereich
        print("\n=== 2. Berechne Arbeitsbereich ===")
        pts = compute_workspace(robot)
        plot_workspace(pts, robot)

        # 3. Trajektorie laden
        print(f"\n=== 3. Lade Trajektorie ({g.trajectory_csv}) ===")

        if d is not None:
            print("Versuche Daten aus Pfadberechnung als Variable zu uebergeben, " \
            " ueberspringe CSV-Import.")
            try:
                matrix = np.column_stack([
                    d['t'],
                    d['x'],  d['y'],  d['z'],
                    d['vx'], d['vy'], d['vz'],
                    d['ax'], d['ay'], d['az'],
                    d['jx'], d['jy'], d['jz'],
                    d['tx'], d['ty'], d['tz'],
                    d['nx'], d['ny'], d['nz'],
                    d['bx'], d['by'], d['bz'],
                    d['kappa'],
                    d['ftx'], d['fty'], d['ftz'],
                    d['fnx'], d['fny'], d['fnz'],
                    d['fx'],  d['fy'],  d['fz'],
                ])
                print(f"Geladen aus Variable: {matrix.shape[0]} Zeitschritte, " \
                      f" {matrix.shape[1]} Spalten")
            except (KeyError, TypeError, ValueError) as e:
                print(f"Warnung: Variable ungültig ({e}), falle zurück auf CSV.")
                if not csv_path.exists():
                    print(f"FEHLER: '{csv_path.absolute()}' nicht gefunden.")
                    return
                matrix = np.loadtxt(csv_path, delimiter=",", skiprows=1)
                print(f"Geladen aus CSV: {matrix.shape[0]} Zeitschritte, {matrix.shape[1]} Spalten")
        else:
            if not csv_path.exists():
                print(f"FEHLER: '{csv_path.absolute()}' nicht gefunden.")
                return
            matrix = np.loadtxt(csv_path, delimiter=",", skiprows=1)
            print(f"Geladen aus CSV: {matrix.shape[0]} Zeitschritte, {matrix.shape[1]} Spalten")

        # 4. Inverse Kinematik
        print("\n=== 4. Inverse Kinematik ===")
        kin = compute_kinematics(robot, matrix)
        save_kinematics(kin)

        # 5. Dynamik
        print("\n=== 5. Dynamik (Lagrange) ===")
        torque = compute_torques(robot, kin, matrix)
        kin["torque"] = torque
        save_kinematics(kin)
        plot_motor_results(kin, torque)

        # 6. Animation
        print("\n=== 6. Rendere Animation ===")
        create_gif(robot, kin)

        print("\nFertig! Alle Ausgaben sind im Ordner 'output'.")