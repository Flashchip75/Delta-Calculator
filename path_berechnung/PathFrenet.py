import numpy as np


class PathFrenet:
    def __init__(self, pts):
        # 1. Erste und zweite Ableitung der Punkte (Geschwindigkeit und Beschleunigung im Raum) -> Wird anhand des Bahnparameters 0 <= t <= 1 bestimmt.
        d1 = np.gradient(pts, axis=0)
        d2 = np.gradient(d1, axis=0)

        # 2. Tangentenvektor T = d1 / |d1| -> wird sofort normiert um ein Zittern der Kurve zu vermeiden
        norm_d1 = np.linalg.norm(d1, axis=1, keepdims=True)
        norm_d1 = np.maximum(norm_d1, 1e-12)  # Division durch 0 verhindern
        self.T = d1 / norm_d1

        # 3. Krümmung (Kappa) = |d1 x d2| / |d1|^3
        cross_d1_d2 = np.cross(d1, d2)
        norm_cross = np.linalg.norm(cross_d1_d2, axis=1)
        self.kappa = norm_cross / (norm_d1[:, 0] ** 3)

        # 4. Binormalenvektor B = (d1 x d2) / |d1 x d2|
        norm_cross_keep = np.maximum(norm_cross[:, None], 1e-12)
        self.B = cross_d1_d2 / norm_cross_keep

        # 5. Normalenvektor N = B x T
        self.N = np.cross(self.B, self.T)


        # 6. Rausch-Unterdrückung auf geraden Strecken!
        # Wo keine Krümmung ist, ist N und B mathematisch undefiniert.
        # Wir setzen sie auf 0, um das "Zittern" der Kräfte komplett zu eliminieren.
        straight_line_mask = self.kappa < 1e-6
        self.N[straight_line_mask] = 0.0
        self.B[straight_line_mask] = 0.0
        self.kappa[straight_line_mask] = 0.0

        # ==========================================================
        # 7. TEST: PROFESSOR-METHODE (Normierung des Krümmungsvektors)
        # Zum Testen einkommentieren (überschreibt self.kappa am Ende)
        # ==========================================================
        #K_vec = self.kappa[:, None] * self.N
        #norm_K_vec = np.linalg.norm(K_vec, axis=1, keepdims=True)
        #norm_K_vec = np.maximum(norm_K_vec, 1e-12)
        #K_vec_normiert = K_vec / norm_K_vec
        #self.kappa = np.linalg.norm(K_vec_normiert, axis=1)


# Frage für GSP am 12.05.2025 -> Wird im Code doch normiert, siehe bsp. norm_d1 = np.linalg.norm(d1,...)
# Wieso stimmen Graphen erst überein, wenn Tangentenvektoren bzw. Krümmungsvektoren nicht mehr nomriert werden???