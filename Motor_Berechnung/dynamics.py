import numpy as np

class DynamicsSolver:
    def __init__(self, robot_config, trajectory):
        self.upper_arm_length = robot_config.upper_arm_length
        self.trajectory_points = trajectory.points

        # Übersetzung der Motoren, z. B. {"A": 10, "B": 10, "C": 10}
        self.motor_transmission = {
            motor["name"]: motor["i"]
            for motor in robot_config.motors
        }

        # Drehachsen der Motoren, z. B. {"A": axis_A, "B": axis_B, "C": axis_C}
        self.motor_axis = {
            motor["name"]: motor["axis"]
            for motor in robot_config.motors
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
        q = np.array(vector_quantity, dtype=float)
        U = self.get_lower_rod_directions(results)

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

    def solve_rod_velocities(self, velocity_vector, results):
        return self.solve_rod_scalars(velocity_vector, results)
    
    def project_rod_force_tangential_to_upper_arm(self, rod_force_scalar, result):
        lower_rod_direction = np.array(result["lower_rod_direction"], dtype=float)
        upper_arm_direction = np.array(result["upper_arm_direction"], dtype=float)
        motor_axis = np.array(result["motor_axis"], dtype=float)

        lower_rod_direction = lower_rod_direction / np.linalg.norm(lower_rod_direction)
        upper_arm_direction = upper_arm_direction / np.linalg.norm(upper_arm_direction)
        motor_axis = motor_axis / np.linalg.norm(motor_axis)

        # Kraft am Ellenbogengelenk auf den Upper Arm
        rod_force_vector = -rod_force_scalar * lower_rod_direction

        # Tangentialrichtung der Kreisbewegung
        tangential_direction = np.cross(motor_axis, upper_arm_direction)

        norm_tangent = np.linalg.norm(tangential_direction)
        if norm_tangent < 1e-12:
            raise ValueError(
                f"Tangentialrichtung für Motor {result['name']} ungültig."
            )

        tangential_direction = tangential_direction / norm_tangent

        tangential_force = np.dot(rod_force_vector, tangential_direction)

        return tangential_force
    
    def compute_motor_torque_from_rod_force(self, rod_force_scalar, result):
        lower_rod_direction = np.array(result["lower_rod_direction"], dtype=float)
        upper_arm_direction = np.array(result["upper_arm_direction"], dtype=float)
        motor_axis = np.array(result["motor_axis"], dtype=float)

        lower_rod_direction = lower_rod_direction / np.linalg.norm(lower_rod_direction)
        upper_arm_direction = upper_arm_direction / np.linalg.norm(upper_arm_direction)
        motor_axis = motor_axis / np.linalg.norm(motor_axis)

        # Kraft am Ellenbogen auf den Upper Arm
        force_on_upper_arm = -rod_force_scalar * lower_rod_direction

        # Tangentialrichtung der Upper-Arm-Kreisbewegung
        tangential_direction = np.cross(motor_axis, upper_arm_direction)

        tangent_norm = np.linalg.norm(tangential_direction)

        if tangent_norm < 1e-12:
            raise ValueError(
                f"Tangentialrichtung ungültig bei Motor {result['name']}"
            )

        tangential_direction = tangential_direction / tangent_norm

        tangential_force = np.dot(force_on_upper_arm, tangential_direction)

        torque_motor = tangential_force * self.upper_arm_length

        return torque_motor
    
    def compute_motor_energy_balance(self, force_vector, velocity_vector, results):
        force_projections = self.project_vector_onto_rods(force_vector, results)
        velocity_projections = self.project_vector_onto_rods(velocity_vector, results)

        rod_forces, U, reconstructed_force = self.solve_rod_forces(
            force_vector,
            results
        )

        rod_velocities, _, reconstructed_velocity = self.solve_rod_velocities(
            velocity_vector,
            results
        )

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
            "reconstructed_velocity": reconstructed_velocity,
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
                alpha_valid = np.gradient(omega_motor[valid], t[valid])
                alpha_all[valid, motor_index] = alpha_valid

        return alpha_all
