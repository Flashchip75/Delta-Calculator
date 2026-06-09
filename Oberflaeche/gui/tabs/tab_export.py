from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import *
from Oberflaeche.help_functions.Export_logic import ExportLogic


class ExportTab(BaseTab):

    def build_left(self):
        ttk.Label(self, text="Export").pack(anchor="w")

        self.logic = ExportLogic(self)

        calc_button = ttk.Button(self, text="Calc All", command=self.logic.calc_all_callback)
        calc_button.pack(fill="x")

        self.csv_line = TextLine(self, "Program File")
        self.csv_line.pack(fill="x")

        self.serial_line = TextLine(self, "Serial Connection")
        self.serial_line.pack(fill="x")

        run_button = ttk.Button(self, text="RUN")
        run_button.pack(fill="x")