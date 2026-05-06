from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab

class GeometrieTab(BaseTab):
    def build_left(self):
        ttk.Label(self.left_frame, text="Geometrie").pack(anchor="w")
        ttk.Label(self.left_frame, text="Eingaben").pack(anchor="w")