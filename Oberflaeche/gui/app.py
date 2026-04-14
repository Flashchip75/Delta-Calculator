import tkinter as tk
from tkinter import ttk

from Oberflaeche.gui.tabs.tab_geometrie import GeometrieTab
from Oberflaeche.gui.tabs.tab_pathdef import PathDefTab
from Oberflaeche.gui.tabs.tab_export import ExportTab

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Delta Roboter GUI")
        self.geometry("1200x700")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.tab_geometrie = GeometrieTab(notebook)
        self.tab_pathdef = PathDefTab(notebook)
        self.tab_export = ExportTab(notebook)

        notebook.add(self.tab_geometrie, text="Geometrie")
        notebook.add(self.tab_pathdef, text="Path Definition")
        notebook.add(self.tab_export, text="Export")


# Note to self vor git
# Extentions matlib
# Jason file path ändern
# robot_controller löschen und ersetzten
# main aufruf überlegen wo


