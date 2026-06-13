from pathlib import Path

from Motor_Berechnung.robotconfig import RobotConfig
from Motor_Berechnung.trajectory import Trajectory
from Motor_Berechnung.kinematics import KinematicsSolver
from Motor_Berechnung.dynamics import DynamicsSolver
from Motor_Berechnung.export import DataExporter
from Oberflaeche.gui.designelemente.plot_frames import PlotFrame


class ExportLogic:

    def __init__(self, tab, on_results_created=None):
        self.tab = tab
        self.on_results_created = on_results_created
        self.results_csv_path = None

    def calc_all_callback(self):

        ROOT = Path(__file__).resolve().parents[2]
        robot_config = RobotConfig() #Später schon erstellt
        trajectory_path = ROOT / robot_config.global_data["trajectory_csv"] # Pfad korrigieren
        trajectory = Trajectory(trajectory_path)

        kinematics_solver = KinematicsSolver(robot_config)
        all_results = kinematics_solver.solve_trajectory(trajectory.path_points)

        dynamics_solver = DynamicsSolver(robot_config, trajectory)

        exporter = DataExporter(trajectory, dynamics_solver)
        filepath = exporter.export_results_to_csv(
            all_results,
            filename="results.csv"
        )

        self.results_csv_path = Path(filepath)
        self.write_csv_path_to_line()

        if self.on_results_created is not None:
            self.on_results_created(self.results_csv_path)

    # TODO: Grafik anzeigen callback
    # TODO: Prüfen ob Path vorhanden


    def write_csv_path_to_line(self):
        if self.results_csv_path is None:
            return

        self.tab.csv_line.input.delete(0, "end")
        self.tab.csv_line.input.insert(0, str(self.results_csv_path))
    # TODO: Funktion zum Pfad in line einfügen