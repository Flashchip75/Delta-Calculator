from pathlib import Path

from Motor_Berechnung.trajectory import Trajectory
from Motor_Berechnung.kinematics import KinematicsSolver
from Motor_Berechnung.dynamics import DynamicsSolver
from Motor_Berechnung.export import DataExporter
from Oberflaeche.help_functions.arduino_runner import ArduinoRunner


# Verbindet Export-Tab, CSV-Erzeugung und ArduinoRunner.
# Der Tab bleibt reine Oberfläche, diese Klasse steuert den Ablauf.
class ExportLogic:
    def __init__(self, export_tab, robot_config, on_results_created=None):
        self.export_tab = export_tab
        self.robot_config = robot_config
        self.on_results_created = on_results_created
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
        self.set_program_file_path(filepath)

        if self.on_results_created is not None:
            self.on_results_created(Path(filepath))

    def run_callback(self):
        results_path = self.get_program_file_path()

        if not results_path.exists():
            print(f"CSV-Datei nicht gefunden: {results_path}")
            return

        port = self.export_tab.serial_line.get()

        self.arduino_runner = ArduinoRunner(port=port, baudrate=115200, slowdown_factor=1, on_log=self.log_from_arduino)
        self.arduino_runner.start(results_path)

    def stop_callback(self):
        if self.arduino_runner is not None:
            self.arduino_runner.stop()

    def get_program_file_path(self):
        return Path(self.export_tab.csv_line.get())

    def set_program_file_path(self, path):
        self.export_tab.csv_line.input.delete(0, "end")
        self.export_tab.csv_line.input.insert(0, str(Path(path)))

    def write_program_file_path(self, value):
        # Wird von TextLine aufgerufen.
        # Keine Speicherung nötig: Program File ist die aktuelle Quelle.
        pass

    def program_file_changed_callback(self):
        csv_path = self.get_program_file_path()

        if not csv_path.exists():
            print(f"CSV-Datei nicht gefunden: {csv_path}")
            return

        if self.on_results_created is not None:
            self.on_results_created(csv_path)

    def log_from_arduino(self, message):
        self.export_tab.after(0, lambda: print(message))