from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab

# Eingabetab links für Geometrie

class GeometrieTab(BaseTab):
    def build_left(self):
        ttk.Label(self, text="Geometrie").pack(anchor="w")
        ttk.Label(self, text="Eingaben").pack(anchor="w")
