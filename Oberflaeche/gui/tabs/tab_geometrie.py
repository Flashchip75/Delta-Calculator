import tkinter as tk
from tkinter import ttk
import numpy as np

from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.help_functions import unit_conversion as uc
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import *


class GeometrieTab(BaseTab):
    def __init__(self, parent, robot_config, on_show_geometry=None):
        self.robot_config = robot_config
        self.on_show_geometry = on_show_geometry
        super().__init__(parent)

    def build_left(self):
        ttk.Label(self, text="Geometrie").pack(anchor="w")
        ttk.Label(self, text="Eingaben").pack(anchor="w")

        self.motor_a_pos = NumberLine(
            self,
            "Motor A Position",
            3,
            uc.UnitLength(),
            defaults=tuple(self.robot_config.motors[0]["position"]),
            writePropertiesFunction=lambda val: self.set_motor_position(0, val)
        )
        self.motor_a_pos.pack(fill=tk.X)

        self.motor_b_pos = NumberLine(
            self,
            "Motor B Position",
            3,
            uc.UnitLength(),
            defaults=tuple(self.robot_config.motors[1]["position"]),
            writePropertiesFunction=lambda val: self.set_motor_position(1, val)
        )
        self.motor_b_pos.pack(fill=tk.X)

        self.motor_c_pos = NumberLine(
            self,
            "Motor C Position",
            3,
            uc.UnitLength(),
            defaults=tuple(self.robot_config.motors[2]["position"]),
            writePropertiesFunction=lambda val: self.set_motor_position(2, val)
        )
        self.motor_c_pos.pack(fill=tk.X)

        self.upper_length = NumberLine(
            self,
            "Oberarmlänge",
            1,
            uc.UnitLength(),
            defaults=(self.robot_config.upper_arm_length,),
            writePropertiesFunction=self.set_upper_arm_length
        )
        self.upper_length.pack(fill=tk.X)

        self.lower_length = NumberLine(
            self,
            "Unterarmlänge",
            1,
            uc.UnitLength(),
            defaults=(self.robot_config.lower_arm_length,),
            writePropertiesFunction=self.set_lower_arm_length
        )
        self.lower_length.pack(fill=tk.X)

        ttk.Button(
            self,
            text="Geometrie anzeigen",
            command=self.show_geometry_callback
        ).pack(fill=tk.X, pady=5)

    def set_motor_position(self, motor_index, value):
        self.robot_config.motors[motor_index]["position"] = np.array(value, dtype=float)

    def set_upper_arm_length(self, value):
        value = float(value[0])
        self.robot_config.upper_arm_length = value

        for motor in self.robot_config.motors:
            motor["upper_length"] = value

    def set_lower_arm_length(self, value):
        value = float(value[0])
        self.robot_config.lower_arm_length = value

        for motor in self.robot_config.motors:
            motor["lower_length"] = value

    def show_geometry_callback(self):
        if self.on_show_geometry is not None:
            self.on_show_geometry()