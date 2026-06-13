import csv
import math
from pathlib import Path
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PlotFrame(ttk.Frame):
    def __init__(self, parent, default_plot="Geometrie"):
        super().__init__(parent)

        self.config = None
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
            "Motorwinkel": {
                "method": self.plot_motor_angles,
                "is_3d": False
            }
        }

        self.default_plot = default_plot

        self.figures = {}
        self.axes = {}
        self.canvases = {}

        self._build_plot_tabs()
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
    # Callbacks
    # ------------------------------------------------------

    def update_geometry_plot(self, config):
        self.config = config
        self.show_plot("Geometrie")

    def update_path_plot(self, csv_path):
        self.path_data = self._load_csv(csv_path)
        self.show_plot("Pfad 3D")

    def update_motor_angle_plot(self, csv_path):
        self.results_data = self._load_csv(csv_path)
        self.show_plot("Motorwinkel")

    # ------------------------------------------------------
    # CSV Hilfsfunktionen
    # ------------------------------------------------------

    def _load_csv(self, csv_path):
        with open(Path(csv_path), "r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))

    def _col(self, data, name):
        return [float(row[name]) for row in data]

    # ------------------------------------------------------
    # Plot-Steuerung
    # ------------------------------------------------------

    def show_plot(self, plot_name):
        config = self.plot_configs.get(plot_name)

        if config is None:
            return

        ax = self.axes[plot_name]
        canvas = self.canvases[plot_name]

        ax.clear()

        config["method"](ax)

        canvas.draw_idle()

    # ------------------------------------------------------
    # Plot-Funktionen
    # ------------------------------------------------------

    def plot_geometry(self, ax):
        if self.config is None:
            return

        motors = self.config.motors
        bases = [motor["position"] for motor in motors]

        center_x = sum(p[0] for p in bases) / len(bases)
        center_y = sum(p[1] for p in bases) / len(bases)

        upper_angle_deg = 135
        upper_angle = math.radians(upper_angle_deg)

        elbows = []

        for motor in motors:
            base = motor["position"]
            upper_length = motor["upper_length"]

            radial = [center_x - base[0], center_y - base[1]]
            radial_len = (radial[0] ** 2 + radial[1] ** 2) ** 0.5

            if radial_len == 0:
                continue

            radial_unit = [radial[0] / radial_len, radial[1] / radial_len]

            elbow = [
                base[0] + radial_unit[0] * upper_length * math.cos(upper_angle),
                base[1] + radial_unit[1] * upper_length * math.cos(upper_angle),
                base[2] - upper_length * math.sin(upper_angle),
            ]

            elbows.append((motor, elbow))

        avg_lower_length = sum(m["lower_length"] for m in motors) / len(motors)

        avg_xy_dist = sum(
            ((elbow[0] - center_x) ** 2 + (elbow[1] - center_y) ** 2) ** 0.5
            for _, elbow in elbows
        ) / len(elbows)

        tcp_z = elbows[0][1][2] - max(avg_lower_length ** 2 - avg_xy_dist ** 2, 0) ** 0.5
        tcp = [center_x, center_y, tcp_z]

        ax.scatter(tcp[0], tcp[1], tcp[2], s=70, label="TCP")
        ax.text(tcp[0], tcp[1], tcp[2], "TCP")

        for motor, elbow in elbows:
            name = motor["name"]
            base = motor["position"]

            ax.scatter(base[0], base[1], base[2], s=50, label=f"Motor {name}")
            ax.text(base[0], base[1], base[2], name)

            ax.scatter(elbow[0], elbow[1], elbow[2], s=35)
            ax.text(elbow[0], elbow[1], elbow[2], f"E{name}")

            ax.plot(
                [base[0], elbow[0]],
                [base[1], elbow[1]],
                [base[2], elbow[2]],
                linewidth=2
            )

            ax.plot(
                [elbow[0], tcp[0]],
                [elbow[1], tcp[1]],
                [elbow[2], tcp[2]],
                linestyle="--",
                linewidth=2
            )

        ax.set_title("Geometrie")
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        ax.set_zlabel("z [m]")
        ax.legend()

    def plot_path(self, ax):
        if not self.path_data:
            return

        x = self._col(self.path_data, "x")
        y = self._col(self.path_data, "y")
        z = self._col(self.path_data, "z")

        ax.plot(x, y, z)

        ax.set_title("Pfad")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")

    def plot_motor_angles(self, ax):
        if not self.results_data:
            return

        t = self._col(self.results_data, "t")

        ax.plot(t, self._col(self.results_data, "phi_1"), label="phi_1")
        ax.plot(t, self._col(self.results_data, "phi_2"), label="phi_2")
        ax.plot(t, self._col(self.results_data, "phi_3"), label="phi_3")

        ax.set_title("Motorwinkel")
        ax.set_xlabel("t")
        ax.set_ylabel("phi")
        ax.legend()
        ax.grid(True)