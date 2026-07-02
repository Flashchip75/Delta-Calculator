from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab

# Eingabetab Links für den Export an Arduino

class ExportTab(BaseTab):
    def build_left(self):
        ttk.Label(self, text="Export").pack(anchor="w")
        ttk.Label(self, text="Eingaben").pack(anchor="w")
