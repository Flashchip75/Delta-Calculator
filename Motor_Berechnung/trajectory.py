import csv
import numpy as np

class Trajectory:
    def __init__(self, trajectory_csv_path):
        self.trajectory_data = self.load_trajectory_csv(trajectory_csv_path)
        self.path_points = self.create_path_points_from_trajectory(self.trajectory_data)
        self.points = self.trajectory_data["points"]

    def load_csv_rows(self, path):
        with open(path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                raise ValueError("CSV enthält keine Kopfzeile")
            return list(reader)

    def create_vector_object_from_row(self, row, x_name, y_name, z_name):
        return np.array([
            float(row[x_name]),
            float(row[y_name]),
            float(row[z_name])
        ], dtype=float)

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

    def load_trajectory_csv(self, path):
        rows = self.load_csv_rows(path)
        points = []
        for row in rows:
            points.append(self.create_trajectory_point_object(row))
        return {
            "count": len(points),
            "points": points,
        }

    def create_path_points_from_trajectory(self, trajectory):
        return np.array([point["position"] for point in trajectory["points"]], dtype=float)
