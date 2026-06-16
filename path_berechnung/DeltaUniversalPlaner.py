import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from path_berechnung.GeometryEngine import GeometryEngine
from path_berechnung.TrajectoryMath import TrajectoryMath

class DeltaUniversalPlaner:
    def __init__(self):
        self.segmente = []
        self.t_gesamt = 0.0
        self.letzter_zustand = {"s": 0.0, "v": 0.0, "a": 0.0, "j": 0.0}
        self.math = TrajectoryMath()
        self.geo = GeometryEngine()

    def plane_gesamten_ablauf(self, pfad_liste, dynamik_liste):
        for punkte, dyn in zip(pfad_liste, dynamik_liste):
            # Pfadlänge des Segments über die Punktewolke bestimmen
            pts = np.array(punkte)
            s_segment = np.sum(np.sqrt(np.sum(np.diff(pts, axis=0) ** 2, axis=1)))

            s0, v0, a0, j0 = self.letzter_zustand.values()
            current_dauer = dyn.get('dauer')

            if dyn.get('type') == 'konstant':
                current_dauer = s_segment / v0 if abs(v0) > 1e-6 else 1.0
                bed = [(0, 0, s0), (0, current_dauer, s0 + s_segment)]
            elif dyn.get('type') == 'warten':
                # SONDERFALL: Warten (Roboter steht still, v=0, a=0)
                current_dauer = dyn['dauer']
                bed = [
                    (0, 0, s0), (1, 0, 0.0), (2, 0, 0.0),  # Start im Stillstand
                    (0, current_dauer, s0),  # Ziel bleibt exakt auf s0
                    (1, current_dauer, 0.0), (2, current_dauer, 0.0)  # Ziel im Stillstand
                ]
            else:
                bed = [(0, 0, s0), (1, 0, v0), (2, 0, a0)]
                if 'ziel_j' in dyn or 'start_j' in dyn: bed.append((3, 0, j0))
                bed.append((0, current_dauer, s0 + s_segment))
                bed.append((1, current_dauer, dyn['ziel_v']))
                if 'ziel_a' in dyn: bed.append((2, current_dauer, dyn['ziel_a']))
                if 'ziel_j' in dyn: bed.append((3, current_dauer, dyn['ziel_j']))

            koeff = self.math.solve_coefficients(bed)
            self.segmente.append({'t_start': self.t_gesamt, 't_ende': self.t_gesamt + current_dauer, 'koeff': koeff})
            self.t_gesamt += current_dauer

            self.letzter_zustand = {
                "s": self.math.get_poly_val(koeff, current_dauer, 0),
                "v": self.math.get_poly_val(koeff, current_dauer, 1),
                "a": self.math.get_poly_val(koeff, current_dauer, 2),
                "j": self.math.get_poly_val(koeff, current_dauer, 3) if len(koeff) > 4 else 0.0
            }

    def get_zustand(self, t, k=0):
        for seg in self.segmente:
            if seg['t_start'] <= t <= seg['t_ende'] + 1e-9:
                return self.math.get_poly_val(seg['koeff'], t - seg['t_start'], k)
        return self.get_zustand(self.t_gesamt, k) if t > self.t_gesamt else 0.0

    def finde_zeit_zu_s(self, s_ziel):
        if s_ziel <= 1e-9: return 0.0
        if s_ziel >= self.letzter_zustand["s"] - 1e-9: return self.t_gesamt
        return brentq(lambda t: self.get_zustand(t, 0) - s_ziel, 0, self.t_gesamt)

    def berechne_punkt_dynamik(self, punktewolke_gesamt):
        """
        Invertiert s -> t exakt für jeden übergebenen Punkt und
        berechnet v, a und j (Ruck) für diesen Zustand.
        """
        s_kumuliert = self.geo.berechne_kumulierte_pfadlaengen(punktewolke_gesamt)

        ergebnisse = []
        for i, punkt in enumerate(punktewolke_gesamt):
            s_aktuell = s_kumuliert[i]

            # Inversion: Zeitstempel für genau diesen Punkt finden
            t = self.finde_zeit_zu_s(s_aktuell)

            # Dynamik (inkl. Ruck k=3) exakt für diesen Zeitpunkt abgreifen
            v = self.get_zustand(t, 1)
            a = self.get_zustand(t, 2)
            j = self.get_zustand(t, 3)

            ergebnisse.append({
                'x': punkt[0], 'y': punkt[1], 'z': punkt[2],
                't': t, 's': s_aktuell, 'v': v, 'a': a, 'j': j
            })
        return ergebnisse