from Oberflaeche.gui.designelemente.initial_condition_frame import initial_condition_frame
from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import *
from Oberflaeche.gui.designelemente.custom_widgets.grouping_widgets import *

import Oberflaeche.gui.designelemente.path_geometry_section as pgeo
import path_berechnung.path_models_for_ui as path_models

# Eingabetab links zur Pfaddefinition

class PathDefTab(BaseTab):
    def build_left(self):

        self.all_geo_sections = []
        self.current_section = None

        def setCurve(index: int):
            [geo_sec.pack_forget() for geo_sec in self.all_geo_sections]
            self.initial_condition.pack_forget()
            if index == -1:
                self.current_section = None
                self.initial_condition.pack(fill=tk.X)
                path_tra_folder.close()
                path_tra_folder.lock()
            else:
                self.current_section = self.all_geo_sections[index]
                self.current_section.pack(fill=tk.X)
                path_tra_folder.unlock()
                path_tra_folder.open()

        # Timeline

        path_tl_folder = FolderFrame(self, "Timeline")
        path_tl_folder.pack(fill=tk.X)

        path_tl_folder.contentFrame.config(background="#333333")

        startButton = tk.Button(
            path_tl_folder.contentFrame,
            text="t0",
            command=lambda: setCurve(-1),
            background="#666666",
            foreground="#ffffff",
        )
        startButton.pack(side="left", padx=(5,0), pady=5)

        arcButton = tk.Button(
           path_tl_folder.contentFrame,
           text="Arc",
           command=lambda:setCurve(0),
            background="#bf6060",
            foreground="#000000",
        )
        arcButton.pack(side="left")

        bezButton = tk.Button(
           path_tl_folder.contentFrame,
           text="Bezier",
           command=lambda:setCurve(1),
            background="#8fbf60",
            foreground="#000000",
        )
        bezButton.pack(side="left")

        # Path Geometry

        path_geo_folder = FolderFrame(self, "Curve Geometry")
        path_geo_folder.pack(fill=tk.X)

        self.initial_condition = initial_condition_frame(path_geo_folder.contentFrame)
        self.initial_condition.pack(fill=tk.X)

        arc_section = pgeo.path_geometry_section(path_geo_folder.contentFrame, path_models.Arc())
        self.all_geo_sections.append(arc_section)

        bez_section = pgeo.path_geometry_section(path_geo_folder.contentFrame, path_models.Bezier())
        self.all_geo_sections.append(bez_section)

        # Path Traversal

        path_tra_folder = FolderFrame(self, "Curve Traversal",False,True)
        path_tra_folder.pack(fill=tk.X)

        num_line_inside = NumberLine(path_tra_folder.contentFrame, "Velocity", 1)
        num_line_inside.pack(fill=tk.X)

        num_line_outside = NumberLine(path_tra_folder.contentFrame, "Acceleration", 1)
        num_line_outside.pack(fill=tk.X)

        # Calculate

        def demoCalc():
            print("Calculating...")
            print("Start: " + str(self.initial_condition.position.get()))
            [print(geo_sec.data_object) for geo_sec in self.all_geo_sections]


        calcButton = tk.Button(
            self,
            text="Calculate full Path",
            command=demoCalc,
        )
        calcButton.pack(fill=tk.X)