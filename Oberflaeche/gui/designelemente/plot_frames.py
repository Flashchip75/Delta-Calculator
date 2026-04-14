import os
import json
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PlotFrame(ttk.Frame):
    def __init__(self, parent, filepath=None, plot_configs=None, default_plot=None, title="Plot"):
        super().__init__(parent)

        self.filepath = filepath or self._get_default_filepath()
        self.plot_configs = plot_configs or {}
        self.default_plot = default_plot
        self.title = title

        self.selected_plot = tk.StringVar()

        self._build_toolbar()
        self._build_canvas()
        self._init_default_plot()

    # ------------------------------------------------------

    # ------------------------------------------------------
    # ------------------- Rechte Plotseite Widget -----------------------------
    # ------------------------------------------------------

    def _get_default_filepath(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        base_dir = os.path.dirname(os.path.dirname(current_dir))

        return os.path.join(base_dir, "delta_robot_testfahrt.json")

    # ------------------------------------------------------

    def _build_toolbar(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=5, pady=5)

        ttk.Label(toolbar, text="Plot:").pack(side="left", padx=(0, 5))

        self.plot_selector = ttk.Combobox(
            toolbar,
            textvariable=self.selected_plot,
            values=list(self.plot_configs.keys()),
            state="readonly"
        )
        self.plot_selector.pack(side="left", fill="x", expand=True)
        self.plot_selector.bind("<<ComboboxSelected>>", self._on_plot_change)

    # ------------------------------------------------------

    def _build_canvas(self):
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ------------------------------------------------------

    def _init_default_plot(self):
        if not self.plot_configs:
            return

        plot_name = self.default_plot or next(iter(self.plot_configs))
        self.selected_plot.set(plot_name)
        self.show_plot(plot_name)

    # ------------------------------------------------------

    def _on_plot_change(self, _event=None):
        self.show_plot(self.selected_plot.get())

    # ------------------------------------------------------

    def show_plot(self, plot_name):
        config = self.plot_configs.get(plot_name)
        if not config:
            return

        self._set_axes(is_3d=config.get("is_3d", False))
        getattr(self, config["method"])()

    # ------------------------------------------------------

    def _set_axes(self, is_3d=False):
        self.figure.clf()
        if is_3d:
            self.ax = self.figure.add_subplot(111, projection="3d")
        else:
            self.ax = self.figure.add_subplot(111)

    # ------------------------------------------------------

    def _load_data(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

# ------------------------------------------------------
#------------------- Plot options -----------------------------
# ------------------------------------------------------

    def plot_path(self):
        data = self._load_data()

        x = [p["x"] for p in data]
        y = [p["y"] for p in data]
        z = [p["z"] for p in data]

        self.ax.plot(x, y, z)
        self.ax.set_title("TCP Path")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.canvas.draw()


    # ------------------------------------------------------

    def plot_vel(self):
        data = self._load_data()

        t = [p["t"] for p in data]
        vx = [p["vx"] for p in data]
        vy = [p["vy"] for p in data]
        vz = [p["vz"] for p in data]

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
        self.ax.text2D(0.3, 0.5, "Geometrie folgt später", transform=self.ax.transAxes)
        self.canvas.draw()