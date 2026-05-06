import os
import json
import numpy as np
from pathlib import Path

class PhysicsEngine:
    @staticmethod
    def compute(pts: np.ndarray, frenet, kin) -> dict[str, np.ndarray]:
        """
        Compute kinematics and force-related quantities along a trajectory.

        Parameters
        ----------
        pts : np.ndarray, shape (N, 3)
            Cartesian trajectory points [m].
        frenet : PathFrenet
            Frenet frame data with attributes:
            - T : np.ndarray, shape (N, 3), tangent vectors
            - N : np.ndarray, shape (N, 3), normal vectors
            - kappa : np.ndarray, shape (N,), curvature [1/m]
        kin : PathKinematics
            Kinematic data with attributes:
            - t : np.ndarray, shape (N,), time [s]
            - v : np.ndarray, shape (N,), velocity [m/s]
            - a : np.ndarray, shape (N,), tangential acceleration [m/s²]

        Returns
        -------
        Dict[str, np.ndarray]
            Dictionary of 1D arrays (length N) containing:

            Time & position:
            - t                  : time [s]
            - x, y, z            : position [m]

            Velocity:
            - vx, vy, vz         : velocity components [m/s]

            Acceleration (derived from forces, m=1 kg):
            - ax, ay, az         : acceleration components [m/s²]

            Jerk:
            - jx, jy, jz         : jerk components [m/s³]

            Frenet frame:
            - tx, ty, tz         : tangent vector
            - nx, ny, nz         : normal vector
            - bx, by, bz         : binormal vector
            - kappa              : curvature [1/m]

            Forces (m = 1 kg normalized):
            - ftx, fty, ftz      : tangential force [N]
            - fnx, fny, fnz      : normal force [N]
            - fx,  fy,  fz       : total force [N]
        """
        B = np.cross(frenet.T, frenet.N)  # Binormalenvektor [1]
        v_vec = kin.v[:, None] * frenet.T  # Geschwindigkeit [m/s]
        
        F_t_vec = kin.a[:, None] * frenet.T  # Tangentialkraft [N]
        F_n_vec = (kin.v ** 2)[:, None] * frenet.kappa[:, None] * frenet.N  # Normalkraft [N]
        F_vec = F_t_vec + F_n_vec  # Gesamtkraft [N]

        a_vec = F_vec  # Beschleunigung [m/s²] (da m=1kg)
        j_vec = np.gradient(a_vec, kin.t, axis=0)  # Ruck [m/s³]
        
        return {
            't':     kin.t,
            'x':     pts[:, 0],     'y':     pts[:, 1],     'z':     pts[:, 2],
            'vx':    v_vec[:, 0],   'vy':    v_vec[:, 1],   'vz':    v_vec[:, 2],
            'ax':    a_vec[:, 0],   'ay':    a_vec[:, 1],   'az':    a_vec[:, 2],
            'jx':    j_vec[:, 0],   'jy':    j_vec[:, 1],   'jz':    j_vec[:, 2],
            'tx':    frenet.T[:, 0],'ty':    frenet.T[:, 1],'tz':    frenet.T[:, 2],
            'nx':    frenet.N[:, 0],'ny':    frenet.N[:, 1],'nz':    frenet.N[:, 2],
            'bx':    B[:, 0],       'by':    B[:, 1],       'bz':    B[:, 2],
            'kappa': frenet.kappa,
            'ftx':   F_t_vec[:, 0], 'fty':   F_t_vec[:, 1], 'ftz':   F_t_vec[:, 2],
            'fnx':   F_n_vec[:, 0], 'fny':   F_n_vec[:, 1], 'fnz':   F_n_vec[:, 2],
            'fx':    F_vec[:, 0],   'fy':    F_vec[:, 1],   'fz':    F_vec[:, 2],
        }

    @staticmethod
    def export_to_csv(
        data: dict[str, np.ndarray],
        filepath: str | Path,
        delimiter: str = ","
    ) -> None:
        """
        Export a dict of 1D numpy arrays to a CSV file.

        Parameters
        ----------
        data : dict[str, np.ndarray]
            Dictionary with keys as column names and values as 1D arrays (length N).
        filepath : str | Path
            Output CSV file path.
        delimiter : str
            Column separator (default: ",").
        """

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        keys = list(data.keys())

        try:
            arr = np.column_stack([data[k] for k in keys])
        except ValueError as e:
            raise ValueError("All arrays must have same length!") from e

        header = delimiter.join(keys)

        np.savetxt(
            filepath,
            arr,
            delimiter=delimiter,
            header=header,
            comments="",
            fmt="%.6f"
        )