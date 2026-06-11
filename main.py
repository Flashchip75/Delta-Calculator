import os

from config import cfg
import Motor_Berechnung.exe_motor as exeM
import path_berechnung.exe_path as exeP

def main():
    print("=== Starte Pfadberechnung ===")
    mode = "gcode"

    geometry = "full_circle"
    gcode = "test.gcode"

    # --- Switch ---
    kwargs = {
        "geometry": dict(geometry=geometry),
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