import csv
from pathlib import Path


class PlotDataLoader:
    @staticmethod
    def load_csv(csv_path):
        data = {}

        with open(Path(csv_path), newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for column in reader.fieldnames:
                data[column] = []

            for row in reader:
                for column, value in row.items():
                    try:
                        data[column].append(float(value))
                    except ValueError:
                        data[column].append(value)

        return data

    @staticmethod
    def get_path_data(data):
        if all(col in data for col in ["x_ef", "y_ef", "z_ef"]):
            return data["x_ef"], data["y_ef"], data["z_ef"]

        if all(col in data for col in ["x", "y", "z"]):
            return data["x"], data["y"], data["z"]

        raise KeyError("Keine passenden Pfad-Spalten gefunden.")

    @staticmethod
    def get_motor_angle_data(data):
        return data["t"], data["phi_1"], data["phi_2"], data["phi_3"]