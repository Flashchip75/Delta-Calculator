from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.plot_frames import PlotFrame

# Tab für die eingabe der Geometrie hier vorläufig
class GeometrieTab(BaseTab):
    def build_left(self):
        ttk.Label(self.left_frame, text="Geometrie").pack(anchor="w")
        ttk.Label(self.left_frame, text="Eingaben").pack(anchor="w")

    def build_right(self):
        self.plot_frame = PlotFrame(self.right_frame, is_3d=True, title="Geometrie Plot")
        self.plot_frame.pack(fill="both", expand=True)