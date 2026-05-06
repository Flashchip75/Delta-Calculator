import os
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PlotFrame(ttk.Frame):
    def __init__(self, parent, plot_configs=None, default_plot=None, title="Plot", kin_struct=None):
        super().__init__(parent)

        if kin_struct is None:
            raise ValueError("KinStruct fehlt! Übergib kin_struct beim Erstellen des PlotFrames.")

        self.kin_struct = kin_struct
        self.plot_configs = plot_configs or {}
        self.default_plot = default_plot
        self.title = title

        self.figures = {}
        self.axes = {}
        self.canvases = {}

        self._build_plot_tabs()
        self._init_plots()

    # ------------------------------------------------------

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

    def _init_plots(self):
        for plot_name in self.plot_configs:
            self.show_plot(plot_name)

        if self.default_plot in self.plot_configs:
            index = list(self.plot_configs.keys()).index(self.default_plot)
            self.notebook.select(index)

    # ------------------------------------------------------

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

    def refresh_all(self):
        for plot_name in self.plot_configs:
            self.show_plot(plot_name)

    # ------------------------------------------------------

    def _load_data(self):
        if self.kin_struct is None:
            raise ValueError("Kein KinStruct vorhanden!")

        return self.kin_struct.trajectory

    # ------------------------------------------------------
    # Plot options
    # ------------------------------------------------------

    def plot_path(self):
        data = self._load_data()

        x = [p.x for p in data]
        y = [p.y for p in data]
        z = [p.z for p in data]

        self.ax.plot(x, y, z)
        self.ax.set_title("TCP Path")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.canvas.draw()

    # ------------------------------------------------------

    def plot_vel(self):
        data = self._load_data()

        t = [p.t for p in data]
        vx = [p.vx for p in data]
        vy = [p.vy for p in data]
        vz = [p.vz for p in data]

        self.ax.plot(t, vx, label="vx")
        self.ax.plot(t, vy, label="vy")
        self.ax.plot(t, vz, label="vz")

        self.ax.set_title("Geschwindigkeit über Zeit")
        self.ax.set_xlabel("t")
        self.ax.set_ylabel("v")
        self.ax.legend()
        self.canvas.draw()

    # ------------------------------------------------------

    def plot_geometry(self):
        self.ax.set_title("Geometrie Plot")
        self.ax.text2D(
            0.3,
            0.5,
            "Geometrie folgt später",
            transform=self.ax.transAxes
        )
        self.canvas.draw()