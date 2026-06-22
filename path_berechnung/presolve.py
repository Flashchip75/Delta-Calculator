import numpy as np
import copy
import csv

class PreCurve:
    def __init__(self, cfg):
        self.c = cfg

    def __call__(self, t):
        c, typ, p = self.c, self.c['type'], np.array(self.c.get('pts', []))
        if typ == 'Line': return p[0] * (1 - t) + p[1] * t
        if typ == 'Bezier': return (1 - t)**3 * p[0] + 3 * t * (1 - t)**2 * p[1] + 3 * t**2 * (1 - t) * p[2] + t**3 * p[3]
        if typ in ['Arc', 'Circle']:
            a = c.get('a', [0, 2 * np.pi])
            ang = a[0] + t * (a[1] - a[0])
            return np.array(c['c']) + c['r'] * (np.cos(ang) * np.array(c['u']) + np.sin(ang) * np.array(c['v']))


class Presolver:
    @staticmethod
    def enrich_config(json_data, default_ppm=100):
        enriched = copy.deepcopy(json_data)
        for cfg in enriched:
            pts = np.array([PreCurve(cfg)(t) for t in np.linspace(0, 1, 100)])
            length = np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1))
            cfg["approx_length"] = length
            cfg["N"] = cfg.get("N", max(2, int(length * default_ppm)))
        return enriched

    @staticmethod
    def export_summary_csv(enriched_data, filename="presolve_summary.csv"):
        """Exportiert eine saubere Übersicht der Segmente als CSV."""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';') # Semikolon für deutsches Excel
            writer.writerow(["Segment_ID", "Typ", "Laenge_m", "Punkte_N", "Zeit_T"])
            for i, seg in enumerate(enriched_data):
                writer.writerow([i, seg["type"], round(seg["approx_length"], 4), seg["N"], seg.get("T", "N/A")])