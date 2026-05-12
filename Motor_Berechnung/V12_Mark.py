import json
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class Robot:
    #==================================
    def __init__(self, config_path):
        config_data = self.load_json(config_path)

        self.global_data = self.create_global_object(config_data["global"])
        self.workspace = self.create_workspace_object(config_data["workspace"])
        self.motors = self.create_motors_object(config_data["motors"])

        self.upper_arm_length = self.motors[0]["upper_length"]
        self.lower_arm_length = self.motors[0]["lower_length"]
        self.robot_center = self.compute_robot_center()

        self.trajectory = self.load_trajectory_csv(self.global_data["trajectory_csv"])
        self.path_points = self.create_path_points_from_trajectory(self.trajectory)

    #==================================
    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    #==================================
    def load_csv_rows(self, path):
        with open(path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSV enthält keine Kopfzeile")

            return list(reader)

    #==================================
    def create_vector_object_from_list(self, values, name):
        if len(values) != 3:
            raise ValueError(f"{name} muss genau 3 Werte enthalten")
        return np.array(values, dtype=float)

    #==================================
    def create_vector_object_from_row(self, row, x_name, y_name, z_name):
        return np.array([
            float(row[x_name]),
            float(row[y_name]),
            float(row[z_name])
        ], dtype=float)

    #==================================
    def create_range_object(self, values, name):
        if len(values) != 2:
            raise ValueError(f"{name} muss genau 2 Werte enthalten")
        return {
            "min": float(values[0]),
            "max": float(values[1]),
        }

    #==================================
    def create_global_object(self, global_data):
        return {
            "gravity": self.create_vector_object_from_list(global_data["gravity"], "global.gravity"),
            "payload_mass": float(global_data["payload_mass"]),
            "singularity_margin_deg": float(global_data["singularity_margin_deg"]),
            "trajectory_csv": str(global_data["trajectory_csv"]),
        }

    #==================================
    def create_workspace_object(self, workspace_data):
        return {
            "resolution": int(workspace_data["resolution"]),
            "range_x": self.create_range_object(workspace_data["range_x"], "workspace.range_x"),
            "range_y": self.create_range_object(workspace_data["range_y"], "workspace.range_y"),
            "range_z": self.create_range_object(workspace_data["range_z"], "workspace.range_z"),
        }

    #==================================
    def create_motor_object(self, name, motor_data):
        axis = self.create_vector_object_from_list(motor_data["axis"], f"motors.{name}.axis")
        axis = unit(axis)

        return {
            "name": name,
            "position": self.create_vector_object_from_list(motor_data["position"], f"motors.{name}.position"),
            "axis": axis,
            "upper_length": float(motor_data["upper_length"]),
            "upper_mass": float(motor_data["upper_mass"]),
            "lower_length": float(motor_data["lower_length"]),
            "lower_mass": float(motor_data["lower_mass"]),
            "theta_min": float(motor_data["theta_min"]),
            "theta_max": float(motor_data["theta_max"]),
            "i": int(motor_data["i"]),
        }

    #==================================
    def create_motors_object(self, motors_data):
        return [
            self.create_motor_object("A", motors_data["A"]),
            self.create_motor_object("B", motors_data["B"]),
            self.create_motor_object("C", motors_data["C"]),
        ]

    #==================================
    def compute_robot_center(self):
        return np.mean([motor["position"] for motor in self.motors], axis=0)

    #==================================
    def validate_trajectory_row(self, row):
        required_columns = [
            "t",
            "x", "y", "z",
            "vx", "vy", "vz",
            "ax", "ay", "az",
            "jx", "jy", "jz",
            "tx", "ty", "tz",
            "nx", "ny", "nz",
            "bx", "by", "bz",
            "kappa",
            "ftx", "fty", "ftz",
            "fnx", "fny", "fnz",
            "fx", "fy", "fz",
        ]

        for column in required_columns:
            if column not in row:
                raise ValueError(f"Fehlende Spalte in trajectory CSV: {column}")

    #==================================
    def create_trajectory_point_object(self, row):
        self.validate_trajectory_row(row)

        return {
            "time": float(row["t"]),
            "position": self.create_vector_object_from_row(row, "x", "y", "z"),
            "velocity": self.create_vector_object_from_row(row, "vx", "vy", "vz"),
            "acceleration": self.create_vector_object_from_row(row, "ax", "ay", "az"),
            "jerk": self.create_vector_object_from_row(row, "jx", "jy", "jz"),
            "tangent": self.create_vector_object_from_row(row, "tx", "ty", "tz"),
            "normal": self.create_vector_object_from_row(row, "nx", "ny", "nz"),
            "binormal": self.create_vector_object_from_row(row, "bx", "by", "bz"),
            "curvature": float(row["kappa"]),
            "tangential_force": self.create_vector_object_from_row(row, "ftx", "fty", "ftz"),
            "normal_force": self.create_vector_object_from_row(row, "fnx", "fny", "fnz"),
            "force": self.create_vector_object_from_row(row, "fx", "fy", "fz"),
        }

    #==================================
    def load_trajectory_csv(self, path):
        rows = self.load_csv_rows(path)
        points = []

        for row in rows:
            points.append(self.create_trajectory_point_object(row))

        return {
            "count": len(points),
            "points": points,
        }

    #==================================
    def create_path_points_from_trajectory(self, trajectory):
        return np.array([point["position"] for point in trajectory["points"]], dtype=float)


# =========================================================
# GRUNDLAGEN
# =========================================================

def norm(v):
    return np.linalg.norm(v)

#==================================
def unit(v):
    n = norm(v)
    if n == 0:
        raise ValueError("Nullvektor kann nicht normiert werden.")
    return v / n

#==================================
def sphere_sphere_intersection(A, RA, B, RB):
    AB = B - A
    c = norm(AB)

    if c == 0:
        raise ValueError("Die Kugelmittelpunkte A und B dürfen nicht identisch sein.")

    if c > RA + RB:
        raise ValueError(
            f"Die Kugeln schneiden sich nicht: Abstand {c:.6f} > RA+RB {RA + RB:.6f}"
        )

    if c < abs(RA - RB):
        raise ValueError(
            f"Eine Kugel liegt in der anderen: Abstand {c:.6f} < |RA-RB| {abs(RA - RB):.6f}"
        )

    e = unit(AB)
    d = (RA**2 - RB**2 + c**2) / (2 * c)
    h2 = RA**2 - d**2
    h = np.sqrt(max(h2, 0.0))
    N = A + d * e

    return N, e, h

#==================================
def plane_plane_intersection(n1, p1, n2, p2):
    u = np.cross(n1, n2)
    u_norm = np.dot(u, u)

    if u_norm == 0:
        raise ValueError("Die Ebenen sind parallel oder identisch.")

    c1 = np.dot(n1, p1)
    c2 = np.dot(n2, p2)
    P0 = (c1 * np.cross(n2, u) + c2 * np.cross(u, n1)) / u_norm

    return P0, u

#==================================
def line_circle_intersection(P0, u, center, r):
    w = P0 - center
    A = np.dot(u, u)
    Bq = 2 * np.dot(w, u)
    C = np.dot(w, w) - r**2
    disc = Bq**2 - 4 * A * C

    if disc < 0:
        raise ValueError("Gerade schneidet den Kreis nicht.")

    disc = max(disc, 0.0)
    lam1 = (-Bq + np.sqrt(disc)) / (2 * A)
    lam2 = (-Bq - np.sqrt(disc)) / (2 * A)

    P1 = P0 + lam1 * u
    P2 = P0 + lam2 * u

    return P1, P2

#==================================
def get_upper_geometry_from_motorposition(motorposition):
    B = np.array(motorposition["position"], dtype=float)
    nB = unit(np.array(motorposition["axis"], dtype=float))
    circle_center = B
    plane_point = B

    return B, nB, circle_center, plane_point

#==================================
def select_lower_point(P1, P2):
    return P1 if P1[2] < P2[2] else P2

#==================================
def calculate_motor_angle(circle_center, motor_axis, point, zero_direction):
    motor_axis = unit(motor_axis)
    zero_direction = unit(zero_direction)
    zero_direction = zero_direction - np.dot(zero_direction, motor_axis) * motor_axis
    zero_direction = unit(zero_direction)

    perp_direction = unit(np.cross(motor_axis, zero_direction))
    r_vec = point - circle_center

    x_local = np.dot(r_vec, zero_direction)
    y_local = np.dot(r_vec, perp_direction)

    angle_rad = np.arctan2(y_local, x_local)
    angle_deg = np.degrees(angle_rad)

    return angle_rad, angle_deg


# =========================================================
# INVERSE KINEMATIK
# =========================================================

def solve_single_arm_ik(A, motorposition, upper_arm_length, lower_arm_length, robot_center):
    A = np.array(A, dtype=float)
    robot_center = np.array(robot_center, dtype=float)

    B, nB, circle_center, plane_point = get_upper_geometry_from_motorposition(motorposition)

    RA = lower_arm_length
    RB = upper_arm_length
    r = upper_arm_length

    N, e, h = sphere_sphere_intersection(A, RA, B, RB)
    P0, u = plane_plane_intersection(e, N, nB, plane_point)
    P1, P2 = line_circle_intersection(P0, u, circle_center, r)
    elbow = select_lower_point(P1, P2)

    zero_direction = B - robot_center
    angle_rad, angle_deg = calculate_motor_angle(circle_center, nB, elbow, zero_direction)

    lower_rod_vector = elbow - A
    lower_rod_direction = unit(lower_rod_vector)

    return {
        "motor_center": B,
        "motor_axis": nB,
        "circle_center": circle_center,
        "elbow": elbow,
        "angle_rad": angle_rad,
        "angle_deg": angle_deg,
        "zero_direction": unit(zero_direction),
        "lower_rod_vector": lower_rod_vector,
        "lower_rod_direction": lower_rod_direction,
        "lower_rod_length": norm(lower_rod_vector),
    }

#==================================
def inverse_kinematics_delta(A, motors, upper_arm_length, lower_arm_length, robot_center):
    results = []

    for motor in motors:
        try:
            result = solve_single_arm_ik(
                A,
                motor,
                upper_arm_length,
                lower_arm_length,
                robot_center=robot_center
            )
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
                "angle_deg": None,
                "zero_direction": None,
                "lower_rod_vector": None,
                "lower_rod_direction": None,
                "lower_rod_length": None,
            }

        results.append(result)

    return results

#==================================
def print_unreachable_points(path_points, all_results):
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

#==================================
def print_reachable_summary(path_points, all_results):
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


# =========================================================
# PLOTTING
# =========================================================

def get_circle_basis(normal):
    normal = unit(normal)

    if abs(normal[0]) < 0.9:
        v = np.cross(normal, [1.0, 0.0, 0.0])
    else:
        v = np.cross(normal, [0.0, 1.0, 0.0])

    v = unit(v)
    w = unit(np.cross(normal, v))

    return v, w

#==================================
def plot_circle(ax, center, normal, radius, color="orange", linewidth=1.2, alpha=0.7):
    normal = unit(normal)
    v, w = get_circle_basis(normal)
    t = np.linspace(0, 2*np.pi, 120)
    circle = np.array([
        center + radius * (np.cos(tt) * v + np.sin(tt) * w)
        for tt in t
    ])
    ax.plot(circle[:, 0], circle[:, 1], circle[:, 2], color=color, linewidth=linewidth, alpha=alpha)

#==================================
def plot_zero_plane(ax, origin, motor_axis, zero_direction, size=0.2, alpha=0.25):
    motor_axis = unit(motor_axis)

    zero_direction = zero_direction - np.dot(zero_direction, motor_axis) * motor_axis
    zero_direction = unit(zero_direction)

    a = 0.6 * size * zero_direction
    b = 0.35 * size * motor_axis

    corners = np.array([
        origin - a - b,
        origin + a - b,
        origin + a + b,
        origin - a + b
    ])

    poly = Poly3DCollection([corners], alpha=alpha)
    poly.set_facecolor("cyan")
    poly.set_edgecolor("black")
    ax.add_collection3d(poly)

    line = np.array([origin, origin + 0.6 * size * zero_direction])
    ax.plot(line[:, 0], line[:, 1], line[:, 2], color="cyan", linewidth=3)

#==================================
def plot_robot(ax, A, motors, results, upper_arm_length, robot_center, path_points=None, title=None):
    A = np.array(A, dtype=float)
    robot_center = np.array(robot_center, dtype=float)

    ax.cla()

    base_points = np.array([m["position"] for m in motors] + [motors[0]["position"]])
    ax.plot(base_points[:, 0], base_points[:, 1], base_points[:, 2],
            color="black", linewidth=2, label="Basisdreieck")

    if path_points is not None:
        path_points = np.array(path_points)
        ax.plot(path_points[:, 0], path_points[:, 1], path_points[:, 2],
                linestyle=":", linewidth=1.5, label="Bahn")

    ax.scatter(*A, s=120, color="magenta", label="Endeffektor A")
    ax.scatter(*robot_center, s=70, color="black", label="Roboterzentrum")

    for i, (motor, res) in enumerate(zip(motors, results)):
        if not res["reachable"]:
            continue

        B = res["motor_center"]
        elbow = res["elbow"]
        axis = res["motor_axis"]
        zero_direction = B - robot_center

        ax.scatter(*B, s=70, color="red")
        plot_circle(ax, B, axis, upper_arm_length)

        upper_line = np.array([B, elbow])
        ax.plot(
            upper_line[:, 0], upper_line[:, 1], upper_line[:, 2],
            linewidth=3, label="oberer Arm" if i == 0 else None
        )

        lower_line = np.array([elbow, A])
        ax.plot(
            lower_line[:, 0], lower_line[:, 1], lower_line[:, 2],
            linestyle="--", linewidth=2, label="unterer Arm" if i == 0 else None
        )

        ax.scatter(*elbow, s=45, color="blue")

        axis_vis = np.array([B - 0.8 * axis, B + 0.8 * axis])
        ax.plot(axis_vis[:, 0], axis_vis[:, 1], axis_vis[:, 2],
                linewidth=2, alpha=0.7, color="green")

        plot_zero_plane(
            ax=ax,
            origin=B,
            motor_axis=axis,
            zero_direction=zero_direction,
            size=0.4,
            alpha=0.22
        )

    ax.set_box_aspect([1, 1, 1])
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-1, 3)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    if title:
        ax.set_title(title)

    ax.legend(loc="upper right")

#==================================
def animate_reachable_poses(robot, path_points, all_results, save_gif=False, gif_name="delta_robot_animation.gif"):
    reachable_indices = [
        i for i, results in enumerate(all_results)
        if all(res["reachable"] for res in results)
    ]

    if len(reachable_indices) == 0:
        print("Keine vollständig erreichbaren Posen für Animation vorhanden.")
        return

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(111, projection="3d")

    def update(frame):
        print(f"Frame {frame+1}/{len(reachable_indices)} wird gezeichnet")

        point_index = reachable_indices[frame]
        A = path_points[point_index]
        results = all_results[point_index]

        plot_robot(
            ax=ax,
            A=A,
            motors=robot.motors,
            results=results,
            upper_arm_length=robot.upper_arm_length,
            robot_center=robot.robot_center,
            path_points=path_points,
            title=f"Delta-Roboter | Punkt {point_index}"
        )

        angle_text = "\n".join(
            f"{res['name']}: {res['angle_deg']:.1f}°"
            for res in results
            if res["reachable"] and res["angle_deg"] is not None
        )

        ax.text2D(0.02, 0.98, angle_text, transform=ax.transAxes, va="top")

    ani = FuncAnimation(
        fig,
        update,
        frames=len(reachable_indices),
        interval=5,
        blit=False,
        repeat=True
    )

    if save_gif:
        ani.save(gif_name, writer=PillowWriter(fps=200))
        print(f"GIF gespeichert: {gif_name}")

    plt.close(fig)


# =========================================================
# Plot Winkel
# =========================================================

def plot_motor_angles(robot, all_results):
    t_values = []
    phi_1 = []
    phi_2 = []
    phi_3 = []

    for i, results in enumerate(all_results):
        t = robot.trajectory["points"][i]["time"]
        t_values.append(t)

        phi_1.append(results[0]["angle_deg"] if results[0]["reachable"] else np.nan)
        phi_2.append(results[1]["angle_deg"] if results[1]["reachable"] else np.nan)
        phi_3.append(results[2]["angle_deg"] if results[2]["reachable"] else np.nan)

    plt.figure(figsize=(10, 6))

    plt.plot(t_values, phi_1, label="φ1")
    plt.plot(t_values, phi_2, label="φ2")
    plt.plot(t_values, phi_3, label="φ3")

    plt.xlabel("t [s]")
    plt.ylabel("Motorwinkel [deg]")
    plt.title("Motorwinkel über der Zeit")
    plt.grid(True)
    plt.legend()

    plt.show()  

# =========================================================
# MAIN
# =========================================================

def main():
    robot = Robot("config.json")

    upper_arm_length = robot.upper_arm_length
    lower_arm_length = robot.lower_arm_length
    motors = robot.motors
    robot_center = robot.robot_center
    path_points = robot.path_points

    all_results = []

    for A in path_points:
        results = inverse_kinematics_delta(
            A,
            motors,
            upper_arm_length,
            lower_arm_length,
            robot_center
        )
        all_results.append(results)

    print_reachable_summary(path_points, all_results)
    print_unreachable_points(path_points, all_results)

    plot_motor_angles(robot, all_results)

   # animate_reachable_poses(
   #     robot,
   #     path_points,
   #     all_results,
   #     save_gif=True,
   #     gif_name="delta_robot_animation.gif"
   # )



if __name__ == "__main__":
    main()