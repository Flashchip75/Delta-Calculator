from robotconfig import robot_config
from trajectory import Trajectory
from kinematics import KinematicsSolver
from dynamics import DynamicsSolver
from visualization import Visualizer
from export import DataExporter
from pathlib import Path

def main():
    ROOT = Path(__file__).resolve().parent.parent

    # 1. Konfiguration laden
    # print(robot_config.global_data["mass_kg"])     # Auslesebeispiel

    trajectory_path = ROOT / robot_config.global_data["trajectory_csv"]

    # 2. Trajektorie laden
    trajectory = Trajectory(trajectory_path)  # Ließt Trajectory Datei aus, Argument für Funktion ist der Datei Pfad der csv. (bei Mark der relative, bei Annika der absolute)

    # 3. Inverse Kinematik berechnen
    kinematics_solver = KinematicsSolver(robot_config)

    #workspace_points = kinematics_solver.plot_workspace(show_unreachable=False)    # Workspace Plot

    all_results = kinematics_solver.solve_trajectory(trajectory.path_points)        # Berechnet Motorwinkel für alle Pfadpunkte
    kinematics_solver.print_reachable_summary(trajectory.path_points, all_results)
    kinematics_solver.print_unreachable_points(trajectory.path_points, all_results)
    #kinematics_solver.debug_plot_offset_trajectory(trajectory.path_points)

    # 4. Dynamik Solver initialisieren (für plot_motor_angles und export)
    dynamics_solver = DynamicsSolver(robot_config, trajectory)      # Dynamics Lib zur berechnung von omega, alpah, T

    # 5. Export
    exporter = DataExporter(trajectory, dynamics_solver)                
    exporter.export_results_to_csv(all_results, filename="results.csv") # CSV Export
    
    # 6. Visualisierung
    visualizer = Visualizer(robot_config, trajectory, dynamics_solver)
    
    visualizer.plot_motor_angles(all_results)
    visualizer.save_motor_angles_plot(all_results, filename="motor_angles.png")

    visualizer.animate_reachable_poses(all_results,save_gif=True,gif_name="delta_robot_animation.gif")

    

if __name__ == "__main__":
    main()
