import numpy as np
from math_utilities import build_orthonormal_basis_from_vector
from math_utilities import gradient
import matplotlib.pyplot as plt

class DynamicsSolver:
    def __init__(self, robot_config, trajectory):
        self.upper_arm_length = robot_config.upper_arm_length
        self.trajectory_points = trajectory.points
    
        self.motors = robot_config.motors
        self.g = abs(robot_config.global_data["gravity"][2])
    
        self.motor_transmission = {
            motor["name"]: motor["i"]
            for motor in self.motors
        }
    
        self.motor_axis = {
            motor["name"]: motor["axis"]
            for motor in self.motors
        }

    def get_lower_rod_directions(self, results):
        U = np.column_stack([res["lower_rod_direction"] for res in results])
        return U

    def project_vector_onto_rods(self, vector_quantity, results):
        q = np.array(vector_quantity, dtype=float)
        projections = []
        for res in results:
            u = res["lower_rod_direction"]
            proj = np.dot(q, u)
            projections.append(proj)
        return np.array(projections)

    def solve_rod_scalars(self, vector_quantity, results):
        q = np.array(vector_quantity, dtype=float)  # Skalare Werte der Stabkräfte aufgesplittet
        U = self.get_lower_rod_directions(results)  # Richtungsvektoren der Stäbe

        detU = np.linalg.det(U)
        if abs(detU) < 1e-10:
            raise ValueError(
                "Die Richtungsmatrix der unteren Stäbe ist singulär oder fast singulär. "
                "Die Zerlegung kann nicht eindeutig berechnet werden."
            )

        scalars = np.linalg.solve(U, q)
        reconstructed_vector = U @ scalars
        return scalars, U, reconstructed_vector

    def solve_rod_forces(self, force_vector, results):
        return self.solve_rod_scalars(force_vector, results)

    
    def project_rod_force_tangential_to_upper_arm(self, rod_force_scalar, result):
        lower_rod_direction = np.array(result["lower_rod_direction"], dtype=float)
        upper_arm_direction = np.array(result["upper_arm_direction"], dtype=float)

        lower_rod_norm = np.linalg.norm(lower_rod_direction)
        upper_arm_norm = np.linalg.norm(upper_arm_direction)

        if lower_rod_norm < 1e-12:
            raise ValueError(
                f"lower_rod_direction von Motor {result['name']} ist ungültig."
            )

        if upper_arm_norm < 1e-12:
            raise ValueError(
                f"upper_arm_direction von Motor {result['name']} ist ungültig."
            )

        lower_rod_direction = lower_rod_direction / lower_rod_norm
        upper_arm_direction = upper_arm_direction / upper_arm_norm

        # Kraft, die über den Lower Arm auf das Ellbogengelenk wirkt
        force_on_upper_arm = -rod_force_scalar * lower_rod_direction


        # Tangentialrichtung muss in der Motorebene liegen.
        motor_axis = np.array(result["motor_axis"], dtype=float)
        motor_axis = motor_axis / np.linalg.norm(motor_axis)

        tangent = np.cross(motor_axis, upper_arm_direction)

        tangent_norm = np.linalg.norm(tangent)
        if tangent_norm < 1e-12:
            raise ValueError(
                f"Tangentialrichtung für Motor {result['name']} ungültig."
            )

        tangent = tangent / tangent_norm

        
        tangential_force = np.dot(force_on_upper_arm, tangent)

        return tangential_force
    
    def compute_motor_torque_from_rod_force(self, rod_force_scalar, result):
        tangential_force = self.project_rod_force_tangential_to_upper_arm(
            rod_force_scalar,
            result
        )

        torque_motor = tangential_force * self.upper_arm_length

        return torque_motor
    
    def compute_motor_energy_balance(self, force_vector, velocity_vector, results):
        force_projections = self.project_vector_onto_rods(force_vector, results)
        velocity_projections = self.project_vector_onto_rods(velocity_vector, results)

        rod_forces, U, reconstructed_force = self.solve_rod_forces(force_vector,results)

        rod_velocities = self.project_vector_onto_rods(velocity_vector, results)

        motors_energy = []

        for res, f_i, v_i in zip(results, rod_forces, rod_velocities):
            P_i = f_i * v_i

            T_i = self.compute_motor_torque_from_rod_force(f_i, res)
           
    
            if abs(T_i) < 1e-12:
                omega_i = np.nan
                i_motor = np.nan
            else:
                i_motor = self.motor_transmission[res["name"]]
                omega_i = (-P_i / T_i) * i_motor

            motors_energy.append({
                "name": res["name"],
                "force_projection": np.dot(
                    np.array(force_vector, dtype=float),
                    res["lower_rod_direction"]
                ),
                "velocity_projection": np.dot(
                    np.array(velocity_vector, dtype=float),
                    res["lower_rod_direction"]
                ),
                "rod_force": f_i,
                "rod_velocity": v_i,
                "P_motor": P_i,
                "T_motor": T_i,
                "omega_motor": omega_i,
                "transmission": i_motor
            })

        return {
            "force_projections": force_projections,
            "velocity_projections": velocity_projections,
            "rod_forces": rod_forces,
            "rod_velocities": rod_velocities,
            "U": U,
            "reconstructed_force": reconstructed_force,
            
            "motors": motors_energy
        }

    def compute_all_motor_omega(self, all_results):
        omega_all = []

        for i, results in enumerate(all_results):
            point = self.trajectory_points[i]

            if not all(res["reachable"] for res in results):
                omega_all.append([np.nan, np.nan, np.nan])
                continue

            try:
                energy = self.compute_motor_energy_balance(
                    force_vector=point["force"],
                    velocity_vector=point["velocity"],
                    results=results
                )

                omega_row = [m["omega_motor"] for m in energy["motors"]]

            except Exception as error:
                print(f"Omega Fehler bei Index {i}: {error}")
                omega_row = [np.nan, np.nan, np.nan]

            omega_all.append(omega_row)

        return np.array(omega_all, dtype=float)

    def compute_all_motor_alpha(self, omega_all):
        t = np.array([point["time"] for point in self.trajectory_points], dtype=float)
        omega_all = np.array(omega_all, dtype=float)

        alpha_all = np.full_like(omega_all, np.nan, dtype=float)

        for motor_index in range(3):
            omega_motor = omega_all[:, motor_index]
            valid = np.isfinite(omega_motor) & np.isfinite(t)

            if np.count_nonzero(valid) >= 2:
                alpha_all[valid, motor_index] = gradient(omega_motor[valid],t[valid])

        return alpha_all

    def compute_motor_omega_numerical_debug(self, all_results):
        t = np.array([point["time"] for point in self.trajectory_points], dtype=float)

        phi_all = np.full((len(all_results), 3), np.nan, dtype=float)

        for i, results in enumerate(all_results):
            for motor_index in range(3):
                if results[motor_index]["reachable"]:
                    phi_all[i, motor_index] = results[motor_index]["angle_rad"]

        omega_numerical = np.full_like(phi_all, np.nan, dtype=float)

        for motor_index in range(3):
            phi_motor = phi_all[:, motor_index]
            valid = np.isfinite(phi_motor) & np.isfinite(t)

            if np.count_nonzero(valid) >= 2:
                omega_numerical[valid, motor_index] = 20*gradient(phi_motor[valid],t[valid])

        omega_analytical = self.compute_all_motor_omega(all_results)

        fig, axs = plt.subplots(3, 1, figsize=(10, 9), sharex=True)

        for motor_index in range(3):
            axs[motor_index].plot(
                t,
                omega_analytical[:, motor_index],
                label=f"omega_{motor_index + 1}_analytisch"
            )

            axs[motor_index].plot(
                t,
                omega_numerical[:, motor_index],
                linestyle="--",
                label=f"omega_{motor_index + 1}_numerisch"
            )

            axs[motor_index].set_ylabel("omega [rad/s]")
            axs[motor_index].grid(True)
            axs[motor_index].legend()

        axs[2].set_xlabel("t [s]")

        plt.suptitle("Vergleich analytische und numerische Winkelgeschwindigkeit")
        plt.tight_layout()
        plt.show()

        return omega_numerical
    
    def compute_all_motor_torque(self, all_results, alpha_all):
        torque_all = np.full_like(alpha_all, np.nan, dtype=float)

        for motor_index in range(3):
            motor = self.motors[motor_index]

            L = motor["upper_length"]
            ms = motor["upper_mass"]
            m2 = motor["lower_mass"] / 2.0
            rs = L / 2.0
            i = motor["i"]
            eta = motor["eta"]
            Jm = motor["Jm"]
            Jg = motor["Jg"]

            J_ges = (1.0 / 3.0) * ms * L**2 + m2 * L**2

            for point_index, results in enumerate(all_results):
                res = results[motor_index]

                if not res["reachable"]:
                    continue

                phi = res["angle_rad"]
                alpha_motor = alpha_all[point_index, motor_index]

                if not np.isfinite(phi) or not np.isfinite(alpha_motor):
                    continue

                alpha_sw = alpha_motor / i

                M_grav = (ms * self.g * rs + m2 * self.g * L) * np.cos(phi)
                M_last = (J_ges * alpha_sw + M_grav) / (i * eta)
                M_traeg = (Jm + Jg) * alpha_motor * i

                torque_all[point_index, motor_index] = M_last + M_traeg

        return torque_all