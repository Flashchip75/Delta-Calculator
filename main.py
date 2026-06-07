from Oberflaeche.gui.app import App

def main():
    print("=== Starte Pfadberechnung ===")
    mode = "geometry"

    jData = "full_circle"
    p1 = [0.4, 0.4, -1]
    p2 = [-0.4, -0.4, -0.5]
    source = "media/test2.png"

    # --- Switch ---
    kwargs = {
        "geometry": dict(geometry=jData),
        "points":   dict(p1=p1, p2=p2),
        "cvision":   dict(source=source),
    }

    data = exeP.exePath().run(**kwargs[mode])

    print("\n=== Starte Motorberechnung ===")
    exeM.exeMotor().run(data=data)

if __name__ == "__main__":
    main()

    # hiermit gui starten
    # app = App()
    # app.mainloop()