"""
robot_geometry.py
=================
Liest config.txt ein. Stellt Robotergeometrie bereit:
  - Motorpositionen, Achsen, Arm-Basisvektoren
  - Arm-Parameter (Laenge, Masse, Traegheit, Winkelgrenzen)
  - IK: Motorwinkel phi aus Endeffektorposition (Kugelschnitt-Methode)

Kein direkter Aufruf anderer Module.
"""

import os
import json
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

# ==============================================================================
# Datenklassen
# ==============================================================================

@dataclass
class ArmParams:
    length:  float
    mass:    float
    inertia: float          # 1/3 * m * L^2 um Motorende

@dataclass
class MotorConfig:
    name:       str
    position:   np.ndarray
    axis_cfg:   Optional[np.ndarray]   # None = AUTO
    upper:      ArmParams
    lower:      ArmParams
    theta_min:  float                  # rad
    theta_max:  float                  # rad
    # Abgeleitet (nach build()):
    axis_vec:   np.ndarray = field(default_factory=lambda: np.zeros(3))
    radial_vec: np.ndarray = field(default_factory=lambda: np.zeros(3))
    drop_vec:   np.ndarray = field(default_factory=lambda: np.zeros(3))


# ==============================================================================
# RobotGeometry
# ==============================================================================

class RobotGeometry:
    """
    Laedt config.json und berechnet alle geometrischen Basisgroessen.
    """

    def __init__(self, configPath: Union[str, Path] = Path(__file__).parent.parent / "config.json"):
        with open(configPath, "r", encoding="utf-8") as f:
            self._cfg = json.load(f)
        self._parse()
        self._build_geometry()

    # ------------------------ Geometrien einlesen --------------------------------------------
    def _parse(self):
        cfg = self._cfg

        # Global
        glob = cfg.get("global", {})
        self.gravity         = np.array(glob.get("gravity", [0.0, 0.0, -9.81]))
        self.payload_mass    = float(glob.get("payload_mass", 0.1))
        self.singularity_rad = np.deg2rad(float(glob.get("singularity_margin_deg", 5.0)))
        self.trajectory_csv  = glob.get("trajectory_csv", "trajectory.csv")
        self.output_dir      = glob.get('output_dir', 'output')

        # Workspace
        ws = cfg.get("workspace", {})
        self.ws_res     = int(ws.get("resolution", 25))
        self.ws_range_x = tuple(ws.get("range_x", [-0.4, 0.4]))
        self.ws_range_y = tuple(ws.get("range_y", [-0.4, 0.4]))
        self.ws_range_z = tuple(ws.get("range_z", [-1.3, -0.1]))

        # Motorpositionen
        self.motors: list[MotorConfig] = []
        motors_cfg = cfg.get("motors", {})
        labels = ["A", "B", "C"]

        for lbl in labels:
            m_cfg = motors_cfg.get(lbl, {})
            pos = np.array(m_cfg.get("position", [0.0, 0.0, 0.0]))
            
            axis_val = m_cfg.get("axis", "AUTO")
            axis = None if axis_val == "AUTO" else np.array(axis_val)

            ul = float(m_cfg.get("upper_length", 0.5))
            um = float(m_cfg.get("upper_mass", 0.3))
            ll = float(m_cfg.get("lower_length", 1.0))
            lm = float(m_cfg.get("lower_mass", 0.15))

            th_min = np.deg2rad(float(m_cfg.get("theta_min", 5.0)))
            th_max = np.deg2rad(float(m_cfg.get("theta_max", 90.0)))

            self.motors.append(MotorConfig(
                name       = lbl,
                position   = pos,
                axis_cfg   = axis,
                upper      = ArmParams(ul, um, (1/3) * um * ul**2),
                lower      = ArmParams(ll, lm, (1/3) * lm * ll**2),
                theta_min  = th_min,
                theta_max  = th_max,
            ))

    # --------------------------------------------------------------------------
    def _build_geometry(self):
        pA, pB, pC = [m.position for m in self.motors] # Positionen der 3 Motoren

        n = np.cross(pB - pA, pC - pA) # Normalenvektor der Motoren ebene
        assert np.linalg.norm(n) > 1e-9, "Motorpositionen kollinear."
        self.plane_normal = n / np.linalg.norm(n) # Normierter Normalenvektor

        # plane_normal soll nach oben zeigen (z > 0)
        if self.plane_normal[2] < 0:
            self.plane_normal = -self.plane_normal

        self.center = (pA + pB + pC) / 3.0 # Mittelpunkt der Motoren

        # --- Verbindungsvektoren (Dreiecksseiten) berechnen ---
        v_AB = pB - pA
        v_BC = pC - pB
        v_CA = pA - pC

        auto_axes = [
            v_AB / np.linalg.norm(v_AB), # Achse für Motor A (zeigt zu B)
            v_BC / np.linalg.norm(v_BC), # Achse für Motor B (zeigt zu C)
            v_CA / np.linalg.norm(v_CA)  # Achse für Motor C (zeigt zu A)
        ]

        for i, mc in enumerate(self.motors):
            # 1. Achsenvektor setzen (entweder aus Config oder automatisch v_AB, v_BC, v_CA)
            if mc.axis_cfg is not None:
                mc.axis_vec = mc.axis_cfg / np.linalg.norm(mc.axis_cfg)
            else:
                mc.axis_vec = auto_axes[i]

            # 2. Drop-Vector: Senkrecht zur Motorachse, zeigt in Richtung Schwerkraft (unten)
            g_hat = self.gravity / np.linalg.norm(self.gravity)
            g_perp = g_hat - np.dot(g_hat, mc.axis_vec) * mc.axis_vec
            if np.linalg.norm(g_perp) > 1e-9:
                mc.drop_vec = g_perp / np.linalg.norm(g_perp)
            else:
                mc.drop_vec = np.array([0.0, 0.0, -1.0]) # Fallback

            # 3. Radial-Vector: Zeigt waagerecht vom Roboter weg (0-Grad-Winkel für IK).
            # MUSS zwingend senkrecht auf Achse und Drop-Vektor stehen!
            # Kreuzprodukt (drop x achse) ergibt einen Vektor der orthogonal nach "außen" zeigt.
            r_vec = np.cross(mc.drop_vec, mc.axis_vec)
            mc.radial_vec = r_vec / np.linalg.norm(r_vec)

    # --------------------------------------------------------------------------
    # IK - Kugelschnitt-Methode
    # --------------------------------------------------------------------------

    def ik(self, motor_idx: int, end_pos: np.ndarray) -> tuple[bool, float]:
        """
        Berechnet Motorwinkel phi fuer Motor motor_idx bei Endeffektorposition
        end_pos.

        Methode: Geometrischer Kugelschnitt.
          Gelenk k_i liegt auf Kreis (Armebene) UND auf Kugel S(e, L_u).
          A*cos(phi) + B*sin(phi) = C
          Loesung via Hilfswinkel: phi = atan2(B,A) ± arccos(C/sqrt(A²+B²))

        Winkelgrenzen theta_min/theta_max werden durchgesetzt.
        select_lower: Loesung mit groesserem sin(phi) (Arm haengt nach unten).

        Rueckgabe: (valid, phi)
        """
        mc    = self.motors[motor_idx]
        r     = mc.radial_vec
        d     = mc.drop_vec
        p     = mc.position
        Lo    = mc.upper.length
        Lu    = mc.lower.length

        # Trigonometrische Normalform A*cos(theta)+B*sin(theta) = C

        f  = p - end_pos
        A  = 2.0 * Lo * float(np.dot(r, f))
        B  = 2.0 * Lo * float(np.dot(d, f))
        C  = Lu**2 - Lo**2 - float(np.dot(f, f))

        # Auf R_AB * cos(theta+psi) = C bringen

        R_AB = np.sqrt(A**2 + B**2)
        if R_AB < 1e-12:
            return False, 0.0

        ratio = C / R_AB
        if abs(ratio) > 1.0:
            return False, 0.0

        psi   = np.arctan2(B, A)
        delta = np.arccos(np.clip(ratio, -1.0, 1.0))

        # Fallunterscheidung 

        phi_a = psi + delta
        phi_b = psi - delta

        # Normiere auf [-pi, pi]
        phi_a = (phi_a + np.pi) % (2 * np.pi) - np.pi
        phi_b = (phi_b + np.pi) % (2 * np.pi) - np.pi

        # Waehle Loesung mit groesserem sin(phi) (haengt tiefer)
        phi = phi_a if np.sin(phi_a) >= np.sin(phi_b) else phi_b

        # Winkelgrenzen pruefen
        if phi < mc.theta_min or phi > mc.theta_max:
            # Andere Loesung versuchen
            phi_alt = phi_b if phi == phi_a else phi_a
            if mc.theta_min <= phi_alt <= mc.theta_max:
                phi = phi_alt
            else:
                return False, 0.0

        # Gelenk berechnen
        k = p + Lo * (np.cos(phi) * r + np.sin(phi) * d)

        # Singularitaetspruefung
        u_vec = end_pos - k
        o_vec = k - p
        denom = np.linalg.norm(u_vec) * np.linalg.norm(o_vec)
        if denom < 1e-12:
            return False, 0.0
        cos_a = np.clip(np.dot(u_vec, o_vec) / denom, -1.0, 1.0)
        if np.arccos(abs(cos_a)) < self.singularity_rad:
            return False, 0.0

        # Gelenk muss unterhalb der Motorebene liegen
        if float(np.dot(k - p, self.plane_normal)) > 0.0:
            return False, 0.0

        return True, phi

    def ik_all(self, end_pos: np.ndarray) -> tuple[bool, np.ndarray]:
        """IK fuer alle drei Motoren. Rueckgabe: (valid, phi_vec(3,))"""
        phis = []
        for i in range(3):
            ok, phi = self.ik(i, end_pos)
            if not ok:
                return False, np.zeros(3)
            phis.append(phi)
        return True, np.array(phis)

    def joint_pos(self, motor_idx: int, phi: float) -> np.ndarray:
        """Gelenk-Endpunkt k_i fuer gegebenes phi."""
        mc = self.motors[motor_idx]
        return (mc.position + mc.upper.length * (np.cos(phi) * mc.radial_vec  + np.sin(phi) * mc.drop_vec))

    def summary(self):
        print("=" * 56)
        print("  Delta Robot - Konfiguration")
        print("=" * 56)
        print(f"  Zentrum      : {self.center}")
        print(f"  Ebene-Normal : {self.plane_normal}")
        print(f"  Schwerkraft  : {self.gravity}")
        print(f"  Payload      : {self.payload_mass} kg")
        for mc in self.motors:
            th_min = np.rad2deg(mc.theta_min)
            th_max = np.rad2deg(mc.theta_max)
            print(f"  Motor {mc.name}: pos={mc.position}  "
                  f"theta=[{th_min:.0f}°,{th_max:.0f}°]  "
                  f"L_o={mc.upper.length}m  L_u={mc.lower.length}m")
        print("=" * 56)


if __name__ == "__main__":
    robot = RobotGeometry("config.txt")
    robot.summary()
