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

        self.advanced_checkbox = CheckboxLine(
            self,
            "Advanced",
            default=False,
            writePropertiesFunction=self.set_advanced_mode
        )
        self.advanced_checkbox.pack(fill=tk.X)

        self.gravity = NumberLine(
            self,
            "Gravity",
            1,
            uc.UnitAcceleration(),
            defaults=(abs(float(self.robot_config.global_data["gravity"][2])),),
            writePropertiesFunction=self.set_gravity
        )
        self.gravity.pack(fill=tk.X)

        self.basic_geometry_frame = tk.Frame(self, bg="#ffffff")
        self.basic_geometry_frame.pack(fill=tk.X)

        self.motor_radius = NumberLine(
            self.basic_geometry_frame,
            "Motor Radius",
            1,
            uc.UnitLength(),
            defaults=(self.get_motor_radius() / uc.UnitLength().mm,),
            writePropertiesFunction=self.set_motor_radius
        )
        self.motor_radius.pack(fill=tk.X)

        self.end_effector_radius = NumberLine(
            self.basic_geometry_frame,
            "Endeffector Radius",
            1,
            uc.UnitLength(),
            defaults=(self.robot_config.motors[0].get("EF_offset_radius", 0.0) / uc.UnitLength().mm,),
            writePropertiesFunction=self.set_end_effector_radius
        )
        self.end_effector_radius.pack(fill=tk.X)

        self.advanced_geometry_frame = tk.Frame(self, bg="#ffffff")
        self.build_advanced_geometry()

        self.upper_length = NumberLine(
            self.basic_geometry_frame,
            "Upper Arm Length",
            1,
            uc.UnitLength(),
            defaults=(self.robot_config.upper_arm_length / uc.UnitLength().mm,),
            writePropertiesFunction=self.set_upper_arm_length
        )
        self.upper_length.pack(fill=tk.X)

        self.upper_arm_mass = NumberLine(
            self.basic_geometry_frame,
            "Upper Arm Mass",
            1,
            uc.UnitMass(),
            defaults=(self.robot_config.upper_arm_mass,),
            writePropertiesFunction=self.set_upper_arm_mass
        )
        self.upper_arm_mass.pack(fill=tk.X)

        self.lower_length = NumberLine(
            self.basic_geometry_frame,
            "Lower Arm Length",
            1,
            uc.UnitLength(),
            defaults=(self.robot_config.lower_arm_length / uc.UnitLength().mm,),
            writePropertiesFunction=self.set_lower_arm_length
        )
        self.lower_length.pack(fill=tk.X)

        self.lower_arm_mass = NumberLine(
            self.basic_geometry_frame,
            "Lower Arm Mass",
            1,
            uc.UnitMass(),
            defaults=(self.robot_config.lower_arm_mass,),
            writePropertiesFunction=self.set_lower_arm_mass
        )
        self.lower_arm_mass.pack(fill=tk.X)

        self.show_geometry_button = ttk.Button(
            self,
            text="Show Geometry",
            command=self.show_geometry_callback
        )
        self.show_geometry_button.pack(fill=tk.X, pady=5)

    def build_advanced_geometry(self):
        advanced_fields = (
            (
                "Position",
                3,
                uc.UnitLength(),
                lambda motor: tuple(np.array(motor["position"], dtype=float) / uc.UnitLength().mm),
                self.set_motor_position,
                ""
            ),
            ("Axis", 3, uc.Unitless(), lambda motor: tuple(motor["axis"]), self.set_motor_axis, ""),
            (
                "EF Offset Angle",
                1,
                uc.UnitAngle(),
                lambda motor: (self.get_angle_degrees(motor.get("EF_offset_angle", 0.0)),),
                self.set_motor_ef_offset_angle,
                "deg"
            ),
            (
                "EF Offset Radius",
                1,
                uc.UnitLength(),
                lambda motor: (motor.get("EF_offset_radius", 0.0) / uc.UnitLength().mm,),
                self.set_motor_ef_offset_radius,
                ""
            ),
            (
                "Upper Arm Length",
                1,
                uc.UnitLength(),
                lambda motor: (motor.get("upper_length", self.robot_config.upper_arm_length) / uc.UnitLength().mm,),
                self.set_motor_upper_arm_length,
                ""
            ),
            (
                "Upper Arm Mass",
                1,
                uc.UnitMass(),
                lambda motor: (motor.get("upper_mass", self.robot_config.upper_arm_mass),),
                self.set_motor_upper_arm_mass,
                ""
            ),
            (
                "Lower Arm Length",
                1,
                uc.UnitLength(),
                lambda motor: (motor.get("lower_length", self.robot_config.lower_arm_length) / uc.UnitLength().mm,),
                self.set_motor_lower_arm_length,
                ""
            ),
            (
                "Lower Arm Mass",
                1,
                uc.UnitMass(),
                lambda motor: (motor.get("lower_mass", self.robot_config.lower_arm_mass),),
                self.set_motor_lower_arm_mass,
                ""
            )
        )

        for motor_index, motor in enumerate(self.robot_config.motors):
            ttk.Label(
                self.advanced_geometry_frame,
                text=f"Motor {motor['name']}"
            ).pack(anchor="w")

            for label, input_count, units, defaults_function, write_function, default_unit in advanced_fields:
                self.add_advanced_motor_line(
                    motor,
                    motor_index,
                    label,
                    input_count,
                    units,
                    defaults_function(motor),
                    write_function,
                    default_unit=default_unit
                )

    def add_advanced_motor_line(
            self,
            motor,
            motor_index,
            label,
            input_count,
            units,
            defaults,
            write_function,
            default_unit=""
    ):
        line = NumberLine(
            self.advanced_geometry_frame,
            f"Motor {motor['name']} {label}",
            input_count,
            units,
            defaults=defaults,
            defaultUnit=default_unit,
            writePropertiesFunction=lambda val, index=motor_index: write_function(index, val)
        )
        line.label.configure(text=label)
        line.pack(fill=tk.X)
        return line

    def set_advanced_mode(self, enabled):
        if enabled:
            self.basic_geometry_frame.pack_forget()
            self.advanced_geometry_frame.pack(
                fill=tk.X,
                before=self.show_geometry_button
            )
        else:
            self.advanced_geometry_frame.pack_forget()
            self.basic_geometry_frame.pack(
                fill=tk.X,
                before=self.show_geometry_button
            )

    def get_motor_center(self):
        return np.mean(
            [np.array(motor["position"], dtype=float) for motor in self.robot_config.motors],
            axis=0
        )

    def get_motor_radius(self):
        center = self.get_motor_center()
        motor_position = np.array(self.robot_config.motors[0]["position"], dtype=float)
        return np.linalg.norm(motor_position[:2] - center[:2])

    def get_angle_degrees(self, angle_radians):
        return round(float(angle_radians) / uc.UnitAngle().deg, 10)

    def set_motor_position(self, motor_index, value):
        self.robot_config.motors[motor_index]["position"] = np.array(value, dtype=float)
        self.robot_config.robot_center = self.get_motor_center()

    def set_motor_axis(self, motor_index, value):
        axis = np.array(value, dtype=float)
        axis_norm = np.linalg.norm(axis)

        if axis_norm == 0.0:
            return

        self.robot_config.motors[motor_index]["axis"] = axis / axis_norm

    def set_motor_ef_offset_angle(self, motor_index, value):
        self.robot_config.motors[motor_index]["EF_offset_angle"] = float(value[0])

    def set_motor_ef_offset_radius(self, motor_index, value):
        self.robot_config.motors[motor_index]["EF_offset_radius"] = abs(float(value[0]))

    def set_motor_upper_arm_length(self, motor_index, value):
        self.robot_config.motors[motor_index]["upper_length"] = float(value[0])

    def set_motor_upper_arm_mass(self, motor_index, value):
        self.robot_config.motors[motor_index]["upper_mass"] = float(value[0])

    def set_motor_lower_arm_length(self, motor_index, value):
        self.robot_config.motors[motor_index]["lower_length"] = float(value[0])

    def set_motor_lower_arm_mass(self, motor_index, value):
        self.robot_config.motors[motor_index]["lower_mass"] = float(value[0])

    def set_motor_radius(self, value):
        radius = abs(float(value[0]))
        center = self.get_motor_center()
        motor_angles = (0.0, 2.0 * np.pi / 3.0, -2.0 * np.pi / 3.0)

        for motor, angle in zip(self.robot_config.motors, motor_angles):
            motor["position"] = center + np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                0.0
            ], dtype=float)

        self.robot_config.robot_center = self.get_motor_center()

    def set_upper_arm_length(self, value):
        value = float(value[0])
        self.robot_config.upper_arm_length = value

        for motor in self.robot_config.motors:
            motor["upper_length"] = value

    def set_upper_arm_mass(self, value):
        value = float(value[0])
        self.robot_config.upper_arm_mass = value

        for motor in self.robot_config.motors:
            motor["upper_mass"] = value

    def set_lower_arm_length(self, value):
        value = float(value[0])
        self.robot_config.lower_arm_length = value

        for motor in self.robot_config.motors:
            motor["lower_length"] = value

    def set_lower_arm_mass(self, value):
        value = float(value[0])
        self.robot_config.lower_arm_mass = value

        for motor in self.robot_config.motors:
            motor["lower_mass"] = value

    def set_end_effector_radius(self, value):
        value = abs(float(value[0]))

        for motor in self.robot_config.motors:
            motor["EF_offset_radius"] = value

    def set_gravity(self, value):
        value = abs(float(value[0]))
        self.robot_config.global_data["gravity"] = np.array([0.0, 0.0, -value], dtype=float)

    def show_geometry_callback(self):
        if self.on_show_geometry is not None:
            self.on_show_geometry()
