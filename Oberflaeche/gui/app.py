from pathlib import Path
import tkinter as tk
from tkinter import ttk

from Motor_Berechnung.robotconfig import RobotConfig
from Oberflaeche.gui.designelemente.input_tabgroup import InputTabGroup
from Oberflaeche.gui.designelemente.plot_frames import PlotFrame
from Oberflaeche.help_functions.plot_data_loader import PlotDataLoader


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

        plot_area = ttk.Frame(main_frame, padding=10)
        plot_area.grid(row=0, column=1, sticky="nsew")

        self.plot_frame = PlotFrame(parent=plot_area, default_plot="Geometrie")
        self.plot_frame.pack(fill="both", expand=True)

        self.input_tabgroup = InputTabGroup(
            main_frame,
            robot_config=self.robot_config,
            on_show_geometry=self.show_geometry_plot,
            on_results_created=self.update_result_plots_from_csv
        )
        self.input_tabgroup.grid(row=0, column=0, sticky="nsew")

    def show_geometry_plot(self):
        self.plot_frame.update_geometry_plot(self.robot_config)

    def update_result_plots_from_csv(self, csv_path):
        data = PlotDataLoader.load_csv(csv_path)

        x, y, z = PlotDataLoader.get_path_data(data)
        self.plot_frame.set_path_data(x, y, z)

        t, phi_1, phi_2, phi_3 = PlotDataLoader.get_motor_angle_data(data)
        self.plot_frame.set_motor_angle_data(t, phi_1, phi_2, phi_3)