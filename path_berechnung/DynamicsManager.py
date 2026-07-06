import numpy as np
import json
from pathlib import Path

from config import load_config
from path_berechnung.PathFrenet import PathFrenet
from path_berechnung.DeltaUniversalPlaner import DeltaUniversalPlaner


class DynamicsManager:
    def __init__(self, mass, g):
        self.mass = mass
        self.g = g[2]
        self.header = "t,s,x,y,z,vx,vy,vz,ax,ay,az,jx,jy,jz,tx,ty,tz,nx,ny,nz,bx,by,bz,kappa,ftx,fty,ftz,fnx,fny,fnz,fx,fy,fz"

    def prozessiere_pfad(self, pfade, dynamik_vorgaben):
        """
        Nimmt die separierten Pfade und Dynamik-Vorgaben, berechnet alles
        und exportiert die Ergebnisse.
        """
        # 1. Gesamte Punktewolke nahtlos zusammenfügen (WICHTIG: Als Kopie!)
        wolke_gesamt = list(pfade[0])  # list() verhindert das Überschreiben von pfade[0]
        for pfad in pfade[1:]:
            wolke_gesamt.extend(pfad[1:])  # Ersten Punkt überspringen, um Duplikate zu vermeiden

        pts = np.array(wolke_gesamt)

        # 2. Kinematik mit dem NEUEN Planer berechnen
        planer = DeltaUniversalPlaner()
        planer.plane_gesamten_ablauf(pfade, dynamik_vorgaben)
        raum_dynamik = planer.berechne_punkt_dynamik(wolke_gesamt)

        # Daten für Vektormathematik in Numpy-Arrays extrahieren
        t_arr = np.array([p['t'] for p in raum_dynamik])
        s_arr = np.array([p['s'] for p in raum_dynamik])
        v_arr = np.array([p['v'] for p in raum_dynamik])
        a_arr = np.array([p['a'] for p in raum_dynamik])
        j_arr = np.array([p['j'] for p in raum_dynamik])

        # 3. Geometrie (Frenet) berechnen
        frenet = PathFrenet(pts)

        # 4. Kräfte berechnen
        v_vec = v_arr[:, None] * frenet.T
        a_vec = a_arr[:, None] * frenet.T + (v_arr ** 2)[:, None] * frenet.kappa[:, None] * frenet.N
        j_vec = j_arr[:, None] * frenet.T

        F_t = self.mass * a_arr[:, None] * frenet.T
        F_n = self.mass * (v_arr ** 2)[:, None] * frenet.kappa[:, None] * frenet.N
        F_g = np.tile(np.array([0, 0, -self.mass * self.g]), (len(t_arr), 1))

        F_vec = F_t + F_n - F_g

        # 5. Daten für den Export zusammenbauen
        B = np.cross(frenet.T, frenet.N)
        csv_matrix = np.column_stack((
            t_arr, s_arr, pts, v_vec, a_vec, j_vec,
            frenet.T, frenet.N, B, frenet.kappa,
            F_t, F_n, F_vec
        ))

        self._export_results(csv_matrix)

        return raum_dynamik, F_vec

    def _export_results(self, matrix):
        cfg = load_config()
        g = cfg.global_cfg
        filepath = Path(g.output_dir) / g.trajectory_csv
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        np.savetxt(str(filepath), matrix, delimiter=",", header=self.header, comments="", fmt="%.6f")

        keys = self.header.split(",")
        matrix_rounded = np.round(matrix, 6)
        json_export = [dict(zip(keys, row.tolist())) for row in matrix_rounded]
        
        json_filepath = filepath.with_suffix('.json')
        
        with open(json_filepath, "w") as f:
            json.dump(json_export, f, indent=4)