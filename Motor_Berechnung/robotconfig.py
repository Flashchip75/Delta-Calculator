import json
import numpy as np
from math_utilities import unit

class RobotConfig:
    def __init__(self, config_path):
        config_data = self.load_json(config_path)

        self.global_data = self.create_global_object(config_data["global"])
        self.workspace = self.create_workspace_object(config_data["workspace"])
        # Zentrumsbestimmung vor den Motoren (wird für "AUTO" axis benötigt)
        positions = [
            self.create_vector_object_from_list(config_data["motors"][m]["position"], f"motors.{m}.position")
            for m in ["A", "B", "C"]
        ]
        self.robot_center = np.mean(positions, axis=0)

        self.motors = self.create_motors_object(config_data["motors"])

        self.upper_arm_length = self.motors[0]["upper_length"]
        self.lower_arm_length = self.motors[0]["lower_length"]

    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def create_vector_object_from_list(self, values, name):
        if len(values) != 3:
            raise ValueError(f"{name} muss genau 3 Werte enthalten")
        return np.array(values, dtype=float)

    def create_range_object(self, values, name):
        if len(values) != 2:
            raise ValueError(f"{name} muss genau 2 Werte enthalten")
        return {
            "min": float(values[0]),
            "max": float(values[1]),
        }

    def create_global_object(self, global_data):
        return {
            "gravity": self.create_vector_object_from_list(global_data["gravity"], "global.gravity"),
            "payload_mass": float(global_data["payload_mass"]),
            "singularity_margin_deg": float(global_data["singularity_margin_deg"]),
            "trajectory_csv": str(global_data["trajectory_csv"]),
        }

    def create_workspace_object(self, workspace_data):
        return {
            "resolution": int(workspace_data["resolution"]),
            "range_x": self.create_range_object(workspace_data["range_x"], "workspace.range_x"),
            "range_y": self.create_range_object(workspace_data["range_y"], "workspace.range_y"),
            "range_z": self.create_range_object(workspace_data["range_z"], "workspace.range_z"),
        }

    def create_motor_object(self, name, motor_data):
        position = self.create_vector_object_from_list(motor_data["position"], f"motors.{name}.position")
        
        if motor_data.get("axis") == "AUTO":
            v = position - self.robot_center
            axis = np.array([-v[1], v[0], 0.0], dtype=float)
            if np.linalg.norm(axis) < 1e-6:
                axis = np.array([1.0, 0.0, 0.0])
        else:
            axis = self.create_vector_object_from_list(motor_data["axis"], f"motors.{name}.axis")
            
        axis = unit(axis)

        return {
            "name": name,
            "position": position,
            "axis": axis,
            "upper_length": float(motor_data["upper_length"]),
            "upper_mass": float(motor_data["upper_mass"]),
            "lower_length": float(motor_data["lower_length"]),
            "lower_mass": float(motor_data["lower_mass"]),
            "theta_min": float(motor_data["theta_min"]),
            "theta_max": float(motor_data["theta_max"]),
            "i": int(motor_data.get("i", 0)),
        }

    def create_motors_object(self, motors_data):
        return [
            self.create_motor_object("A", motors_data["A"]),
            self.create_motor_object("B", motors_data["B"]),
            self.create_motor_object("C", motors_data["C"]),
        ]

    def compute_robot_center(self):
        return np.mean([motor["position"] for motor in self.motors], axis=0)
