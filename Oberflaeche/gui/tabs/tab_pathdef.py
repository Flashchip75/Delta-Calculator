from Oberflaeche.gui.designelemente.initial_condition_frame import initial_condition_frame
from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import *
from Oberflaeche.gui.designelemente.custom_widgets.grouping_widgets import *
from Oberflaeche.gui.designelemente.custom_widgets.timeline_button import TimelineButton

import Oberflaeche.gui.designelemente.path_geometry_section as pgeo
import path_berechnung.path_models_for_ui as path_models
import path_berechnung.exe_path as exeP

# Eingabetab links zur Pfaddefinition

class PathDefTab(BaseTab):
    def build_left(self):

        self.current_index = -1
        self.all_geo_sections = []
        self.all_time_law_sections = []
        self.all_timeline_buttons = []

        self.transitioning = False
        self.solver_output = None

        # ----- Controls ----- ----- ----- ----- -----

        self.path_controls_folder = FolderFrame(self, "Controls")
        self.path_controls_folder.pack(fill=tk.X)

        curve_type_keys = [ct.__name__ for ct in path_models.get_path_models()[0]]

        self.geometry_type_selector = DropdownLine(
            self.path_controls_folder.contentFrame,
            "New Curve Type",
            options=dict(zip(curve_type_keys, path_models.get_path_models()[0])),
        )
        self.geometry_type_selector.pack(fill=tk.X)

        self.add_button = tk.Button(
            self.path_controls_folder.contentFrame,
            text="[+] Add Curve",
            command=lambda:self.add_curve( self.geometry_type_selector.get()() ),
        )
        self.add_button.pack(fill=tk.X, pady=(0, 5))

        self.remove_button = tk.Button(
            self.path_controls_folder.contentFrame,
            text="[-] Remove current Curve",
            command=lambda:self.remove_curve( self.current_index ),
            state="disabled",
        )
        self.remove_button.pack(fill=tk.X)

        # ----- Timeline ----- ----- ----- ----- -----

        self.path_tl_folder = FolderFrame(self, "Timeline", False, True)
        self.path_tl_folder.pack(fill=tk.X)

        self.path_tl_folder.contentFrame.config(background="#333333")

        self.timeline_start = tk.Button(
            self.path_tl_folder.contentFrame,
            text="",
            background="#333333",
            state="disabled"
        )
        self.timeline_start.pack(side="left", padx=(5, 0), pady=(5, 5))

        # ----- Path Geometry ----- ----- ----- ----- -----

        self.path_geo_folder = FolderFrame(self, "Curve Geometry", False, True)
        self.path_geo_folder.pack(fill=tk.X)

        # ----- Path Traversal ----- ----- ----- ----- -----

        self.path_tra_folder = FolderFrame(self, "Curve Traversal", False, True)
        self.path_tra_folder.pack(fill=tk.X)

        time_law_keys = ["Extend Previous"] + [tl.__name__ for tl in path_models.get_path_models()[1]]
        time_law_values = (lambda:None,) + path_models.get_path_models()[1]

        self.time_law_type_selector = DropdownLine(
            self.path_tra_folder.contentFrame,
            "Time Law",
            options=dict(zip(time_law_keys, time_law_values)),
            writePropertiesFunction=lambda data_class: self.replace_time_law(self.current_index, data_class() ),
        )
        self.time_law_type_selector.pack(fill=tk.X, pady=(0,5))

        # ----- Calculate ----- ----- ----- ----- -----

        self.calc_button = tk.Button(
            self,
            text="Calculate full Path",
            command=self.solve,
            state="disabled",
        )
        self.calc_button.pack(fill=tk.X)

    # ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----

    def add_curve(self, geometry_data_object):
        self.invalidate()
        # New Geometry
        new_section = pgeo.path_geometry_section(self.path_geo_folder.contentFrame, geometry_data_object, self.invalidate)
        self.all_geo_sections.append(new_section)
        new_index = len(self.all_geo_sections) - 1

        # New Time Law (Extend by default, unless first Curve)
        self.all_time_law_sections.append(None)
        if self.current_index == -1:
            self.replace_time_law( new_index, list(self.time_law_type_selector.input.conversionDict.values())[1]() )

        # New Timeline Button
        new_button = TimelineButton(
            self.path_tl_folder.contentFrame,
            text=geometry_data_object.__class__.__name__,
            command=self.set_curve,
            index=new_index,
        )
        new_button.pack(side="left")
        self.all_timeline_buttons.append(new_button)

        self.set_curve(new_index)

    def set_curve(self, index: int):
        self.current_index = index
        for geo_sec in self.all_geo_sections:
            geo_sec.pack_forget()
        for button in self.all_timeline_buttons:
            button.normal_color()

        if self.current_index == -1:
            self.lock_editing()
        else:
            self.unlock_editing()
            current_section = self.all_geo_sections[index]
            current_section.pack(fill=tk.X)
            self.all_timeline_buttons[index].highlight_color()
            self.set_time_law(index)

    def remove_curve(self, index: int):
        self.invalidate()
        # Remove Geometry
        self.all_geo_sections[index].destroy()
        self.all_geo_sections.pop(index)

        # Move or Remove Time Law
        old_time_law = self.all_time_law_sections[index]        # Object to destroy
        next_index = index - 1                                  # Jump to the left

        if len(self.all_time_law_sections) > index+1:           # If in the middle of the List
            next_index = index                                  # Jump to the right instead
            if self.all_time_law_sections[index+1] is None:     # If next curve was extending this time law
                self.all_time_law_sections[index+1] = self.all_time_law_sections[index] # transfer time law
                old_time_law = None                             # And do not destroy section

        if old_time_law is not None:
            old_time_law.destroy()
        self.all_time_law_sections.pop(index)

        # Remove Timeline Button
        self.all_timeline_buttons[index].destroy()
        self.all_timeline_buttons.pop(index)

        # Update Button indices
        for button, i in zip(self.all_timeline_buttons, range(len(self.all_timeline_buttons))):
            button.index = i

        # Show next curve
        self.set_curve(next_index)

    def set_time_law(self, index: int):
        self.transitioning = True # Set Transitioning Flag to catch combobox callback

        [time_law.pack_forget() for time_law in self.all_time_law_sections if time_law is not None]

        if self.all_time_law_sections[index] is not None:
            self.all_time_law_sections[index].pack(fill=tk.X)
            combobox_index = list( self.time_law_type_selector.input.conversionDict.values() ).index( self.all_time_law_sections[index].data_object.__class__ )
        else:
            combobox_index = 0

        self.time_law_type_selector.input.current(combobox_index)

        self.transitioning = False

    def replace_time_law(self, index: int, time_law_data_object):
        if not self.transitioning:
            self.invalidate()
            old_section = self.all_time_law_sections[index]
            if time_law_data_object is not None:
                new_section = pgeo.path_data_section(self.path_tra_folder.contentFrame, time_law_data_object, self.invalidate)
            else:
                new_section = None

            self.all_time_law_sections[index] = new_section

            if old_section is not None:
                old_section.destroy()

            if index == self.current_index:
                self.set_time_law(index)

    def lock_editing(self):
        self.remove_button.configure(state="disabled")
        self.calc_button.configure(state="disabled")
        self.path_tl_folder.close()
        self.path_tl_folder.lock()
        self.path_geo_folder.close()
        self.path_geo_folder.lock()
        self.path_tra_folder.close()
        self.path_tra_folder.lock()

    def unlock_editing(self):
        self.remove_button.configure(state="normal")
        self.calc_button.configure(state="normal")
        self.path_tl_folder.unlock()
        self.path_tl_folder.open()
        self.path_geo_folder.unlock()
        self.path_geo_folder.open()
        self.path_tra_folder.unlock()
        self.path_tra_folder.open()

    def update_references(self):
        i = -1
        for geo_sec in self.all_geo_sections:
            if self.all_time_law_sections[i] is not None:
                i = i + 1
            geo_sec.data_object.time_law_ref = i

    def solve(self):
        if self.solver_output is not None:
            print("Found cached solution")
        else:
            print("Calculating...")
            curve_list = [geo_sec.data_object for geo_sec in self.all_geo_sections]
            time_law_list = [time_law.data_object for time_law in self.all_time_law_sections if time_law is not None]
            self.update_references()

            print("----- Curves:")
            [print(c) for c in curve_list]
            print("----- Time Laws:")
            [print(tl) for tl in time_law_list]

            #self.solver_output = "DATA"
            self.solver_output = exeP.exePath().run( uiData = (curve_list, time_law_list) )
            #print(self.solver_output)

    def invalidate(self):
        self.solver_output = None