from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import *
from Oberflaeche.help_functions.Export_logic import ExportLogic
from Oberflaeche.help_functions.arduino_runner import ArduinoRunner



class ExportTab(BaseTab):
    def __init__(self, parent, robot_config, on_results_created=None):
        self.robot_config = robot_config
        self.on_results_created = on_results_created
        self.logic = None
        self.arduino_runner = None
        super().__init__(parent)

    def build_left(self):
        ttk.Label(self, text="Export").pack(anchor="w")

        self.logic = ExportLogic(
            self,
            robot_config=self.robot_config,
            on_results_created=self.on_results_created
        )

        ttk.Button(self, text="Calc All", command=self.logic.calc_all_callback).pack(fill="x")

        self.csv_line = TextLine(self, "Program File", default="results.csv")
        self.csv_line.pack(fill="x")

        self.serial_line = TextLine(self, "Serial Connection", default="/dev/tty.usbserial-110")
        self.serial_line.pack(fill="x")

        ttk.Button(self, text="RUN", command=self.run_callback).pack(fill="x")
        ttk.Button(self, text="STOP", command=self.stop_callback).pack(fill="x")

    def run_callback(self):
        results_path = self.logic.results_csv_path

        if results_path is None:
            print("Keine results.csv vorhanden. Bitte zuerst Calc All ausführen.")
            return

        self.arduino_runner = ArduinoRunner(
            port=self.serial_line.get(),
            baudrate=115200,
            slowdown_factor=1,
            on_log=self.log_from_arduino
        )

        self.arduino_runner.start(results_path)

    def stop_callback(self):
        if self.arduino_runner is not None:
            self.arduino_runner.stop()

    def log_from_arduino(self, message):
        self.after(0, lambda: print(message))