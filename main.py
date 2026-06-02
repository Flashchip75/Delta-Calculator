import os

from config import cfg
import Motor_Berechnung.exe_motor as exeM
import path_berechnung.exe_path as exeP

def main():
    print("=== Starte Pfadberechnung ===")
    mode = "geometry"

    p1 = [0.4, 0.4, -1]
    p2 = [-0.4, -0.4, -0.5]
    source = "media/test2.png"
    geometry = "profile_1"
    gcode = "test.gcode"

    # --- Switch ---
    kwargs = {
        "geometry": dict(geometry=geometry),
        "points":   dict(p1=p1, p2=p2),
        "cvision":  dict(source=source),
        "gcode":    dict(gcode=gcode),
    }

    g = cfg.global_cfg
    if os.makedirs(g.output_dir, exist_ok=True):
        print(f"Output-Verzeichnis '{g.output_dir}' erstellt.")

    data = exeP.exePath().run(**kwargs[mode])

    print("\n=== Starte Motorberechnung ===")
    exeM.exeMotor().run(data=data)

if __name__ == "__main__":
    main()