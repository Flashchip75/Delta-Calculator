import numpy as np

class Curve:
    def __init__(self, cfg):
        self.c = cfg

    def __call__(self, t):
        c = self.c
        typ, p = c['type'], np.array(c.get('pts', []))

        # Linie definieren: {"type": "Line", "pts": [[x,y,z], [x,y,z]]}
        if typ == 'Line':
            return p[0] * (1 - t) + p[1] * t

        # Bezier-Kurve definieren: {"type": "Bezier", "pts": [[x,y,z], [x,y,z], [x,y,z], [x,y,z]]}

        # Die Bezierkurve wird über 4 Punkte im Raum definiert.

        # Dabei legen Punkt 1 und 4 den Start bzw. Endpunkt fest. Über die Punkte 2 und 3 werden die Tangentialvektoren festgelegt.
        if typ == 'Bezier':
            return (1 - t)**3 * p[0] + 3 * t * (1 - t)**2 * p[1] + 3 * t**2 * (1 - t) * p[2] + t**3 * p[3]

        # Kreis bzw. Kreisbogen definieren: {"type": "Circle/Arc", "c": [x,y,z], "r": R, "u":[x,y,z], "v": [x,y,z], "a": [Startwinkel, Endwinkel]}

        # Kreis und Kreisbogen werden über den Mittelpunkt c, den Radius r, die Ebenen u, v und Bogenlänge in rad a [Startwinkel, Endwinkel] bestimmt.
        if typ in ['Arc', 'Circle']:
            a = c.get('a', [0, 2 * np.pi])
            ang = a[0] + t * (a[1] - a[0])
            return np.array(c['c']) + c['r'] * (np.cos(ang) * np.array(c['u']) + np.sin(ang) * np.array(c['v']))

        # "T": 0.2, "v0": 10.0, "v1": 0.0, "N": 200 Zeit, Anfangsgeschwindigkeit, Endgeschwindigkeit, Punktezahl

class Trajectory:
    def __init__(self, json_data, default_ppm=1000):
        self.segments = []

        for c in json_data:
            # 1. Grobe Längenbestimmung (wird nur benötigt, falls 'N' nicht im JSON steht)
            r_approx = np.array([Curve(c)(t) for t in np.linspace(0, 1, 100)])
            length = np.sum(np.linalg.norm(np.diff(r_approx, axis=0), axis=1))

            # 2. Bestimme Punktanzahl N (entweder aus JSON oder über ppm berechnet)
            num_points = c.get("N", max(2, int(length * default_ppm)))

            # 3. DIREKTE BERECHNUNG: Erzeugt die Punkte direkt aus der Kurvengleichung
            # t läuft in gleichmäßigen Schritten von 0 bis 1
            t_values = np.linspace(0, 1, num_points)
            segment_cloud = np.array([Curve(c)(t) for t in t_values])

            # Speichere das Segment ab
            self.segments.append({
                "type": c["type"],
                "cloud": segment_cloud,
                "length": length,
                "num_points": num_points,
                "cfg": c
            })

        # Erzeuge eine kombinierte Punktewolke für die gesamte Trajektorie
        if self.segments:
            self.cloud = np.vstack([seg["cloud"] for seg in self.segments])
            # Duplikate entfernen
            diff = np.linalg.norm(np.diff(self.cloud, axis=0), axis=1)
            mask = np.insert(diff > 1e-9, 0, True)
            self.cloud = self.cloud[mask]
        else:
            self.cloud = np.array([])