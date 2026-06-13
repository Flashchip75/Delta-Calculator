from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab


class GeometrieTab(BaseTab):

    def __init__(self, parent):
        self.plot_frame = None
        self.robot_config = None
        super().__init__(parent)

    def build_left(self):
        ttk.Label(self, text="Geometrie").pack(anchor="w")
        ttk.Label(self, text="Eingaben").pack(anchor="w")

        ttk.Button(
            self,
            text="Geometrie anzeigen",
            command=self.show_geometry_callback
        ).pack(fill="x", pady=5)

    def show_geometry_callback(self):
        if self.plot_frame is not None and self.robot_config is not None:
            self.plot_frame.update_geometry_plot(
                self.robot_config
            )