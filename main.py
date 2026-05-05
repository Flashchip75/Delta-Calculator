import Motor_Berechnung.exe_motor as exeM
import path_berechnung.exe_path as exeP

def main():
    print("=== Starte Pfadberechnung ===")
    mode = "geometry"

    p1 = [0.4, 0.4, 0]
    p2 = [-0.4, -0.4, 0]

    jData = [
        {"type": "Line", "pts": [[0.0, 0.0, 0.0], [0.2, 0.0, 0.0]]},
        {"type": "Arc", "c": [0.2, 0.2, 0.0], "r": 0.2, "u": [1, 0, 0],
        "v": [0, 1, 0], "a": [-1.5708, 0.0]},
        {"type": "Bezier",
        "pts": [[0.4, 0.2, 0.0], [0.4, 0.4, 0.0], [0.2, 0.4, 0.0], [0.2, 0.4, 0.2]]},
        {"type": "Line", "pts": [[0.2, 0.4, 0.2], [0.2, 0.4, 0.4]]}
    ]

    source = "media/test2.png"

    # --- Switch ---
    kwargs = {
        "geometry": dict(geometry=jData),
        "points":   dict(p1=p1, p2=p2),
        "cvision":   dict(source=source),
    }

    d = exeP.exePath().run(**kwargs[mode])

    print("\n=== Starte Motorberechnung ===")
    exeM.exeMotor().run(d)

if __name__ == "__main__":
    main()