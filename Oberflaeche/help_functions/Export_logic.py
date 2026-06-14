from pathlib import Path

from Motor_Berechnung.trajectory import Trajectory
from Motor_Berechnung.kinematics import KinematicsSolver
from Motor_Berechnung.dynamics import DynamicsSolver
from Motor_Berechnung.export import DataExporter
from Oberflaeche.help_functions.arduino_runner import ArduinoRunner


class ExportLogic:
    def __init__(self, export_tab, robot_config, on_results_created=None):
        self.export_tab = export_tab
        self.robot_config = robot_config
        self.on_results_created = on_results_created
        self.results_csv_path = None
        self.arduino_runner = None

    def calc_all_callback(self):
        ROOT = Path(__file__).resolve().parents[2]
        robot_config = self.robot_config
        trajectory_path = ROOT / robot_config.global_data["trajectory_csv"]

        trajectory = Trajectory(trajectory_path)

        kinematics_solver = KinematicsSolver(robot_config)
        all_results = kinematics_solver.solve_trajectory(trajectory.path_points)

        dynamics_solver = DynamicsSolver(robot_config, trajectory)
        exporter = DataExporter(trajectory, dynamics_solver)

        filepath = exporter.export_results_to_csv(all_results, filename="results.csv")

        self.results_csv_path = Path(filepath)
        self.write_csv_path_to_line()

        if self.on_results_created is not None:
            self.on_results_created(self.results_csv_path)

    def run_callback(self):
        results_path = Path(self.export_tab.csv_line.get())

        if not results_path.exists():
            print(f"CSV-Datei nicht gefunden: {results_path}")
            return

        self.results_csv_path = results_path
        port = self.export_tab.serial_line.get()

        self.arduino_runner = ArduinoRunner(port=port, baudrate=115200, slowdown_factor=1, on_log=self.log_from_arduino)
        self.arduino_runner.start(results_path)

    def stop_callback(self):
        if self.arduino_runner is not None:
            self.arduino_runner.stop()

    def write_csv_path_to_line(self):
        if self.results_csv_path is None:
            return

        self.export_tab.csv_line.input.delete(0, "end")
        self.export_tab.csv_line.input.insert(0, str(self.results_csv_path))

    def log_from_arduino(self, message):
        self.export_tab.after(0, lambda: print(message))

    def write_program_file_path(self, value):
        self.results_csv_path = Path(value)

    def program_file_changed_callback(self):
        if self.results_csv_path is None:
            return

        if not self.results_csv_path.exists():
            print(f"CSV-Datei nicht gefunden: {self.results_csv_path}")
            return

        if self.on_results_created is not None:
            self.on_results_created(self.results_csv_path)