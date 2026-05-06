import tkinter as tk
from tkinter import ttk

from Oberflaeche.gui.tabs.tab_geometrie import GeometrieTab
from Oberflaeche.gui.tabs.tab_pathdef import PathDefTab
from Oberflaeche.gui.tabs.tab_export import ExportTab
from Oberflaeche.gui.designelemente.plot_frames import PlotFrame
from Oberflaeche.help_functions.struct_kin_data import write_kin_struct


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Delta Roboter GUI")
        self.geometry("1200x700")

        self.kin_struct = write_kin_struct("delta_robot_testfahrt.json")

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky="nsew")

        plot_area = ttk.Frame(main_frame, padding=10)
        plot_area.grid(row=0, column=1, sticky="nsew")

        self.tab_geometrie = GeometrieTab(notebook)
        self.tab_pathdef = PathDefTab(notebook)
        self.tab_export = ExportTab(notebook)

        notebook.add(self.tab_geometrie, text="Geometrie")
        notebook.add(self.tab_pathdef, text="Path Definition")
        notebook.add(self.tab_export, text="Export")

        self.plot_frame = PlotFrame(
            plot_area,
            plot_configs={
                "Geometrie": {"method": "plot_geometry", "is_3d": True},
                "Path": {"method": "plot_path", "is_3d": True},
                "Velocity": {"method": "plot_vel", "is_3d": False},
            },
            default_plot="Geometrie",
            title="Plot",
            kin_struct=self.kin_struct,
        )
        self.plot_frame.pack(fill="both", expand=True)