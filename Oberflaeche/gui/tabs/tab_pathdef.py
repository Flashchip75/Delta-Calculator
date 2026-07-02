from Oberflaeche.gui.designelemente.initial_condition_frame import initial_condition_frame
from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import *
from Oberflaeche.gui.designelemente.custom_widgets.grouping_widgets import *

import Oberflaeche.gui.designelemente.path_geometry_section as pgeo
import path_berechnung.path_models_for_ui as path_models
import path_berechnung.exe_path as exeP

# Eingabetab links zur Pfaddefinition

class PathDefTab(BaseTab):
    def build_left(self):

        self.all_geo_sections = []
        self.current_section = None
        self.all_time_laws = []

        def setCurve(index: int):
            [geo_sec.pack_forget() for geo_sec in self.all_geo_sections]
            [time_law.pack_forget() for time_law in self.all_time_laws]

            self.current_section = self.all_geo_sections[index]
            self.current_section.pack(fill=tk.X)
            self.all_time_laws[ self.current_section.data_object.time_law_ref ].pack(fill=tk.X)


        # ----- Controls ----- ----- ----- ----- -----

        path_controls_folder = FolderFrame(self, "Controls")
        path_controls_folder.pack(fill=tk.X)

        curve_type_keys = [ct.__name__ for ct in path_models.get_path_models()[0]]

        time_law_selector = DropdownLine(
            path_controls_folder.contentFrame,
            "New Curve Type",
            options=dict(zip(curve_type_keys, path_models.get_path_models()[0])),
        )
        time_law_selector.pack(fill=tk.X)

        addButton = tk.Button(
            path_controls_folder.contentFrame,
            text="[+] Add Curve",
        )
        addButton.pack(fill=tk.X, pady=(0, 5))

        removeButton = tk.Button(
            path_controls_folder.contentFrame,
            text="[-] Remove current Curve",
        )
        removeButton.pack(fill=tk.X)

        # ----- Timeline ----- ----- ----- ----- -----

        path_tl_folder = FolderFrame(self, "Timeline")
        path_tl_folder.pack(fill=tk.X)

        path_tl_folder.contentFrame.config(background="#333333")


        arcButton = tk.Button(
            path_tl_folder.contentFrame,
            text="Arc",
            command=lambda:setCurve(0),
            background="#bf6060",
            foreground="#000000",
        )
        arcButton.pack(side="left",padx = (5, 0), pady = (5, 5))

        bezButton = tk.Button(
            path_tl_folder.contentFrame,
            text="Bezier",
            command=lambda:setCurve(1),
            background="#8fbf60",
            foreground="#000000",
        )
        bezButton.pack(side="left")

        lineButton = tk.Button(
            path_tl_folder.contentFrame,
            text="Line",
            command=lambda:setCurve(2),
            background="#60bfbf",
            foreground="#000000",
        )
        lineButton.pack(side="left")



        # ----- Path Geometry ----- ----- ----- ----- -----

        path_geo_folder = FolderFrame(self, "Curve Geometry")
        path_geo_folder.pack(fill=tk.X)

        arc_section = pgeo.path_geometry_section(path_geo_folder.contentFrame, path_models.Arc())
        self.all_geo_sections.append(arc_section) # at [0]

        bez_section = pgeo.path_geometry_section(path_geo_folder.contentFrame, path_models.Bezier())
        self.all_geo_sections.append(bez_section) # at [1]

        line_section = pgeo.path_geometry_section(path_geo_folder.contentFrame, path_models.Line())
        self.all_geo_sections.append(line_section) # at [2]



        # ----- Path Traversal ----- ----- ----- ----- -----

        path_tra_folder = FolderFrame(self, "Curve Traversal")
        path_tra_folder.pack(fill=tk.X)


        time_law_keys = [tl.__name__ for tl in path_models.get_path_models()[1]] + ["Extend Previous"]
        time_law_values = path_models.get_path_models()[1] + (None,)

        time_law_selector = DropdownLine(
            path_tra_folder.contentFrame,
            "Time Law",
            options=dict(zip(time_law_keys, time_law_values)),
        )
        time_law_selector.pack(fill=tk.X, pady=(0,5))

        poly5_time = pgeo.path_geometry_section(path_tra_folder.contentFrame, path_models.Polynomial5())
        self.all_time_laws.append(poly5_time)
        self.all_geo_sections[0].data_object.time_law_ref = 0

        self.all_geo_sections[1].data_object.time_law_ref = 0


        poly7_time = pgeo.path_geometry_section(path_tra_folder.contentFrame, path_models.Polynomial7())
        self.all_time_laws.append(poly7_time)
        self.all_geo_sections[2].data_object.time_law_ref = 1



        # ----- Calculate ----- ----- ----- ----- -----

        def demoCalc():
            print("Calculating...")
            curve_list = [geo_sec.data_object for geo_sec in self.all_geo_sections]
            time_law_list = [time_law.data_object for time_law in self.all_time_laws]

            print("----- Curves:")
            [print(c) for c in curve_list]
            print("----- Time Laws:")
            [print(tl) for tl in time_law_list]

            calc_data = exeP.exePath().run( uiData = (curve_list, time_law_list) )
            print(calc_data)

        calcButton = tk.Button(
            self,
            text="Calculate full Path",
            command=demoCalc,
        )
        calcButton.pack(fill=tk.X)


        #  ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
        # Populate initial:
        setCurve(0)
