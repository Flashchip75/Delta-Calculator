import Motor_Berechnung.exe_motor as exeM
import path_berechnung.exe_path as exeP

def main():
    print("=== Starte Pfadberechnung ===")
    p1 = [0.4, 0.4, 0]
    p2 = [-0.4, -0.4, 0]
    # if p1 or p2 uses image or video input
    #p1 = None
    #p2 = None
    j_data = [{"type": "Line", "pts": [[0.0, 0.0, 0.0], [0.2, 0.0, 0.0]]},
              {"type": "Arc", "c": [0.2, 0.2, 0.0], "r": 0.2, "u": [1, 0, 0],
               "v": [0, 1, 0], "a": [-1.5708, 0.0]}, {"type": "Bezier",
                "pts": [[0.4, 0.2, 0.0], [0.4, 0.4, 0.0], [0.2, 0.4, 0.0], [0.2, 0.4, 0.2]]},
                {"type": "Line", "pts": [[0.2, 0.4, 0.2], [0.2, 0.4, 0.4]]}]

    d = exeP.exePath().run(geometry = j_data, p1=p1, p2=p2)
    #d = exeP.exePath().run(p1, p2, source="media/test2.png")

    print("\n=== Starte Motorberechnung ===")
    exeM.exeMotor().run(d)

if __name__ == "__main__":
    main()