from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.geo_input import GeoInput
from Oberflaeche.gui.designelemente.plot_frames import PlotFrame
from Oberflaeche.help_functions.struct_geo_data import GeoData


class GeometrieTab(BaseTab):
    def __init__(self, parent):
        self.plot_frame = None
        self.geo_input = None
        self.geo_data = GeoData()
        super().__init__(parent)

    def build_left(self):
        self.geo_input = GeoInput(self.left_frame, self.geo_data)
        self.geo_input.pack(fill="both", expand=True, anchor="n")

    def build_right(self):
        self.plot_frame = PlotFrame(
            self.right_frame,
            plot_configs={
                "Geometrie": {"method": "plot_geometry", "is_3d": True},
                "Path": {"method": "plot_path", "is_3d": True},
                "Velocity": {"method": "plot_vel", "is_3d": False},
            },
            default_plot="Geometrie",
            title="Geometrie Plot"
        )
        self.plot_frame.pack(fill="both", expand=True)
