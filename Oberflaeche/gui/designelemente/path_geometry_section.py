import typing
from typing import Tuple, List
import dataclasses
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import PropertyLine, NumberLine, IncrementorLine, CheckboxLine, TextLine, DropdownLine
from Oberflaeche.help_functions import unit_conversion as uc
import tkinter as tk
from tkinter import ttk
from path_berechnung.presolve import Presolver as pre


class path_geometry_section(tk.Frame):
    def __init__(self, master=None, data_object = None, **kwargs):
        super().__init__(master, **kwargs)
        if data_object is not None:
            self.data_object = data_object
            self._create_lines_from_dataclass()

    def _update_single_curve(self):
        #TODO: Presolve this curve and/or callback to parent (path_tab)

        discrete_path_data = pre.enrich_config( dict( uidata = ([self.data_object],[]) ) )
        print(discrete_path_data)
        pass

    def _create_lines_from_dataclass(self):
        self.lines = []
        for f in dataclasses.fields(self.data_object):
            # Skip specific keywords
            keywords = (
                "time_law_ref" # Reference integer connecting path geometry to traversal time_law
            )
            if f.name in keywords:
                continue

            # Extract Field Value
            if isinstance(f.default, dataclasses._MISSING_TYPE): # if produced my default factory
                default_value = getattr(self.data_object,f.name)
            else:
                default_value = f.default

            # Name and default Units

            default_unit = "/"

            # Find Base Type
            if typing.get_origin(f.type): # if annotated as typing type
                main_type = typing.get_origin(f.type)
            else:
                main_type = f.type

            # Extract Subtype Information
            main_type_args = typing.get_args(f.type)
            if main_type_args and main_type == tuple:
                sub_type = main_type_args[0]

                # Adjust defaults if unit is defined
                if main_type_args[-1] == str:
                    default_value = f.default[0:-1]
                    default_unit = f.default[-1]
            else:
                sub_type = None

            # Create new Line
            self._create_new_line(main_type, sub_type, f.name, default_value, default_unit)

    def _create_new_line(self, main_type, sub_type, field_name, default_value, default_unit):
        l = None

        # Common Attributes:
        line_name = field_name.replace("_", " ")
        write_function = lambda value: setattr(self.data_object, field_name, value)
        callback_function = self._update_single_curve
        unit_system = uc.get_unit_type(default_unit)()

        # Main parser
        # ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- | BOOL
        if   main_type == bool:
            l = CheckboxLine(
                self,
                line_name,
                writePropertiesFunction = write_function,
                onLineChangedFunction = callback_function,
                default = default_value
            )
        # ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- | STR
        elif main_type == str:
            l = TextLine(
                self,
                line_name,
                writePropertiesFunction=write_function,
                onLineChangedFunction=callback_function,
                default=default_value
            )
        # ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- | INT
        elif main_type == int:
            l = IncrementorLine(
                self,
                line_name,
                writePropertiesFunction = write_function,
                onLineChangedFunction = callback_function,
                default = default_value,
                units = unit_system,
                defaultUnit = default_unit
            )
        # ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- | FLOAT
        elif main_type == float:
            l = NumberLine(
                self,
                line_name,
                writePropertiesFunction = write_function,
                onLineChangedFunction = callback_function,
                defaults = (default_value,),
                inputCount = 1,
                units = unit_system,
                defaultUnit = default_unit
            )
        # ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- | TUPLE
        elif main_type == tuple:
            if sub_type == float:
                is_coordinate = isinstance(unit_system,uc.UnitLength) and len(default_value) == 3
                l = NumberLine(
                    self,
                    line_name,
                    writePropertiesFunction = write_function,
                    onLineChangedFunction = callback_function,
                    defaults = default_value,
                    inputCount = len(default_value),
                    units = unit_system,
                    defaultUnit = default_unit,
                    colored = is_coordinate
                )
            elif sub_type == int:
                l = IncrementorLine(
                    self,
                    line_name,
                    writePropertiesFunction = write_function,
                    onLineChangedFunction = callback_function,
                    default = default_value[0],
                    defaultUnit = default_unit,
                    units = unit_system
                )
        # ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- | LIST
        elif main_type == list:
            l = DropdownLine(
                self,
                line_name,
                writePropertiesFunction = write_function,
                onLineChangedFunction = callback_function,
                options = default_value
            )
        # ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- | DICT
        elif main_type == dict:
            l = DropdownLine(
                self,
                line_name,
                writePropertiesFunction=write_function,
                onLineChangedFunction=callback_function,
                options=default_value
            )

        # Store new Line
        if l:
            self.lines.append(l)
            l.pack(fill=tk.BOTH)
            l.updateLine(True)