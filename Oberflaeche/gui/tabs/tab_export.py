from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import *
from Oberflaeche.help_functions.Export_logic import ExportLogic


class ExportTab(BaseTab):
    def __init__(self, parent, robot_config, on_results_created=None):
        self.robot_config = robot_config
        self.on_results_created = on_results_created
        self.logic = None
        super().__init__(parent)

    def build_left(self):
        ttk.Label(self, text="Export").pack(anchor="w")

        self.logic = ExportLogic(self, robot_config=self.robot_config, on_results_created=self.on_results_created)

        ttk.Button(self, text="Calc All", command=self.logic.calc_all_callback).pack(fill="x")

        self.csv_line = TextLine(self, "Program File", default="results.csv",
                                 writePropertiesFunction=self.logic.write_program_file_path,
                                 onLineChangedFunction=self.logic.program_file_changed_callback)
        self.csv_line.pack(fill="x")

        self.serial_line = TextLine(self, "Serial Connection", default="/dev/tty.usbserial-110")
        self.serial_line.pack(fill="x")

        ttk.Button(self, text="RUN", command=self.logic.run_callback).pack(fill="x")
        ttk.Button(self, text="STOP", command=self.logic.stop_callback).pack(fill="x")