"""
run_all.py
==========
Steuerungsscript. Führt alle Module der Reihe nach aus.
"""

import os
import numpy as np
from robot_geometry import RobotGeometry

# Ins Script-Verzeichnis wechseln
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=== 1. Lade Geometrie ===")
    robot = RobotGeometry() # Nutzt standardmäßig config.json
    robot.summary()

    print("\n=== 2. Berechne Arbeitsbereich ===")
    from workspace import compute_workspace, plot_workspace
    pts = compute_workspace(robot)
    plot_workspace(pts, robot)

    print(f"\n=== 3. Lade Trajektorie ({robot.trajectory_csv}) ===")
    if not os.path.exists(robot.trajectory_csv):
        print(f"FEHLER: Die Datei '{robot.trajectory_csv}' wurde nicht gefunden.")
        return
    
    # Lade CSV (skiprows=1 überspringt den Header)
    matrix = np.loadtxt(robot.trajectory_csv, delimiter=",", skiprows=1)
    print(f"  Erfolgreich geladen: {matrix.shape[0]} Zeitschritte, {matrix.shape[1]} Spalten")

    print("\n=== 4. Inverse Kinematik ===")
    from inverse_kinematics import compute_kinematics, save_kinematics
    kin = compute_kinematics(robot, matrix)
    save_kinematics(kin)

    print("\n=== 5. Dynamik (Lagrange) ===")
    from dynamics import compute_torques, plot_motor_results
    torque = compute_torques(robot, kin, matrix)
    kin["torque"] = torque
    save_kinematics(kin)
    plot_motor_results(kin, torque)

    print("\n=== 6. Rendere Animation ===")
    from animation import create_gif
    create_gif(robot, kin)
    
    print("\nFertig! Alle Ausgaben sind im Ordner 'output'.")

if __name__ == "__main__":
    main()