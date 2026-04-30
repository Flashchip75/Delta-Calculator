import Motor_Berechnung.exe_motor as exeM
import path_berechnung.exe_path as exeP

def main():
    print("=== Starte Pfadberechnung ===")
    p1 = [0, 0, 0]
    p2 = [100, 0, 0]
    # if p1 or p2 uses image or video input
    #p1 = None
    #p2 = None
    d = exeP.exePath().run(p1, p2, source="media/test2.png")

    print("\n=== Starte Motorberechnung ===")
    exeM.exeMotor().run(d)

if __name__ == "__main__":
    main()

#test