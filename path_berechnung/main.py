import numpy as np
import json
from track import Trajectory
from PathFrenet import PathFrenet
from PathKinematics import PathKinematics
from Visualization import Plotter


def main():
    # 1. Geometrie-Definition (N=2000 zur Vermeidung von numerischem Zittern)
    j_data = [
        {
            "type": "Bezier",
            "pts": [
                [0.0, 0.0, 0.0],
                [0.0, 0.4, 0.0],
                [0.4, 0.0, 0.0],
                [0.4, 0.4, 0.0]
            ],
            "T": 2.0,
            "v0": 0.0,
            "v1": 0.0,
            "N": 1000

        }
    ]

    # 2. Initialisierung der Trajektorie
    traj = Trajectory(j_data)

    # Listen für die Gesamtdarstellung (Akkumulation über alle Segmente)
    t_all, s_all, v_all, a_all, pts_all = [], [], [], [], []
    T_all, N_all, kappa_all, F_mag_all, F_vec_all = [], [], [], [], []
    t_offset, s_offset = 0.0, 0.0

    json_export = []
    header_str = "t,x,y,z,vx,vy,vz,ax,ay,az,jx,jy,jz,tx,ty,tz,nx,ny,nz,bx,by,bz,kappa,ftx,fty,ftz,fnx,fny,fnz,fx,fy,fz"
    keys = header_str.split(",")

    # 3. Berechnung pro Segment
    for i, segment in enumerate(traj.segments):
        pts = segment["cloud"]
        cfg = segment["cfg"]

        # Zeit und Randbedingungen aus dem JSON laden[cite: 3]
        T_seg = cfg.get("T", 5.0)
        v0_seg = cfg.get("v0", 0.0)
        v1_seg = cfg.get("v1", 0.0)

        frenet = PathFrenet(pts)
        kin = PathKinematics(pts, T=T_seg, v0=v0_seg, v1=v1_seg)

        # 4. Erweiterte Physik (Integrierte Kraftberechnung)
        mass = 1.0  # kg[cite: 1]
        g = 9.81  # m/s²

        B = np.cross(frenet.T, frenet.N)
        v_vec = kin.v[:, None] * frenet.T

        # Dynamische Kräfte[cite: 1]
        F_t_vec = kin.a[:, None] * frenet.T  # Tangentialkraft
        F_n_vec = (kin.v ** 2)[:, None] * frenet.kappa[:, None] * frenet.N  # Normalkraft

        # Gewichtskraft (wirkt statisch in positive Z-Richtung, um Gravitation auszugleichen)[cite: 1]
        F_g_vec = np.tile(np.array([0, 0, mass * g]), (len(kin.t), 1))

        # Gesamtkraft (Strukturkraft)[cite: 1]
        F_vec = F_t_vec + F_n_vec + F_g_vec
        F_mag = np.linalg.norm(F_vec, axis=1)  # Betrag der Gesamtkraft für die Anzeige[cite: 5]

        # Beschleunigung und Ruck[cite: 1]
        a_vec = F_vec / mass
        j_vec = np.gradient(a_vec, kin.t, axis=0)

        # 5. Daten zusammenstellen
        csv_data = np.column_stack((
            kin.t + t_offset, pts, v_vec, a_vec, j_vec,
            frenet.T, frenet.N, B, frenet.kappa,
            F_t_vec, F_n_vec, F_vec
        ))

        # Akkumulieren für Visualisierung[cite: 5]
        t_all.append(kin.t + t_offset)
        s_all.append(kin.s + s_offset)
        v_all.append(kin.v)
        a_all.append(kin.a)
        pts_all.append(pts)
        T_all.append(frenet.T)
        N_all.append(frenet.N)
        kappa_all.append(frenet.kappa)
        F_mag_all.append(F_mag)  # Korrekte Übergabe an die Liste
        F_vec_all.append(F_vec)

        t_offset += kin.t[-1]
        s_offset += kin.s[-1]

        # JSON-Struktur für Export[cite: 1]
        segment_json = [dict(zip(keys, np.round(row, 6))) for row in csv_data]
        json_export.append({
            "segment_id": i,
            "type": cfg["type"],
            "data": segment_json
        })

    # 6. Export
    with open("roboter_dynamik.json", "w") as f:
        json.dump(json_export, f, indent=4)

    print(f"-> Daten exportiert ({len(traj.segments)} Segmente).")

    # 7. Visualisierung (Zusammenführung aller akkumulierten Daten)[cite: 5]
    Plotter.show(
        np.concatenate(t_all), np.concatenate(s_all), np.concatenate(v_all),
        np.concatenate(a_all), np.concatenate(pts_all), np.concatenate(T_all),
        np.concatenate(N_all), np.concatenate(kappa_all),
        np.concatenate(F_mag_all), np.concatenate(F_vec_all)
    )


if __name__ == "__main__":
    main()