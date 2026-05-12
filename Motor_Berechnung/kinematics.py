import numpy as np
from math_utilities import (
    sphere_sphere_intersection,
    plane_plane_intersection,
    line_circle_intersection,
    norm,
    unit
)

class KinematicsSolver:
    def __init__(self, robot_config):
        self.upper_arm_length = robot_config.upper_arm_length
        self.lower_arm_length = robot_config.lower_arm_length
        self.robot_center = robot_config.robot_center
        self.motors = robot_config.motors

    def get_upper_geometry_from_motorposition(self, motorposition):
        B = np.array(motorposition["position"], dtype=float)
        nB = unit(np.array(motorposition["axis"], dtype=float))
        circle_center = B
        plane_point = B
        return B, nB, circle_center, plane_point

    def select_lower_point(self, P1, P2):
        return P1 if P1[2] < P2[2] else P2

    def calculate_motor_angle_rad(self, circle_center, motor_axis, point, zero_direction):
        motor_axis = unit(motor_axis)
        zero_direction = unit(zero_direction)

        zero_direction = zero_direction - np.dot(zero_direction, motor_axis) * motor_axis
        zero_direction = unit(zero_direction)

        perp_direction = unit(np.cross(motor_axis, zero_direction))
        r_vec = point - circle_center

        x_local = np.dot(r_vec, zero_direction)
        y_local = np.dot(r_vec, perp_direction)

        angle_rad = np.arctan2(y_local, x_local)
        return angle_rad

    def solve_single_arm_ik(self, A, motorposition):
        A = np.array(A, dtype=float)
        robot_center = np.array(self.robot_center, dtype=float)

        B, nB, circle_center, plane_point = self.get_upper_geometry_from_motorposition(motorposition)

        RA = self.lower_arm_length
        RB = self.upper_arm_length
        r = self.upper_arm_length

        N, e, h = sphere_sphere_intersection(A, RA, B, RB)
        P0, u = plane_plane_intersection(e, N, nB, plane_point)
        P1, P2 = line_circle_intersection(P0, u, circle_center, r)
        elbow = self.select_lower_point(P1, P2)
        upper_arm_vector = elbow - B
        upper_arm_direction = unit(upper_arm_vector)

        zero_direction = B - robot_center
        angle_rad = self.calculate_motor_angle_rad(circle_center, nB, elbow, zero_direction)

        lower_rod_vector = elbow - A
        lower_rod_direction = unit(lower_rod_vector)

        return {
            "motor_center": B,
            "motor_axis": nB,
            "circle_center": circle_center,
            "elbow": elbow,
            "angle_rad": angle_rad,
            "zero_direction": unit(zero_direction),

            "upper_arm_vector": upper_arm_vector,
            "upper_arm_direction": upper_arm_direction,

            "lower_rod_vector": lower_rod_vector,
            "lower_rod_direction": lower_rod_direction,
            "lower_rod_length": norm(lower_rod_vector),
        }

    def solve_point(self, A):
        results = []
        for motor in self.motors:
            try:
                result = self.solve_single_arm_ik(A, motor)
                result["name"] = motor["name"]
                result["reachable"] = True
                result["error"] = None
            except Exception as error:
                result = {
                    "name": motor["name"],
                    "reachable": False,
                    "error": str(error),
                    "motor_center": motor["position"],
                    "motor_axis": motor["axis"],
                    "circle_center": None,
                    "elbow": None,
                    "angle_rad": None,
                    "zero_direction": None,
                    "lower_rod_vector": None,
                    "lower_rod_direction": None,
                    "lower_rod_length": None,
                }
            results.append(result)
        return results

    def solve_trajectory(self, path_points):
        all_results = []
        for A in path_points:
            all_results.append(self.solve_point(A))
        return all_results

    def print_unreachable_points(self, path_points, all_results):
        print("====================================================")
        print("NICHT ERREICHBARE PUNKTE")
        print("====================================================")
        unreachable_count = 0
        for i, (A, results) in enumerate(zip(path_points, all_results)):
            for res in results:
                if not res["reachable"]:
                    unreachable_count += 1
                    print(f"Index                : {i}")
                    print(f"Motor                : {res['name']}")
                    print(f"Punkt A              : {np.round(A, 6)}")
                    print(f"Fehler               : {res['error']}")
                    print()
        if unreachable_count == 0:
            print("Alle Punkte sind erreichbar.")
            print()

    def print_reachable_summary(self, path_points, all_results):
        total_points = len(path_points)
        fully_reachable_points = 0
        for results in all_results:
            if all(res["reachable"] for res in results):
                fully_reachable_points += 1

        print("====================================================")
        print("ERREICHBARKEIT")
        print("====================================================")
        print(f"Gesamtpunkte         : {total_points}")
        print(f"Voll erreichbar      : {fully_reachable_points}")
        print(f"Nichterreichbar      : {total_points - fully_reachable_points}")
        print()
