from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json


# Klasse beinhaltet Designelemente die auf die rechte Fensterseite gebased werden können

class PlotFrame(ttk.Frame):
    # Konstruktor Erstellt Plotfigure mit Achen
    def __init__(self, parent, is_3d=False, title="Plot"):
        super().__init__(parent)

        self.figure = Figure(figsize=(6, 5), dpi=100)
        # Fallunterscheidung für Figures erstellen in 3D oder 2D
        if is_3d:
            self.ax = self.figure.add_subplot(111, projection="3d")
        else:
            self.ax = self.figure.add_subplot(111)

        self.ax.set_title(title)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    import json

    # Plottet den Pfad in die 3D figure
    def plot_path(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        x = [p["x"] for p in data]
        y = [p["y"] for p in data]
        z = [p["z"] for p in data]

        self.ax.clear()
        self.ax.plot(x, y, z)

        self.ax.set_title("TCP Path")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")

        self.canvas.draw()

    # plottet die TCP Geschwindigkeit über zeit in x,y und z richtung
    def plot_vel(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        t  = [p["t"] for p in data]
        vx = [p["vx"] for p in data]
        vy = [p["vy"] for p in data]
        vz = [p["vz"] for p in data]

        self.ax.clear()
        self.ax.plot(t, vx, label="vx")
        self.ax.plot(t, vy, label="vy")
        self.ax.plot(t, vz, label="vz")

        self.ax.set_title("Geschwindigkeit über Zeit")
        self.ax.set_xlabel("t")
        self.ax.set_ylabel("v")

        self.ax.legend()

        self.canvas.draw()