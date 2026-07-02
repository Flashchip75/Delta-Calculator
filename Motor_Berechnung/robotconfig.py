import numpy as np
from Motor_Berechnung.math_utilities import unit

class RobotConfig:
    def __init__(self):
        self.global_data = {
            "gravity": np.array([0.0, 0.0, -9.81], dtype=float),
            "mass_kg": 1.0,
            "payload_mass": 0.100,
            "singularity_margin_deg": 5.0,
            "trajectory_csv": "roboter_dynamik.csv",
            "output_dir": "output"
        }

        self.workspace = {
            "resolution": 25,
            "range_x": {"min": -0.6, "max": 0.6},
            "range_y": {"min": -0.6, "max": 0.6},
            "range_z": {"min": -0.6, "max": 0}
        }

        pos_A = np.array([-0.072612, -0.044232, 0.0], dtype=float)
        pos_B = np.array([0.074612, -0.040768, 0.0], dtype=float)
        pos_C = np.array([-0.002, 0.085, 0.0], dtype=float)

        self.robot_center = np.mean([pos_A, pos_B, pos_C], axis=0)

        self.motors = [
            {
                "name": "A",
                "position": pos_A,
                "axis": unit(np.array([0.500, -0.866, 0.000], dtype=float)),
                "upper_length": 0.177,
                "upper_mass": 0.100,
                "lower_length": 0.400,
                "lower_mass": 0.050,
                "theta_min": -1.5708, # -90 grad
                "theta_max": 0.0873, # 5 grad
                "i": 20,
                "eta": 0.85,
                "Jm": 0.0,
                "Jg": 0.0,
                "EF_offset_angle": 0,
                "EF_offset_radius": 0.0045
            },
            {
                "name": "B",
                "position": pos_B,
                "axis": unit(np.array([0.500, 0.866, 0.000], dtype=float)),
                "upper_length": 0.177,
                "upper_mass": 0.100,
                "lower_length": 0.400,
                "lower_mass": 0.050,
                "theta_min": -1.5708, # -90 grad
                "theta_max": 0.0873, # 5 grad
                "i": 20,
                "eta": 0.85,
                "Jm": 0.0,
                "Jg": 0.0,
                "EF_offset_angle": 2.0943951023931953, # 120 grad
                "EF_offset_radius": 0.0045
            },
            {
                "name": "C",
                "position": pos_C,
                "axis": unit(np.array([-1, 0.000, 0.000], dtype=float)),
                "upper_length": 0.177,
                "upper_mass": 0.100,
                "lower_length": 0.400,
                "lower_mass": 0.050,
                "theta_min": -1.5708, # -90 grad
                "theta_max": 0.0873, # 5 grad
                "i": 20,
                "eta": 0.85,
                "Jm": 0.0,
                "Jg": 0.0,
                "EF_offset_angle": -2.0943951023931953, # -120 grad
                "EF_offset_radius": 0.0045
            }
        ]

        self.upper_arm_length = self.motors[0]["upper_length"]
        self.lower_arm_length = self.motors[0]["lower_length"]

    def set_val(self, key, value):
        """Hilfsfunktion für die GUI, um Werte in dicts oder als direkte Attribute zu schreiben."""
        if hasattr(self, "global_data") and key in self.global_data:
            self.global_data[key] = value
        elif hasattr(self, "workspace") and key in self.workspace:
            self.workspace[key] = value
        else:
            setattr(self, key, value)

# Erstelle ein globales Singleton-Objekt.
# Dieses Objekt (als Objekt statt Klasse) kann nun projektweit importiert werden.
robot_config = RobotConfig()
