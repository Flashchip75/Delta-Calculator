import numpy as np
from Motor_Berechnung.math_utilities import (
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
        self.workspace = robot_config.workspace

    def get_upper_geometry_from_motorposition(self, motorposition):
        B = np.array(motorposition["position"], dtype=float)
        nB = unit(np.array(motorposition["axis"], dtype=float))
        circle_center = B
        plane_point = B
        return B, nB, circle_center, plane_point

    def select_lower_point(self, P1, P2):
        return P1 if P1[2] < P2[2] else P2
    
    def validate_motor_angle(self, angle_rad, motorposition):
        theta_min = motorposition.get("theta_min")
        theta_max = motorposition.get("theta_max")

        if theta_min is None or theta_max is None:
            raise ValueError(
                f"Motor {motorposition['name']} hat keine theta_min/theta_max Werte."
            )

        if angle_rad < theta_min or angle_rad > theta_max:
            raise ValueError(
                f"Motor {motorposition['name']}: Winkel {np.degrees(angle_rad):.2f}° "
                f"außerhalb der Grenzen "
                f"[{np.degrees(theta_min):.2f}°, {np.degrees(theta_max):.2f}°]"
            )

        return angle_rad

    def calculate_motor_angle_rad(self, circle_center, motor_axis, point, zero_direction):
        motor_axis = unit(motor_axis)
        zero_direction = unit(zero_direction)

        zero_direction = zero_direction - np.dot(zero_direction, motor_axis) * motor_axis
        zero_direction = unit(zero_direction)

        perp_direction = unit(np.cross(motor_axis, zero_direction))
        r_vec = point - circle_center

        x_local = np.dot(r_vec, zero_direction)
        y_local = np.dot(r_vec, perp_direction)

        angle_rad = -np.arctan2(y_local, x_local)
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
        angle_rad = self.validate_motor_angle(angle_rad, motorposition)

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
        A = np.array(A, dtype=float)

        for motor in self.motors:
            try:
                ef_offset_radius = motor.get("EF_offset_radius", 0.0)
                ef_offset_angle = motor.get("EF_offset_angle", 0.0)

                ef_offset = np.array([
                    ef_offset_radius * np.cos(ef_offset_angle),
                    ef_offset_radius * np.sin(ef_offset_angle),
                    0.0], dtype=float)

                A_motor = A + ef_offset

                result = self.solve_single_arm_ik(A_motor, motor)
                result["name"] = motor["name"]
                result["reachable"] = True
                result["error"] = None
                result["target_point_with_offset"] = A_motor
                result["ef_offset"] = ef_offset

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
                    "target_point_with_offset": None,
                    "ef_offset": None,
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


    def generate_workspace_grid(self):
        resolution = int(self.workspace["resolution"])

        x_values = np.linspace(self.workspace["range_x"]["min"], self.workspace["range_x"]["max"], resolution)
        y_values = np.linspace(self.workspace["range_y"]["min"], self.workspace["range_y"]["max"], resolution)
        z_values = np.linspace(self.workspace["range_z"]["min"], self.workspace["range_z"]["max"], resolution)

        X, Y, Z = np.meshgrid(x_values, y_values, z_values, indexing="ij")

        return np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))


    def is_point_in_rough_workspace(self, point):
        point = np.array(point, dtype=float)

        for motor in self.motors:
            motor_position = np.array(motor["position"], dtype=float)

            upper_length = motor["upper_length"]
            lower_length = motor["lower_length"]

            distance = norm(point - motor_position)

            max_reach = upper_length + lower_length
            min_reach = abs(lower_length - upper_length)

            if distance > max_reach:
                return False

            if distance < min_reach:
                return False

        return True

    def solve_workspace(self):
        workspace_grid_points = self.generate_workspace_grid()


        rough_workspace_points = []
        reachable_workspace_points = []
        unreachable_workspace_points = []
        workspace_results = []

        for point in workspace_grid_points:
            if not self.is_point_in_rough_workspace(point):
                continue

            rough_workspace_points.append(point)

            result = self.solve_point(point)
            is_reachable = all(motor_result["reachable"] for motor_result in result)

            workspace_results.append({
                "point": point,
                "reachable": is_reachable,
                "result": result
            })

            if is_reachable:
                reachable_workspace_points.append(point)
            else:
                unreachable_workspace_points.append(point)

        return (
            np.array(reachable_workspace_points, dtype=float),
            np.array(unreachable_workspace_points, dtype=float),
            np.array(rough_workspace_points, dtype=float),
            workspace_results
        )


    def plot_workspace(self, show_unreachable=False, show_rough_workspace=False):
        import matplotlib.pyplot as plt
        
        reachable_points, unreachable_points, rough_points, workspace_results = self.solve_workspace()

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        if show_rough_workspace and len(rough_points) > 0:
            ax.scatter(
                rough_points[:, 0],
                rough_points[:, 1],
                rough_points[:, 2],
                s=2,
                alpha=0.05,
                label="Grobe Vorauswahl"
            )

        if show_unreachable and len(unreachable_points) > 0:
            ax.scatter(
                unreachable_points[:, 0],
                unreachable_points[:, 1],
                unreachable_points[:, 2],
                s=3,
                alpha=0.1,
                label="Nach Vorauswahl nicht IK-erreichbar"
            )

        if len(reachable_points) > 0:
            ax.scatter(
                reachable_points[:, 0],
                reachable_points[:, 1],
                reachable_points[:, 2],
                s=8,
                alpha=0.8,
                label="IK-erreichbarer Workspace"
            )


        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.set_zlabel("Z [m]")
        ax.set_title("Erreichbarer Workspace des Roboters")
        ax.legend()
        ax.grid(True)

        print(f"Gitterpunkte insgesamt : {len(self.generate_workspace_grid())}")
        print(f"Grobe Vorauswahl       : {len(rough_points)}")
        print(f"IK-erreichbar          : {len(reachable_points)}")
        print(f"Nicht IK-erreichbar    : {len(unreachable_points)}")

        plt.show()

        return reachable_points


    def debug_plot_offset_trajectory(self, path_points):
        import matplotlib.pyplot as plt
    
        path_points = np.array(path_points, dtype=float)
    
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
    
        # Originale Endeffektor-Bahn
        ax.plot(
            path_points[:, 0],
            path_points[:, 1],
            path_points[:, 2],
            label="Originale Bahn A"
        )
    
        # Offset-Bahn pro Motor
        for motor in self.motors:
            radius = motor.get("EF_offset_radius", 0.0)
            angle = motor.get("EF_offset_angle", 0.0)
    
            ef_offset = np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                0.0
            ], dtype=float)
    
            offset_points = path_points + ef_offset
    
            ax.plot(
                offset_points[:, 0],
                offset_points[:, 1],
                offset_points[:, 2],
                label=f"Offset-Bahn Motor {motor['name']}"
            )
    
            # Motorposition markieren
            B = motor["position"]
            ax.scatter(B[0], B[1], B[2], marker="o")
            ax.text(B[0], B[1], B[2], f"Motor {motor['name']}")
    
            # Offset-Richtung am ersten Punkt anzeigen
            A0 = path_points[0]
            A0_offset = A0 + ef_offset
    
            ax.plot(
                [A0[0], A0_offset[0]],
                [A0[1], A0_offset[1]],
                [A0[2], A0_offset[2]],
                linestyle="--"
            )
    
        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.set_zlabel("Z [m]")
        ax.set_title("Debug: Roboterfahrt mit Endeffektor-Offset")
        ax.legend()
        ax.grid(True)
    
        plt.show()