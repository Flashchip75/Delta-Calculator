from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab


class GeometrieTab(BaseTab):
    def __init__(self, parent, on_show_geometry=None):
        self.on_show_geometry = on_show_geometry
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
        if self.on_show_geometry is not None:
            self.on_show_geometry()