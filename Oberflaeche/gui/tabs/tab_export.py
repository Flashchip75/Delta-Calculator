import os
from tkinter import ttk
import tkinter as tk

from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.plot_frames import PlotFrame

# Tab zum export in Arduino und zur überprüfung der Leistung und Fahrt
# Beispielplots: Was wollen wir abbilden können?
# Den switch zwischen den tabs irgendwie ausgliedern
class ExportTab(BaseTab):

    def build_left(self):
        ttk.Label(self.left_frame, text="Export", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

        # Auswahl Plot-Typ
        ttk.Label(self.left_frame, text="Plot auswählen:").pack(anchor="w")

        self.plot_choice = tk.StringVar(value="Path")

        self.combo = ttk.Combobox(
            self.left_frame,
            textvariable=self.plot_choice,
            values=["Path", "Velocity"],
            state="readonly"
        )
        self.combo.pack(fill="x", pady=5)

        # Button zum Aktualisieren
        ttk.Button(
            self.left_frame,
            text="Plot anzeigen",
            command=self.update_plot
        ).pack(fill="x", pady=10)

    def build_right(self):
        self.plot_frame = PlotFrame(self.right_frame, is_3d=True)
        self.plot_frame.pack(fill="both", expand=True)

    def update_plot(self):
        # Pfad zur JSON
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        filepath = os.path.join(script_dir, "delta_robot_testfahrt.json")

        choice = self.plot_choice.get()

        if choice == "Path":
            # 3D Plot
            self.plot_frame.figure.clf()
            self.plot_frame.ax = self.plot_frame.figure.add_subplot(111, projection="3d")
            self.plot_frame.plot_path(filepath)

        elif choice == "Velocity":
            # 2D Plot
            self.plot_frame.figure.clf()
            self.plot_frame.ax = self.plot_frame.figure.add_subplot(111)
            self.plot_frame.plot_vel(filepath)