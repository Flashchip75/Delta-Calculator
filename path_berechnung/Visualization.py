import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


class Plotter:
    @staticmethod
    def show(t, s, v, a, j, pts, T, N, kappa, F_mag, F_vec):
        # 0. Vorherige Plots schließen, um Memory Leaks zu vermeiden
        plt.close('all')

        # =====================================================================
        # 1. Visualisierung: 2D-Zustandsgraphen (v, a, j) über der Bogenlänge s
        # =====================================================================
        fig1, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

        # Geschwindigkeit (grün)
        ax1.plot(s, v, 'go', markersize=3, label='v(s)')
        ax1.set_ylabel('Geschwindigkeit [mm/s]')
        ax1.set_title('Diskrete Dynamikwerte (v, a, j) über der Bogenlänge s')
        ax1.grid(True)
        ax1.legend()

        # Beschleunigung (rot)
        ax2.plot(s, a, 'ro', markersize=3, label='a(s)')
        ax2.set_ylabel('Beschleunigung [mm/s²]')
        ax2.grid(True)
        ax2.legend()

        # Ruck (blau)
        ax3.plot(s, j, 'bo', markersize=3, label='j(s) (Ruck)')
        ax3.set_ylabel('Ruck [mm/s³]')
        ax3.set_xlabel('Bogenlänge s [mm]')
        ax3.grid(True)
        ax3.legend()

        fig1.tight_layout()

        # =====================================================================
        # 2. Visualisierung: 3D-Trajektorien-Animation
        # =====================================================================
        fig2 = plt.figure(figsize=(10, 8))
        ax3d = fig2.add_subplot(111, projection='3d')

        # Dynamische Achsengrenzen basierend auf der Punktewolke ermitteln
        # (Verhindert, dass die Kurve aus dem Bild wandert, wenn sie größer als 0.5 wird)
        min_b = np.min(pts, axis=0) - 10
        max_b = np.max(pts, axis=0) + 10

        def update(i):
            ax3d.cla()
            # Pfad zeichnen
            ax3d.plot(*pts.T, color='gray', alpha=0.3)
            p, k = pts[i], kappa[i]

            # Vektoren zeichnen (T=rot, N=blau)
            ax3d.quiver(*p, *T[i], color='r', length=max((max_b[0] - min_b[0]) * 0.05, 0.08))
            ax3d.quiver(*p, *N[i], color='b', length=max((max_b[0] - min_b[0]) * 0.05, 0.08))

            # Krümmungskreis zeichnen
            if k > 0.001:  # Toleranz angepasst für flachere Kurven
                th = np.linspace(0, 2 * np.pi, 50)
                kreis = p + (1 / k) * N[i] + (1 / k) * (np.outer(np.cos(th), T[i]) + np.outer(np.sin(th), N[i]))
                ax3d.plot(*kreis.T, color='g')

            # Achsen setzen und Titel updaten
            ax3d.set_xlim(min_b[0], max_b[0])
            ax3d.set_ylim(min_b[1], max_b[1])
            ax3d.set_zlim(min_b[2], max_b[2] + 0.1)  # Leichtes Z-Offset, falls Kurve flach ist
            ax3d.set_title(f"s={s[i]:.2f}mm | t={t[i]:.2f}s | Gesamtkraft: {F_mag[i]:.2f} N")

        # Animations-Logik
        dt_data = t[1] - t[0] if len(t) > 1 else 0.01
        frame_skip = 1
        calc_interval = dt_data * frame_skip * 1000

        ani = FuncAnimation(
            fig2,
            update,
            frames=range(0, len(t), frame_skip),
            interval=calc_interval,
            repeat=False  # Stoppt nach einem Durchlauf sauber
        )

        # HIER: Ein einziger plt.show() Aufruf öffnet BEIDE Fenster (fig1 und fig2)
        plt.show()

        return ani