import csv
import numpy as np
import os 

class DataExporter:
    def __init__(self, trajectory, dynamics_solver):
        self.trajectory = trajectory
        self.dynamics_solver = dynamics_solver

    def export_results_to_csv(self, all_results, filename="results.csv"):
        omega_all = self.dynamics_solver.compute_all_motor_omega(all_results)
        alpha_all = self.dynamics_solver.compute_all_motor_alpha(omega_all)
    
        rows = []
    
        for i, results in enumerate(all_results):
            row = {
                "t": self.trajectory.points[i]["time"],
    
                "phi_1_rad": results[0]["angle_rad"] if results[0]["reachable"] else np.nan,
                "phi_2_rad": results[1]["angle_rad"] if results[1]["reachable"] else np.nan,
                "phi_3_rad": results[2]["angle_rad"] if results[2]["reachable"] else np.nan,
    
                "omega_1_rad_s": omega_all[i][0],
                "omega_2_rad_s": omega_all[i][1],
                "omega_3_rad_s": omega_all[i][2],
    
                "alpha_1_rad_s2": alpha_all[i][0],
                "alpha_2_rad_s2": alpha_all[i][1],
                "alpha_3_rad_s2": alpha_all[i][2],
            }
            rows.append(row)
    
        if len(rows) == 0:
            print("Keine Daten für CSV vorhanden.")
            return
    
        fieldnames = [
            "t",
            "phi_1_rad",
            "phi_2_rad",
            "phi_3_rad",
            "omega_1_rad_s",
            "omega_2_rad_s",
            "omega_3_rad_s",
            "alpha_1_rad_s2",
            "alpha_2_rad_s2",
            "alpha_3_rad_s2",
        ]
    
        output_dir = "output"
        csv_dir = os.path.join(output_dir, "csv")
        os.makedirs(csv_dir, exist_ok=True)
    
        filepath = os.path.join(csv_dir, filename)
    
        with open(filepath, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
        print(f"CSV gespeichert: {filepath}")
