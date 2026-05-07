import matplotlib.pyplot as plt, numpy as np
from matplotlib.animation import FuncAnimation

class Plotter:
    @staticmethod
    def show(t, s, v, a, pts, T, N, kappa, F_mag, F_vec):
        fig1, (ax1, ax3) = plt.subplots(2, 1, figsize=(10, 8))
        ax1.plot(t, s, label='s(t)'); ax1.plot(t, v, label='v(t)'); ax1.plot(t, a, '--', label='a(t)'); ax1.legend()
        ax3.plot(t, F_mag, 'k', label='|F|'); [ax3.plot(t, F_vec[:,i], label=f'F_{"xyz"[i]}') for i in range(3)]; ax3.legend()
        fig2 = plt.figure(); ax3d = fig2.add_subplot(111, projection='3d')
        def update(i):
            ax3d.cla(); ax3d.plot(*pts.T, color='gray', alpha=0.3); p, k = pts[i], kappa[i]
            ax3d.quiver(*p, *T[i], color='r', length=0.08); ax3d.quiver(*p, *N[i], color='b', length=0.08)
            if k>0.1: th=np.linspace(0,2*np.pi,50); ax3d.plot(*(p+(1/k)*N[i] + (1/k)*(np.outer(np.cos(th),T[i])+np.outer(np.sin(th),N[i]))).T, color='g')
            ax3d.set(xlim=(-.1,.5), ylim=(-.1,.5), zlim=(0,.5), title=f"t={t[i]:.2f}s | Gesamtkraft: {F_mag[i]:.2f} N")

        # 1. Berechne die reale Zeitdifferenz zwischen zwei Datenpunkten
        dt_data = t[1] - t[0]

        # 2. Definiere den "Skip" (wie viele Punkte übersprungen werden)
        frame_skip = 5

        # 3. Berechne das Intervall in Millisekunden:
        # Zeit pro Frame = dt_data * frame_skip (in Sekunden)
        # Millisekunden = Zeit pro Frame * 1000
        calc_interval = dt_data * frame_skip * 1000


        # WICHTIG: Einer Variable zuweisen (z.B. ani =)
        ani = FuncAnimation(
            fig2,
            update,
            frames=range(0, len(t), frame_skip),
            interval=calc_interval,
            repeat=True
        )

        # plt.show() MUSS nach der Zuweisung kommen
        plt.show()

        # Optional: Gib ani zurück, falls du die Methode in einer anderen Klasse aufrufst
        return ani