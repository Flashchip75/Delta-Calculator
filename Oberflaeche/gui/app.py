from pathlib import Path
import tkinter as tk
from tkinter import ttk

from Motor_Berechnung.robotconfig import RobotConfig

from Oberflaeche.gui.designelemente.input_tabgroup import InputTabGroup
from Oberflaeche.gui.designelemente.plot_frames import PlotFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Delta Roboter GUI")
        self.geometry("1200x700")

        self.project_root = Path(__file__).resolve().parents[2]

        self.robot_config = RobotConfig()

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # Eingaben links
        self.input_tabgroup = InputTabGroup(main_frame)
        self.input_tabgroup.grid(row=0, column=0, sticky="nsew")

        # Plotbereich rechts
        plot_area = ttk.Frame(main_frame, padding=10)
        plot_area.grid(row=0, column=1, sticky="nsew")

        self.plot_frame = PlotFrame(
            parent=plot_area,
            default_plot="Geometrie"
        )

        self.plot_frame.pack(fill="both", expand=True)
        self.input_tabgroup.tab_geometrie.plot_frame = self.plot_frame
        self.input_tabgroup.tab_geometrie.robot_config = self.robot_config
        self.input_tabgroup.tab_export.plot_frame = self.plot_frame