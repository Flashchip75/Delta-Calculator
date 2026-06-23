from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import *
from Oberflaeche.gui.designelemente.custom_widgets.grouping_widgets import *

import Oberflaeche.gui.designelemente.path_geometry_section as pdp
import path_berechnung.path_models_for_ui as path_models

# Eingabetab links zur Pfaddefinition

class PathDefTab(BaseTab):
    def build_left(self):
        ttk.Label(self, text="Pfad").pack(anchor="w")
        ttk.Label(self, text="Eingaben").pack(anchor="w")

        # Example variable and lambda function for writing properties to arbitrary locations
        self.x_test = (10, 20)
        write_x = lambda newVal: setattr(self, "x_test", newVal)

        def printAction():
            print("> Widget Values:")
            print(num_line4.get())
            print(num_line3.get())
            print(num_line2.get())
            print(num_line1.get())
            print(int_line.get())
            print(bool_line.get())
            print(list_line.get())
            print(dict_line.get())
            print("- - - - -")
            print("> Written Values:")
            print("x = " + str(self.x_test))
            print("----- ----- ----- ----- -----")

            folder.unlock()

        num_line4 = NumberLine(self, "Pos4", 4, uc.UnitLength(), defaults=(1, 2, 3, 4))
        num_line4.pack(fill=tk.X)
        num_line3 = NumberLine(self, "Pos3", 3, uc.UnitTime(), colored=True, onLineChangedFunction=printAction)
        num_line3.pack(fill=tk.X)
        num_line2 = NumberLine(self, "Pos2", 2, uc.UnitVelocity(), writePropertiesFunction=write_x)
        num_line2.pack(fill=tk.X)
        num_line1 = NumberLine(self, "Pos1", 1, colored=True, colorShift=0.5)
        num_line1.pack(fill=tk.X)
        blank_line = PropertyLine(self, "Blank")
        blank_line.pack(fill=tk.X)
        int_line = IncrementorLine(self, "Int")
        int_line.pack(fill=tk.X)

        folder = FolderFrame(self, "Folder", False, True)
        folder.pack(fill=tk.X)
        subframe = folder.contentFrame

        bool_line = CheckboxLine(subframe, "Box", writePropertiesFunction=lambda val: print("New State: " + str(val)), onLineChangedFunction=printAction)
        bool_line.pack(fill=tk.X)
        str_line = TextLine(subframe, "Teeeext", writePropertiesFunction=lambda val: print("New Text: " + str(val)), onLineChangedFunction=printAction, colored=True, colorShift=0.1)
        str_line.pack(fill=tk.X)
        list_line = DropdownLine(subframe, "Just List", ["Number 1", "Number 2", "Number 3"], writePropertiesFunction=lambda val: print("WOOP"), onLineChangedFunction=printAction, colored=True, colorShift=0.9)
        list_line.pack(fill=tk.X)
        dict_line = DropdownLine(subframe, "Not Just List", {"Number 1": 1, "Number 2": 2, "Number 3": 3}, writePropertiesFunction=lambda val: print("BEEP"), onLineChangedFunction=printAction, colored=True, colorShift=0.9)
        dict_line.pack(fill=tk.X)

        printButton = tk.Button(
            self,
            text="Print",
            command=printAction,
        )
        printButton.pack(fill=tk.X)

        line_obj = path_models.Line()
        bez_obj = path_models.Bezier()
        arc_obj = path_models.Arc()
        wait_obj = path_models.Wait()
        debug_obj = path_models.Debug()

        #line_section = pdp.path_property_section(self, line_obj)
        #line_section.pack(fill=tk.X)
#
        #bez_section = pdp.path_property_section(self, bez_obj)
        #bez_section.pack(fill=tk.X)
#
        #arc_section = pdp.path_property_section(self,arc_obj)
        #arc_section.pack(fill=tk.X)
#
        #wait_section = pdp.path_property_section(self, wait_obj)
        #wait_section.pack(fill=tk.X)

        debug_section = pdp.path_geometry_section(self, debug_obj)
        debug_section.pack(fill=tk.X)

        def objAction():
            print("> Object Values:")
            print(line_obj)
            print(bez_obj)
            print(arc_obj)
            print(wait_obj)
            print(debug_obj)
            print("----- ----- ----- ----- -----")

        pathSectionButton = tk.Button(
            self,
            text="Obj Data",
            command=objAction
        )
        pathSectionButton.pack(fill=tk.X)