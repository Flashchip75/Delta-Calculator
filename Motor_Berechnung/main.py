from robotconfig import RobotConfig
from trajectory import Trajectory
from kinematics import KinematicsSolver
from dynamics import DynamicsSolver
from visualization import Visualizer
from export import DataExporter

def main():
    # 1. Konfiguration laden
    robot_config = RobotConfig("config.json")

    # 2. Trajektorie laden
    trajectory = Trajectory(robot_config.global_data["trajectory_csv"])

    # 3. Inverse Kinematik berechnen
    kinematics_solver = KinematicsSolver(robot_config)
    all_results = kinematics_solver.solve_trajectory(trajectory.path_points)

    kinematics_solver.print_reachable_summary(trajectory.path_points, all_results)
    kinematics_solver.print_unreachable_points(trajectory.path_points, all_results)

    # 4. Dynamik Solver initialisieren (für plot_motor_angles und export)
    dynamics_solver = DynamicsSolver(robot_config, trajectory)

    # 5. Export
    exporter = DataExporter(trajectory, dynamics_solver)
    exporter.export_results_to_csv(all_results, filename="results.csv")

    # 6. Visualisierung
    visualizer = Visualizer(robot_config, trajectory, dynamics_solver)
    
    visualizer.plot_motor_angles(all_results)
    visualizer.save_motor_angles_plot(all_results, filename="motor_angles.png")

    visualizer.animate_reachable_poses(all_results,save_gif=True,gif_name="delta_robot_animation.gif")

    

if __name__ == "__main__":
    main()
