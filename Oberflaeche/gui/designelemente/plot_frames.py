import os
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PlotFrame(ttk.Frame):
    def __init__(self, parent, plot_configs=None, default_plot=None,
                 title="Plot", kin_struct=None, geo_struct=None, path_struct=None):

        super().__init__(parent)

# Datahandling anpassen auf Klassen und Objektlogik
        self.kin_struct = kin_struct
        self.geo_struct = geo_struct
        self.path_struct = path_struct
        self.plot_configs = plot_configs or {}
        self.default_plot = default_plot
        self.title = title

        self.figures = {}
        self.axes = {}
        self.canvases = {}

        self._build_plot_tabs()
        self._init_plots()

    # ------------------------------------------------------

# Aufbau der Tabstruktur für Widget
    def _build_plot_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        for plot_name, config in self.plot_configs.items():
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=plot_name)

            figure = Figure(figsize=(6, 5), dpi=100)

            if config.get("is_3d", False):
                ax = figure.add_subplot(111, projection="3d")
            else:
                ax = figure.add_subplot(111)

            canvas = FigureCanvasTkAgg(figure, master=tab)
            canvas.get_tk_widget().pack(fill="both", expand=True)

            self.figures[plot_name] = figure
            self.axes[plot_name] = ax
            self.canvases[plot_name] = canvas

    # ------------------------------------------------------

# initialisierung der Plots
    def _init_plots(self):
        for plot_name in self.plot_configs:
            self.show_plot(plot_name)

        if self.default_plot in self.plot_configs:
            index = list(self.plot_configs.keys()).index(self.default_plot)
            self.notebook.select(index)

    # ------------------------------------------------------

# Anzeigen des gewählten Plots
    def show_plot(self, plot_name):
        config = self.plot_configs.get(plot_name)
        if not config:
            return

        self.figure = self.figures[plot_name]
        self.ax = self.axes[plot_name]
        self.canvas = self.canvases[plot_name]

        self.ax.clear()

        getattr(self, config["method"])()

    # ------------------------------------------------------

# Aktualisieren aller Plots
    def refresh_all(self):
        for plot_name in self.plot_configs:
            self.show_plot(plot_name)

    # ------------------------------------------------------

# Daten laden aus struktur mit zukünftige Datahandling über Klasse
    def _load_data(self):
        if self.kin_struct is None:
            raise ValueError("Kein KinStruct vorhanden!")

        return self.kin_struct.trajectory

    # ------------------------------------------------------
    # Plot options
    # ------------------------------------------------------

# Plottet pfad auf 3d Axis
    def plot_path(self):
        data = self.path_struct.trajectory

        x = [p.x for p in data]
        y = [p.y for p in data]
        z = [p.z for p in data]

        self.ax.plot(x, y, z)
        self.canvas.draw()

    # ------------------------------------------------------

# plotte geschwindigkeit auf 2d plot
    def plot_vel(self):
        data = self.kin_struct.trajectory

        t = [p.t for p in data]
        vx = [p.vx for p in data]
        vy = [p.vy for p in data]
        vz = [p.vz for p in data]

        self.ax.plot(t, vx)
        self.ax.plot(t, vy)
        self.ax.plot(t, vz)

        self.canvas.draw()

    # ------------------------------------------------------

# Zeigt provisorisch die Position der Motoren im Raum
    def plot_geometry(self):
        geo = self.geo_struct

        self.ax.set_title("Geometrie")

        for name, motor in geo.motors.items():
            x, y, z = motor.position
            self.ax.scatter(x, y, z, label=name)

        self.ax.legend()
        self.canvas.draw()
