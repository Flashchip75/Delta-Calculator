from tkinter import ttk

from Oberflaeche.gui.tabs.tab_geometrie import GeometrieTab
from Oberflaeche.gui.tabs.tab_pathdef import PathDefTab
from Oberflaeche.gui.tabs.tab_export import ExportTab

# TODO: Force Update on Tab change for MAC
# Tab change get's stuck while hovering the mouse over the Tabs, nto showing the new content until you move the curser off it.
# Probably able to catch a click event and force the update on that.

class InputTabGroup(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_geometrie = GeometrieTab(self.notebook)
        self.tab_pathdef = PathDefTab(self.notebook)
        self.tab_export = ExportTab(self.notebook)

        self.notebook.add(self.tab_geometrie, text="Geometrie")
        self.notebook.add(self.tab_pathdef, text="Path Definition")
        self.notebook.add(self.tab_export, text="Export")