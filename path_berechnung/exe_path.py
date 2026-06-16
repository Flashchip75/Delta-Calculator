from __future__ import annotations
import numpy as np
import math

from config import cfg
from pathlib import Path
from .track import Trajectory
from .PathFrenet import PathFrenet
from .ProfileManager import ProfileManager
from .DynamicsManager import DynamicsManager
from .Visualization import Plotter
from .jsonConverter import UIProfileConverter


class exePath:
    def run(
        self,
        geometry: str | None = None,
        gcode: str | None = None,
        uiData: tuple | None = None
    ) -> dict[str, np.ndarray]:
        """
        Priority:
          1. geometry given directly            -> load from JSON via ProfileManager
          4. gcode given                        -> parse GCode file for path
          5. none                               -> raise ValueError
        """

        path = cfg.path
        g = cfg.global_cfg

        # 1. Geometrie
        print("=== Definiere Pfad-Geometrie ===")

        if geometry is not None:
            print("=== Geometrie (direkt übergeben) ===")
            filepath = path.path_profiles
            if filepath is None:
                raise ValueError("Kein Pfad für path_profiles in config.json angegeben.")
            print(f"  Lade Profil '{geometry}' aus '{filepath}'")
            manager = ProfileManager(filepath=filepath)
            j_data = manager.get_profile(geometry)
        elif gcode is not None:
            ext = Path(gcode).suffix.lower()
            if ext in ['.gcode', '.gc', '.g']:
                print(f"=== Geometrie (GCode: {gcode}) ===")
                from .gcode_reader import read_gcode
                j_data = read_gcode(gcode)
                print(f"  GCode '{gcode}' mit {len(j_data)} Segmenten geladen.")
            else:
                raise ValueError(f"Unbekannte Dateiendung '{ext}' für GCode-Datei.")
        elif uiData is not None:
            print("=== Konvertiere UI-Daten -> j_data ===")

            converter = UIProfileConverter(default_N=100)

            j_data = converter.convert_flat(geometries=uiData[0], timeLaws=uiData[1])
        else:
            raise ValueError("Entweder geometry oder gcode muss angegeben werden.")

        # 2. Trajektorie & Dynamik (New Logic)
        print("=== Berechne Trajektorie & Dynamik ===")

        self.validate_path_continuity(j_data)

        traj = Trajectory(j_data)
        pfade = []
        dynamik_vorgaben = []

        for seg in traj.segments:
            # Extrahiert die generierte Punktewolke des Segments
            pfade.append(seg["cloud"].tolist())
            # Extrahiert Dynamik-Vorgaben oder Fallback
            dyn = seg["cfg"].get("dynamik", {"type": "konstant"})
            dynamik_vorgaben.append(dyn)

        # 3. Berechnung über DynamicsManager
        print("=== Prozessiere Pfad-Dynamik ===")
        manager = DynamicsManager(mass=g.mass_kg, g=g.gravity)
        dynamik, F_vec = manager.prozessiere_pfad(pfade, dynamik_vorgaben)

        t = np.array([p['t'] for p in dynamik])
        s = np.array([p['s'] for p in dynamik])
        x = np.array([p['x'] for p in dynamik])
        y = np.array([p['y'] for p in dynamik])
        z = np.array([p['z'] for p in dynamik])
        pts = np.column_stack((x, y, z))
        
        v = np.array([p['v'] for p in dynamik])
        a = np.array([p['a'] for p in dynamik])
        j = np.array([p['j'] for p in dynamik])

        # Frenet-Koordinatensystem berechnen
        pts = np.column_stack((x, y, z))
        frenet = PathFrenet(pts)
        B = np.cross(frenet.T, frenet.N)

        # Vektorielle Kinematik-Komponenten aufbauen
        v_vec = v[:, None] * frenet.T
        a_vec = a[:, None] * frenet.T + (v ** 2)[:, None] * frenet.kappa[:, None] * frenet.N
        j_vec = j[:, None] * frenet.T

        # Kraftkomponenten aufteilen (Nutzt die Masse g.mass_kg aus deiner globalen Konfiguration)
        F_t_vec = g.mass_kg * a[:, None] * frenet.T
        F_n_vec = g.mass_kg * (v ** 2)[:, None] * frenet.kappa[:, None] * frenet.N

        # Zusammenfügen in dein Dictionary
        data = {
            't':     t,
            's':     s,
            'x':     x,             'y':     y,             'z':     z,
            'vx':    v_vec[:, 0],   'vy':    v_vec[:, 1],   'vz':    v_vec[:, 2],
            'ax':    a_vec[:, 0],   'ay':    a_vec[:, 1],   'az':    a_vec[:, 2],
            'jx':    j_vec[:, 0],   'jy':    j_vec[:, 1],   'jz':    j_vec[:, 2],
            'tx':    frenet.T[:, 0],'ty':    frenet.T[:, 1],'tz':    frenet.T[:, 2],
            'nx':    frenet.N[:, 0],'ny':    frenet.N[:, 1],'nz':    frenet.N[:, 2],
            'bx':    B[:, 0],       'by':    B[:, 1],       'bz':    B[:, 2],
            'kappa': frenet.kappa,
            'ftx':   F_t_vec[:, 0], 'fty':   F_t_vec[:, 1], 'ftz':   F_t_vec[:, 2],
            'fnx':   F_n_vec[:, 0], 'fny':   F_n_vec[:, 1], 'fnz':   F_n_vec[:, 2],
            'fx':    F_vec[:, 0],   'fy':    F_vec[:, 1],   'fz':    F_vec[:, 2],
        }

        # Visualisierungen anzeigen
        print("=== Oeffne Diagramme und 3D-Animation ===")
        F_mag = np.linalg.norm(F_vec, axis=1)
        
        # Plotter aufrufen und die Animation an self.ani binden
        #self.ani = Plotter.show(
        #    t, s, v, a, j, pts,
        #    frenet.T, frenet.N, frenet.kappa,
        #    F_mag, F_vec
        #)

        # 5. Export (Inline ausführen)
        print("=== Exportiere Daten ===")
        csvPath = Path(__file__).parent.parent / g.output_dir / g.trajectory_csv
        csvPath.parent.mkdir(parents=True, exist_ok=True)
        
        keys = list(data.keys())
        arr = np.column_stack([data[k] for k in keys])
        header = ",".join(keys)
        
        np.savetxt(
            csvPath,
            arr,
            delimiter=",",
            header=header,
            comments="",
            fmt="%.6f"
        )
        
        return data

    @staticmethod
    def validate_path_continuity(j_data):
        """
        Checks if all consecutive segments in j_data are physically connected.
        Raises a ValueError if a gap is detected.
        """
        def get_start_end(seg, idx):
            seg_type = seg.get("type")
            
            # Handling types that explicitly define points
            if seg_type in ["Line", "Bezier"]:
                if "pts" not in seg or len(seg["pts"]) < 2:
                    raise ValueError(f"Segment {idx} ({seg_type}) is missing 'pts' or has insufficient points.")
                return seg["pts"][0], seg["pts"][-1]
            
            # Handling Arc type (requires calculating start and end from angles)
            elif seg_type == "Arc":
                try:
                    c, r = seg["c"], seg["r"]
                    u, v = seg["u"], seg["v"]
                    angles = seg["a"]  # [start_angle, end_angle]
                    
                    # Helper to calculate a 3D point on the arc given an angle
                    def calc_point(angle):
                        cos_a = math.cos(angle)
                        sin_a = math.sin(angle)
                        return [c[i] + r * (cos_a * u[i] + sin_a * v[i]) for i in range(3)]
                    
                    return calc_point(angles[0]), calc_point(angles[1])
                except KeyError as e:
                    raise ValueError(f"Segment {idx} (Arc) is missing required parameter: {e}")
            
            else:
                raise ValueError(f"Unknown segment type '{seg_type}' at index {idx}.")

        if not j_data or len(j_data) < 2:
            return  # Nothing to compare

        for i in range(len(j_data) - 1):
            curr_seg = j_data[i]
            next_seg = j_data[i + 1]
            
            _, curr_end = get_start_end(curr_seg, i)
            next_start, _ = get_start_end(next_seg, i + 1)
            
            # Compare coordinates using a small tolerance (1mm or 0.001 units depending on your scale)
            is_connected = all(math.isclose(c, n, abs_tol=1e-3) for c, n in zip(curr_end, next_start))
            
            if not is_connected:
                # Formatting points nicely for the error message
                curr_end_str = [round(x, 3) for x in curr_end]
                next_start_str = [round(x, 3) for x in next_start]
                
                raise ValueError(
                    f"Path discontinuity detected between segment {i} ({curr_seg['type']}) "
                    f"and segment {i+1} ({next_seg['type']}).\n"
                    f"  Segment {i} ends at:   {curr_end_str}\n"
                    f"  Segment {i+1} starts at: {next_start_str}"
                )