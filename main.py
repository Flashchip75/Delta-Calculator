import Motor_Berechnung.exe_motor as exeM
import path_berechnung.exe_path as exeP

def main():
    print("=== Starte Pfadberechnung ===")
    exeP.exePath().run()

    print("\n=== Starte Motorberechnung ===")
    exeM.exeMotor().run()

if __name__ == "__main__":
    main()