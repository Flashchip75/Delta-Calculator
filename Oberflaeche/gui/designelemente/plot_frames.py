import csv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PlotFrame(ttk.Frame):
    def __init__(self, parent, data_dir, config=None, default_plot="Geometrie"):
        super().__init__(parent)

        self.data_dir = Path(data_dir)
        self.config = config

        self.path_csv = self.data_dir / "roboter_dynamik.csv"
        self.results_csv = self.data_dir / "results.csv"

        self.path_data = []
        self.results_data = []

        self.plot_configs = {
            "Geometrie": {
                "method": self.plot_geometry,
                "is_3d": True
            },
            "Pfad 3D": {
                "method": self.plot_path,
                "is_3d": True
            },
            "Geschwindigkeit": {
                "method": self.plot_velocity,
                "is_3d": False
            },
            "Motorwinkel": {
                "method": self.plot_motor_angles,
                "is_3d": False
            },
        }

        self.default_plot = default_plot

        self.figures = {}
        self.axes = {}
        self.canvases = {}

        self._build_plot_tabs()
        self.load_data()
        self.show_all_plots()
        self._select_default_plot()

    # ------------------------------------------------------
    # GUI-Aufbau
    # ------------------------------------------------------

    def _build_plot_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        for plot_name, config in self.plot_configs.items():
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=plot_name)

            figure = Figure(figsize=(6, 5), dpi=100)

            if config["is_3d"]:
                ax = figure.add_subplot(111, projection="3d")
            else:
                ax = figure.add_subplot(111)

            canvas = FigureCanvasTkAgg(figure, master=tab)
            canvas.get_tk_widget().pack(fill="both", expand=True)

            self.figures[plot_name] = figure
            self.axes[plot_name] = ax
            self.canvases[plot_name] = canvas

    def _select_default_plot(self):
        if self.default_plot in self.plot_configs:
            index = list(self.plot_configs.keys()).index(self.default_plot)
            self.notebook.select(index)

    # ------------------------------------------------------
    # Daten laden
    # ------------------------------------------------------

    def load_data(self):

        try:
            self.path_data = self._load_csv(self.path_csv)
            self.results_data = self._load_csv(self.results_csv)

        except Exception as error:
            messagebox.showerror("Plot-Daten konnten nicht geladen werden", str(error))

    def _load_csv(self, path):
        if not path.exists():
            raise FileNotFoundError(f"Datei nicht gefunden: {path}")

        with open(path, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError(f"CSV hat keine Kopfzeile: {path}")

            return list(reader)

    def _col(self, data, name):
        return [float(row[name]) for row in data]

    # ------------------------------------------------------
    # Plot-Steuerung
    # ------------------------------------------------------

    def show_all_plots(self):
        for plot_name in self.plot_configs:
            self.show_plot(plot_name)

    def show_plot(self, plot_name):
        config = self.plot_configs.get(plot_name)
        if config is None:
            return

        ax = self.axes[plot_name]
        canvas = self.canvases[plot_name]

        ax.clear()

        try:
            config["method"](ax)
        except Exception as error:
            ax.text2D(
                0.05,
                0.5,
                f"Plot konnte nicht erstellt werden:\n{error}",
                transform=ax.transAxes
            )
            print(f"Fehler in Plot '{plot_name}':", error)

        canvas.draw_idle()

    # ------------------------------------------------------
    # Plot-Funktionen
    # ------------------------------------------------------

    def plot_geometry(self, ax):
        if self.config is None:
            ax.text2D(0.1, 0.5, "Keine config übergeben", transform=ax.transAxes)
            return

        motors = self.config.motors

        for motor in motors:
            name = motor["name"]
            x, y, z = motor["position"]

            ax.scatter(x, y, z, label=f"Motor {name}")
            ax.text(x, y, z, name)

        ax.set_title("Geometrie")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.legend()


    def plot_path(self, ax):
        x = self._col(self.path_data, "x")
        y = self._col(self.path_data, "y")
        z = self._col(self.path_data, "z")

        ax.plot(x, y, z)

        ax.set_title("3D-Pfad")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")

    def plot_velocity(self, ax):
        t = self._col(self.path_data, "t")

        ax.plot(t, self._col(self.path_data, "vx"), label="vx")
        ax.plot(t, self._col(self.path_data, "vy"), label="vy")
        ax.plot(t, self._col(self.path_data, "vz"), label="vz")

        ax.set_title("Geschwindigkeit")
        ax.set_xlabel("t")
        ax.set_ylabel("v")
        ax.legend()
        ax.grid(True)

    def plot_motor_angles(self, ax):
        t = self._col(self.results_data, "t")

        ax.plot(t, self._col(self.results_data, "phi_1"), label="phi_1")
        ax.plot(t, self._col(self.results_data, "phi_2"), label="phi_2")
        ax.plot(t, self._col(self.results_data, "phi_3"), label="phi_3")

        ax.set_title("Motorwinkel")
        ax.set_xlabel("t")
        ax.set_ylabel("phi")
        ax.legend()
        ax.grid(True)