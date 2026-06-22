import typing
from typing import Tuple, List
import dataclasses
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import PropertyLine, NumberLine, IncrementorLine, CheckboxLine, TextLine, DropdownLine


def create_lines_from_dataclass(dataclass, line_master) -> List[PropertyLine]:
    new_lines = []
    for f in dataclasses.fields(dataclass):

        # Skip specific keywords
        if f.name == "time_law_ref":
            continue

        # Find base type if type is typing alias
        main_type = typing.get_origin(f.type) if typing.get_origin(f.type) else f.type

        # Extract Subtype Information
        main_type_args = typing.get_args(f.type)
        if main_type_args:
            sub_type = main_type_args[0]
            if main_type_args[-1] == str:
                field_count = len(main_type_args) - 1
                has_unit_string = True
            else:
                field_count = len(main_type_args)
                has_unit_string = False

        # Initialize Property Writer
        write_to_field = lambda value: setattr(dataclass, f.name, value)

        # Main parser
        if   main_type == bool:
            l = CheckboxLine(
                line_master,
                f.name.replace("_", " "),
                default = f.default,
                writePropertiesFunction = write_to_field
            )
            new_lines.append(l)
            print("BOOL")

        elif main_type == str:
            #new_lines.append(TextLine(line_master,f.name.replace("_"," ")))
            print("STRING")

        elif main_type == int:
            #new_lines.append(IncrementorLine(line_master,f.name.replace("_"," ")))
            print("INTEGER")

        elif main_type == float:
            # new_lines.append(NumberLine(line_master,f.name.replace("_"," ")))
            print("FLOAT")

        elif main_type == tuple:
            if sub_type == int:
                # new_lines.append(IncrementorLine(line_master,f.name.replace("_"," ")))
                print("INT TUPLE")

            elif sub_type == float:
                # new_lines.append(NumberLine(line_master,f.name.replace("_"," ")))
                print("FLOAT TUPLE")


        elif main_type == list:
            #new_lines.append(DropdownLine(line_master, f.name.replace("_", " ")))
            print("LIST")

        elif main_type == dict:
            # new_lines.append(DropdownLine(line_master, f.name.replace("_", " ")))
            print("DICT")




