import numpy as np
from Motor_Berechnung.math_utilities import unit

class RobotConfig:
    def __init__(self, config_path=None):
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
            "range_x": {"min": -0.4, "max": 0.4},
            "range_y": {"min": -0.4, "max": 0.4},
            "range_z": {"min": -1.3, "max": -0.1}
        }

        pos_A = np.array([0.900, 0.000, 1.500], dtype=float)
        pos_B = np.array([-0.450, 0.779, 1.500], dtype=float)
        pos_C = np.array([-0.450, -0.779, 1.500], dtype=float)

        self.robot_center = np.mean([pos_A, pos_B, pos_C], axis=0)

        self.motors = [
            {
                "name": "A",
                "position": pos_A,
                "axis": unit(np.array([0.000, 1.000, 0.000], dtype=float)),
                "upper_length": 1.000,
                "upper_mass": 0.600,
                "lower_length": 2.000,
                "lower_mass": 0.150,
                "theta_min": -180.0,
                "theta_max": 180.0,
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
                "axis": unit(np.array([-0.866, -0.500, 0.000], dtype=float)),
                "upper_length": 1.000,
                "upper_mass": 0.600,
                "lower_length": 2.000,
                "lower_mass": 0.150,
                "theta_min": -180.0,
                "theta_max": 180.0,
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
                "axis": unit(np.array([0.866, -0.500, 0.000], dtype=float)),
                "upper_length": 1.000,
                "upper_mass": 0.600,
                "lower_length": 2.000,
                "lower_mass": 0.150,
                "theta_min": -180.0,
                "theta_max": 180.0,
                "i": 20,
                "eta": 0.85,
                "Jm": 0.0,
                "Jg": 0.0,
                "EF_offset_angle": -2.0943951023931953, # -120 grad
                "EF_offset_radius": 0.0045
            }
        ]

        self.upper_arm_length = self.motors[0]["upper_length"]
        self.upper_arm_mass   = self.motors[0]["upper_mass"]
        self.lower_arm_length = self.motors[0]["lower_length"]
        self.lower_arm_mass   = self.motors[0]["lower_mass"]