import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from math_utilities import unit, get_circle_basis
import os

class Visualizer:
    def __init__(self, robot_config, trajectory, dynamics_solver):
        self.robot_config = robot_config
        self.trajectory = trajectory
        self.dynamics_solver = dynamics_solver
        self.upper_arm_length = robot_config.upper_arm_length
        self.robot_center = robot_config.robot_center
        self.motors = robot_config.motors
        self.path_points = trajectory.path_points

    def plot_circle(self, ax, center, normal, radius, color="orange", linewidth=1.2, alpha=0.7):
        normal = unit(normal)
        v, w = get_circle_basis(normal)
        t = np.linspace(0, 2*np.pi, 120)

        circle = np.array([
            center + radius * (np.cos(tt) * v + np.sin(tt) * w)
            for tt in t
        ])
        ax.plot(circle[:, 0], circle[:, 1], circle[:, 2], color=color, linewidth=linewidth, alpha=alpha)

    def plot_zero_plane(self, ax, origin, motor_axis, zero_direction, size=1.2, alpha=0.25):
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

        line = np.array([origin, origin + 0.9 * size * zero_direction])
        ax.plot(line[:, 0], line[:, 1], line[:, 2], color="cyan", linewidth=3)

    def plot_robot(self, ax, A, results, title=None):
        A = np.array(A, dtype=float)
        robot_center = np.array(self.robot_center, dtype=float)

        ax.cla()

        base_points = np.array([m["position"] for m in self.motors] + [self.motors[0]["position"]])
        ax.plot(base_points[:, 0], base_points[:, 1], base_points[:, 2],
                color="black", linewidth=2, label="Basisdreieck")

        if self.path_points is not None:
            path_points = np.array(self.path_points)
            ax.plot(path_points[:, 0], path_points[:, 1], path_points[:, 2],
                    linestyle=":", linewidth=1.5, label="Bahn")

        ax.scatter(*A, s=120, color="magenta", label="Endeffektor A")
        ax.scatter(*robot_center, s=70, color="black", label="Roboterzentrum")

        for i, (motor, res) in enumerate(zip(self.motors, results)):
            if not res["reachable"]:
                continue

            B = res["motor_center"]
            elbow = res["elbow"]
            axis = res["motor_axis"]
            zero_direction = B - robot_center

            ax.scatter(*B, s=70, color="red")
            self.plot_circle(ax, B, axis, self.upper_arm_length)

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

            self.plot_zero_plane(
                ax=ax,
                origin=B,
                motor_axis=axis,
                zero_direction=zero_direction,
                size=1.4,
                alpha=0.22
            )

        ax.set_box_aspect([1, 1, 1])
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_zlim(-1.0, 2)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        if title:
            ax.set_title(title)

        ax.legend(loc="upper right")

    def animate_reachable_poses(self, all_results, save_gif=False, gif_name="delta_robot_animation.gif"):
        reachable_indices = [
            i for i, results in enumerate(all_results)
            if all(res["reachable"] for res in results)
        ]

        if len(reachable_indices) == 0:
            print("Keine vollständig erreichbaren Posen für Animation vorhanden.")
            return

        target_duration_s = 5
        target_fps = 20
        target_frame_count = target_duration_s * target_fps

        step = max(1, len(reachable_indices) // target_frame_count)
        sampled_indices = reachable_indices[::step]

        print(f"Originale Frames      : {len(reachable_indices)}")
        print(f"Verwendete GIF-Frames : {len(sampled_indices)}")
        print(f"Jeder {step}. Frame wird verwendet")

        fig = plt.figure(figsize=(9, 8))
        ax = fig.add_subplot(111, projection="3d")

        def update(frame):
            print(f"Frame {frame + 1}/{len(sampled_indices)} wird gezeichnet")
            point_index = sampled_indices[frame]
            A = self.path_points[point_index]
            results = all_results[point_index]

            self.plot_robot(
                ax=ax,
                A=A,
                results=results,
                title=f"Delta-Roboter | Punkt {point_index}"
            )

            angle_text = "\n".join(
                f"{res['name']}: {res['angle_rad']:.3f} rad"
                for res in results
                if res["reachable"] and res["angle_rad"] is not None
            )
            ax.text2D(0.02, 0.98, angle_text, transform=ax.transAxes, va="top")

        ani = FuncAnimation(
            fig,
            update,
            frames=len(sampled_indices),
            interval=50,
            blit=False,
            repeat=True
        )

        if save_gif:
            output_dir = "output"
            plot_dir = os.path.join(output_dir, "plots")
            os.makedirs(plot_dir, exist_ok=True)
        
            gif_path = os.path.join(plot_dir, gif_name)
        
            ani.save(gif_path, writer=PillowWriter(fps=target_fps))
            print(f"GIF gespeichert: {gif_path}")

        plt.close(fig)

    def plot_motor_angles(self, all_results):
        omega_all = self.dynamics_solver.compute_all_motor_omega(all_results)
        alpha_all = self.dynamics_solver.compute_all_motor_alpha(omega_all)

        t = []
        phi_1, phi_2, phi_3 = [], [], []
        omega_1, omega_2, omega_3 = [], [], []
        alpha_1, alpha_2, alpha_3 = [], [], []

        for i, results in enumerate(all_results):
            t.append(self.trajectory.points[i]["time"])

            phi_1.append(results[0]["angle_rad"] if results[0]["reachable"] else np.nan)
            phi_2.append(results[1]["angle_rad"] if results[1]["reachable"] else np.nan)
            phi_3.append(results[2]["angle_rad"] if results[2]["reachable"] else np.nan)

            omega_1.append(omega_all[i][0])
            omega_2.append(omega_all[i][1])
            omega_3.append(omega_all[i][2])

            alpha_1.append(alpha_all[i][0])
            alpha_2.append(alpha_all[i][1])
            alpha_3.append(alpha_all[i][2])

        fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

        axs[0].plot(t, phi_1, label="phi_1")
        axs[0].plot(t, phi_2, label="phi_2")
        axs[0].plot(t, phi_3, label="phi_3")
        axs[0].set_ylabel("Winkel [rad]")
        axs[0].grid()
        axs[0].legend()

        axs[1].plot(t, omega_1, label="omega_1")
        axs[1].plot(t, omega_2, label="omega_2")
        axs[1].plot(t, omega_3, label="omega_3")
        axs[1].set_ylabel("omega [rad/s]")
        axs[1].grid()
        axs[1].legend()

        axs[2].plot(t, alpha_1, label="alpha_1")
        axs[2].plot(t, alpha_2, label="alpha_2")
        axs[2].plot(t, alpha_3, label="alpha_3")
        axs[2].set_ylabel("alpha [rad/s²]")
        axs[2].set_xlabel("t [s]")
        axs[2].grid()
        axs[2].legend()

        plt.tight_layout()
        # plt.show()

    def save_motor_angles_plot(self, all_results, filename="motor_angles.png"):
        omega_all = self.dynamics_solver.compute_all_motor_omega(all_results)
        alpha_all = self.dynamics_solver.compute_all_motor_alpha(omega_all)

        t = []
        phi_1, phi_2, phi_3 = [], [], []
        omega_1, omega_2, omega_3 = [], [], []
        alpha_1, alpha_2, alpha_3 = [], [], []

        for i, results in enumerate(all_results):
            t.append(self.trajectory.points[i]["time"])

            phi_1.append(results[0]["angle_rad"] if results[0]["reachable"] else np.nan)
            phi_2.append(results[1]["angle_rad"] if results[1]["reachable"] else np.nan)
            phi_3.append(results[2]["angle_rad"] if results[2]["reachable"] else np.nan)

            omega_1.append(omega_all[i][0])
            omega_2.append(omega_all[i][1])
            omega_3.append(omega_all[i][2])

            alpha_1.append(alpha_all[i][0])
            alpha_2.append(alpha_all[i][1])
            alpha_3.append(alpha_all[i][2])

        fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

        axs[0].plot(t, phi_1, label="phi_1")
        axs[0].plot(t, phi_2, label="phi_2")
        axs[0].plot(t, phi_3, label="phi_3")
        axs[0].set_ylabel("phi [rad]")
        axs[0].set_title("Motorwinkel")
        axs[0].grid(True)
        axs[0].legend()

        axs[1].plot(t, omega_1, label="omega_1")
        axs[1].plot(t, omega_2, label="omega_2")
        axs[1].plot(t, omega_3, label="omega_3")
        axs[1].set_ylabel("omega [rad/s]")
        axs[1].set_title("Winkelgeschwindigkeit")
        axs[1].grid(True)
        axs[1].legend()

        axs[2].plot(t, alpha_1, label="alpha_1")
        axs[2].plot(t, alpha_2, label="alpha_2")
        axs[2].plot(t, alpha_3, label="alpha_3")
        axs[2].set_ylabel("alpha [rad/s²]")
        axs[2].set_xlabel("t [s]")
        axs[2].set_title("Winkelbeschleunigung")
        axs[2].grid(True)
        axs[2].legend()

        fig.tight_layout()

        output_dir = self.robot_config.output_dir if hasattr(self.robot_config, "output_dir") else "output"
        plot_dir = os.path.join(output_dir, "plots")
        os.makedirs(plot_dir, exist_ok=True)

        filepath = os.path.join(plot_dir, filename)

        fig.savefig(filepath, dpi=300, bbox_inches="tight")
        plt.close(fig)

        print(f"Plot gespeichert: {filepath}")
