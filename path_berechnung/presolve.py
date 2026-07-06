import numpy as np
import copy
import csv
from path_berechnung.ui_to_presolve import UIToPresolveConverter


class PreCurve:
    def __init__(self, cfg):
        self.c = cfg

    def __call__(self, t):
        if not isinstance(self.c, dict):
            raise TypeError(f"PreCurve expected dict, got {type(self.c)}: {self.c}")

        c = self.c
        typ = c.get('type')

        if typ is None:
            raise ValueError(f"Missing 'type' in segment: {c}")

        p = np.array(c.get('pts', []))

        if typ == 'Line':
            return p[0] * (1 - t) + p[1] * t

        if typ == 'Bezier':
            return (
                (1 - t)**3 * p[0]
                + 3 * t * (1 - t)**2 * p[1]
                + 3 * t**2 * (1 - t) * p[2]
                + t**3 * p[3]
            )

        if typ in ['Arc', 'Circle']:
            a = c.get('a', [0, 2 * np.pi])
            ang = a[0] + t * (a[1] - a[0])
            return np.array(c['c']) + c['r'] * (
                np.cos(ang) * np.array(c['u']) +
                np.sin(ang) * np.array(c['v'])
            )

        raise ValueError(f"Unknown curve type: {typ}")


class Presolver:

    @staticmethod
    def enrich_config(json_data, default_ppm=100):

        # --- Fall 1: neues Format (Liste von Dicts)
        if isinstance(json_data, list):
            cfg_list = json_data

        # --- Fall 2: altes UI-Format
        elif isinstance(json_data, dict) and "uidata" in json_data:
            geometries, time_laws = json_data["uidata"]

            from path_berechnung.ui_to_presolve import UIToPresolveConverter
            converter = UIToPresolveConverter(default_N=default_ppm)

            cfg_list = converter.convert_ui_data((geometries, time_laws))

        else:
            raise TypeError(f"Unsupported input format: {type(json_data)}")

        for i, cfg in enumerate(cfg_list):
            if not isinstance(cfg, dict):
                raise TypeError(f"Segment {i} is not dict: {cfg}")

        enriched = copy.deepcopy(cfg_list)

        for cfg in enriched:
            pts_preview = np.array([
                PreCurve(cfg)(t)
                for t in np.linspace(0, 1, 100)
            ])

            length = np.sum(
                np.linalg.norm(np.diff(pts_preview, axis=0), axis=1)
            )

            cfg["approx_length"] = length
            cfg["N"] = cfg.get("N", max(2, int(length * default_ppm)))

            pts = np.array([
                PreCurve(cfg)(t)
                for t in np.linspace(0, 1, cfg["N"])
            ])

            cfg["point_cloud"] = pts.tolist()

        return enriched

    @staticmethod
    def enrich_ui_path(ui_data, default_ppm=100):
        converter = UIToPresolveConverter(default_N=default_ppm)
        presolver_input = converter.convert_ui_data(ui_data)
        return Presolver.enrich_config(presolver_input, default_ppm)

    @staticmethod
    def export_summary_csv(enriched_data, filename="presolve_summary.csv"):
        """Exportiert eine saubere Übersicht der Segmente als CSV."""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';') # Semikolon für deutsches Excel
            writer.writerow(["Segment_ID", "Typ", "Laenge_m", "Punkte_N", "Zeit_T"])
            for i, seg in enumerate(enriched_data):
                writer.writerow([i, seg["type"], round(seg["approx_length"], 4), seg["N"], seg.get("T", "N/A")])

    @staticmethod
    def get_total_point_cloud(enriched_data):
        point_cloud = []

        for seg in enriched_data:
            pts = seg.get("point_cloud", [])

            if not pts:
                continue

            # Doppelten Uebergangspunkt vermeiden
            if point_cloud and pts[0] == point_cloud[-1]:
                point_cloud.extend(pts[1:])
            else:
                point_cloud.extend(pts)

        return point_cloud
