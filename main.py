import Motor_Berechnung.exe_motor as exem
import path_berechnung.exe_path as exep

def main():
    print("=== Starte Pfadberechnung ===")
    exep.exePath().run()

    print("\n=== Starte Motorberechnung ===")
    exem.exeMotor().run()

if __name__ == "__main__":
    main()