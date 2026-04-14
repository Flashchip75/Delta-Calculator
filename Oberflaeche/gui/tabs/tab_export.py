from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.plot_frames import PlotFrame


class ExportTab(BaseTab):
    def build_left(self):
        ttk.Label(self.left_frame, text="Export").pack(anchor="w")

    def build_right(self):
        self.plot_frame = PlotFrame(
            self.right_frame,
            plot_configs={
                "Path": {"method": "plot_path", "is_3d": True},
                "Velocity": {"method": "plot_vel", "is_3d": False},
                "Geometrie": {"method": "plot_geometry", "is_3d": True},
            },
            default_plot="Velocity",
            title="Export Plot"
        )
        self.plot_frame.pack(fill="both", expand=True)