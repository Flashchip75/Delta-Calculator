import csv
import numpy as np
import os 

class DataExporter:
    def __init__(self, trajectory, dynamics_solver):
        self.trajectory = trajectory
        self.dynamics_solver = dynamics_solver
        self.data = []
 

    def export_results_to_csv(self, all_results, filename="results.csv"):
    
        rows = self.build_data(all_results)

        if len(rows) == 0:
            print("Keine Daten für CSV vorhanden.")
            return

        fieldnames = list(rows[0].keys())

    
        output_dir = "output"
        csv_dir = os.path.join(output_dir, "csv")
        os.makedirs(csv_dir, exist_ok=True)
    
        filepath = os.path.join(csv_dir, filename)
    
        with open(filepath, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
        print(f"CSV gespeichert: {filepath}")

    def build_data(self, all_results):
        omega_all = self.dynamics_solver.compute_all_motor_omega(all_results)
        alpha_all = self.dynamics_solver.compute_all_motor_alpha(omega_all)
        torque_all = self.dynamics_solver.compute_all_motor_torque(all_results,alpha_all)

        rows = []

        for i, results in enumerate(all_results):
            point = self.trajectory.points[i]

            row = {
                "t": point["time"],

                "x_ef": point["position"][0],
                "y_ef": point["position"][1],
                "z_ef": point["position"][2],

                "x_elbow_1": results[0]["elbow"][0] if results[0]["reachable"] else np.nan,
                "y_elbow_1": results[0]["elbow"][1] if results[0]["reachable"] else np.nan,
                "z_elbow_1": results[0]["elbow"][2] if results[0]["reachable"] else np.nan,

                "x_elbow_2": results[1]["elbow"][0] if results[1]["reachable"] else np.nan,
                "y_elbow_2": results[1]["elbow"][1] if results[1]["reachable"] else np.nan,
                "z_elbow_2": results[1]["elbow"][2] if results[1]["reachable"] else np.nan,

                "x_elbow_3": results[2]["elbow"][0] if results[2]["reachable"] else np.nan,
                "y_elbow_3": results[2]["elbow"][1] if results[2]["reachable"] else np.nan,
                "z_elbow_3": results[2]["elbow"][2] if results[2]["reachable"] else np.nan,

                "phi_1": results[0]["angle_rad"] if results[0]["reachable"] else np.nan,
                "phi_2": results[1]["angle_rad"] if results[1]["reachable"] else np.nan,
                "phi_3": results[2]["angle_rad"] if results[2]["reachable"] else np.nan,

                "omega_1": omega_all[i][0],
                "omega_2": omega_all[i][1],
                "omega_3": omega_all[i][2],

                "alpha_1": alpha_all[i][0],
                "alpha_2": alpha_all[i][1],
                "alpha_3": alpha_all[i][2],

                "M_motor_1": torque_all[i][0],
                "M_motor_2": torque_all[i][1],
                "M_motor_3": torque_all[i][2],
            }

            rows.append(row)

        self.data = rows
        return rows