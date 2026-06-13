from tkinter import ttk

from Oberflaeche.gui.tabs.tab_geometrie import GeometrieTab
from Oberflaeche.gui.tabs.tab_pathdef import PathDefTab
from Oberflaeche.gui.tabs.tab_export import ExportTab


class InputTabGroup(ttk.Frame):
    def __init__(self, parent, robot_config, on_show_geometry=None, on_results_created=None):
        super().__init__(parent)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_geometrie = GeometrieTab(
            self.notebook,
            on_show_geometry=on_show_geometry
        )

        self.tab_pathdef = PathDefTab(self.notebook)

        self.tab_export = ExportTab(
            self.notebook,
            robot_config=robot_config,
            on_results_created=on_results_created
        )

        self.notebook.add(self.tab_geometrie, text="Geometrie")
        self.notebook.add(self.tab_pathdef, text="Path Definition")
        self.notebook.add(self.tab_export, text="Export")