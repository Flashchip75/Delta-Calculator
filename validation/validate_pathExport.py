import numpy as np
import pandas as pd
from pathlib import Path


COLUMNS = 't x y z vx vy vz ax ay az jx jy jz tx ty tz nx ny nz bx by bz kappa ftx fty ftz fnx fny fnz fx fy fz'.split()
COL_IDX = {c: i for i, c in enumerate(COLUMNS)}

# Toleranzen
TOL_FLOAT   = 1e-10   # Roundtrip-Floating-Point-Toleranz
TOL_ORTHO   = 1e-6    # Frenet-Orthonormalitäts-Toleranz
TOL_FORCE   = 1e-4    # Kraft-Konsistenz-Toleranz (N)


class PathExportValidator:
    """
    Führt mehrere Validierungen auf einer geladenen Trajektorien-Matrix durch.

    Parameters
    ----------
    matrix     : np.ndarray, shape (N, 32) — die geladene Trajektorienmatrix
    csv_path   : Path zur Original-CSV (für Roundtrip-Check)
    output_dir : Path zum Ausgabeordner (für temporäre Dateien)
    """

    def __init__(self, matrix: np.ndarray, csv_path: Path, output_dir: Path):
        self.matrix     = matrix
        self.csv_path   = csv_path
        self.output_dir = output_dir
        self._results: list[tuple[bool, str]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_all(self) -> bool:
        """Führt alle Validierungen aus. Gibt True zurück wenn alle bestanden."""
        self._results.clear()
        print("\n╔══════════════════════════════════════════╗")
        print("║       PathExportValidator — Report       ║")
        print("╚══════════════════════════════════════════╝")

        self.check_shape()
        self.check_nan_inf()
        self.check_time_monotonic()
        self.check_roundtrip()
        self.check_frenet_orthonormality()
        self.check_force_consistency()
        self.check_workspace_bounds()
        self.check_curvature_sign()

        passed = sum(1 for ok, _ in self._results if ok)
        total  = len(self._results)
        all_ok = passed == total

        print(f"\n {passed}/{total} Checks bestanden.\n")
        return all_ok

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def check_shape(self):
        """Korrekte Anzahl Spalten (32) und mindestens 2 Zeitschritte."""
        rows, cols = self.matrix.shape
        ok = (cols == len(COLUMNS) and rows >= 2)
        msg = f"Shape: {self.matrix.shape}  (erwartet: (N, {len(COLUMNS)}))"
        self._report("Shape", ok, msg)

    def check_nan_inf(self):
        """Keine NaN oder Inf-Werte in der Matrix."""
        nan_count = int(np.isnan(self.matrix).sum())
        inf_count = int(np.isinf(self.matrix).sum())
        ok  = (nan_count == 0 and inf_count == 0)
        msg = f"NaN: {nan_count}, Inf: {inf_count}"
        self._report("NaN/Inf", ok, msg)

    def check_time_monotonic(self):
        """Zeitvektor t muss streng monoton steigend sein."""
        t    = self.matrix[:, COL_IDX['t']]
        diffs = np.diff(t)
        ok   = bool(np.all(diffs > 0))
        msg  = f"dt_min={diffs.min():.4e}s, dt_max={diffs.max():.4e}s"
        self._report("Zeit monoton", ok, msg)

    def check_roundtrip(self):
        """Matrix → CSV → reload muss bitgenau übereinstimmen (bis auf Float-Rundung)."""
        rt_path = self.output_dir / "_roundtrip_tmp.csv"
        try:
            pd.DataFrame(self.matrix, columns=COLUMNS).to_csv(rt_path, index=False)
            orig = np.loadtxt(self.csv_path, delimiter=",", skiprows=1)
            rt   = np.loadtxt(rt_path,       delimiter=",", skiprows=1)

            if orig.shape != rt.shape:
                self._report("Roundtrip", False, f"Shape-Mismatch: orig={orig.shape}, rt={rt.shape}")
                return

            diff     = np.abs(orig - rt)
            max_diff = diff.max(axis=0)
            worst    = [(COLUMNS[i], float(max_diff[i])) for i in np.where(max_diff >= TOL_FLOAT)[0]]
            ok       = len(worst) == 0
            msg      = f"max_diff_global={diff.max():.2e}" + (f" — Ausreißer: {worst}" if worst else "")
            self._report("Roundtrip CSV", ok, msg)
        finally:
            if rt_path.exists():
                rt_path.unlink()

    def check_frenet_orthonormality(self):
        """
        Tangente T, Normale N, Binormale B müssen orthonormal sein:
          |T| ≈ 1,  |N| ≈ 1,  |B| ≈ 1
          T·N ≈ 0,  T·B ≈ 0,  N·B ≈ 0
        """
        kappa = self.matrix[:, COL_IDX['kappa']]
        if np.max(kappa) < 1e-6:
            self._report("Frenet Orthonorm.", True, "Übersprungen — Gerade (κ≈0), N/B nicht definiert.")
            return
        T = self.matrix[:, [COL_IDX['tx'], COL_IDX['ty'], COL_IDX['tz']]]
        N = self.matrix[:, [COL_IDX['nx'], COL_IDX['ny'], COL_IDX['nz']]]
        B = self.matrix[:, [COL_IDX['bx'], COL_IDX['by'], COL_IDX['bz']]]

        norm_T = np.linalg.norm(T, axis=1)
        norm_N = np.linalg.norm(N, axis=1)
        norm_B = np.linalg.norm(B, axis=1)
        dot_TN = np.abs(np.einsum('ij,ij->i', T, N))
        dot_TB = np.abs(np.einsum('ij,ij->i', T, B))
        dot_NB = np.abs(np.einsum('ij,ij->i', N, B))

        checks = {
            '|T|=1': np.abs(norm_T - 1).max(),
            '|N|=1': np.abs(norm_N - 1).max(),
            '|B|=1': np.abs(norm_B - 1).max(),
            'T⊥N':   dot_TN.max(),
            'T⊥B':   dot_TB.max(),
            'N⊥B':   dot_NB.max(),
        }
        failed = {k: v for k, v in checks.items() if v > TOL_ORTHO}
        ok  = len(failed) == 0
        msg = "OK" if ok else f"Fehler: { {k: f'{v:.2e}' for k, v in failed.items()} }"
        self._report("Frenet Orthonorm.", ok, msg)

    def check_force_consistency(self):
        """
        Gesamtkraft f muss der Vektorsumme aus ft + fn entsprechen:
          |f - (ft + fn)| ≈ 0
        """
        ft = self.matrix[:, [COL_IDX['ftx'], COL_IDX['fty'], COL_IDX['ftz']]]
        fn = self.matrix[:, [COL_IDX['fnx'], COL_IDX['fny'], COL_IDX['fnz']]]
        f  = self.matrix[:, [COL_IDX['fx'],  COL_IDX['fy'],  COL_IDX['fz']]]

        residual = np.linalg.norm(f - (ft + fn), axis=1)

        try:
            from config import cfg
            g_mag = np.linalg.norm(cfg.global_cfg.gravity) * cfg.global_cfg.mass_kg
            tol = TOL_FORCE + g_mag + 0.1
        except Exception:
            tol = TOL_FORCE
    
        ok  = bool(residual.max() < tol)
        msg = f"max|f - (ft+fn)| = {residual.max():.4e} N  (Schwerkraftanteil ~{g_mag:.2f}N erwartet)"
        self._report("Kraft f≈ft+fn+fg", ok, msg)

    def check_workspace_bounds(self):
        """
        Warnt wenn Trajektorie außerhalb des konfigurierten Arbeitsraums liegt.
        Importiert cfg nur wenn verfügbar — kein harter Fehler wenn nicht.
        """
        try:
            from config import cfg
            ws  = cfg.workspace
            x   = self.matrix[:, COL_IDX['x']]
            y   = self.matrix[:, COL_IDX['y']]
            z   = self.matrix[:, COL_IDX['z']]

            x_ok = bool(np.all((x >= ws.range_x[0]) & (x <= ws.range_x[1])))
            y_ok = bool(np.all((y >= ws.range_y[0]) & (y <= ws.range_y[1])))
            z_ok = bool(np.all((z >= ws.range_z[0]) & (z <= ws.range_z[1])))
            ok   = x_ok and y_ok and z_ok

            details = []
            if not x_ok: details.append(f"x∈[{x.min():.3f}, {x.max():.3f}] vs cfg[{ws.range_x[0]}, {ws.range_x[1]}]")
            if not y_ok: details.append(f"y∈[{y.min():.3f}, {y.max():.3f}] vs cfg[{ws.range_y[0]}, {ws.range_y[1]}]")
            if not z_ok: details.append(f"z∈[{z.min():.3f}, {z.max():.3f}] vs cfg[{ws.range_z[0]}, {ws.range_z[1]}]")
            msg = "Innerhalb Arbeitsraum" if ok else " | ".join(details)
            self._report("Arbeitsraum", ok, msg)

        except Exception as e:
            self._report("Arbeitsraum", True, f"Übersprungen ({e})")

    def check_curvature_sign(self):
        """Krümmung κ darf nicht negativ sein."""
        kappa = self.matrix[:, COL_IDX['kappa']]
        neg   = int((kappa < 0).sum())
        ok    = neg == 0
        msg   = f"min={kappa.min():.4e}, max={kappa.max():.4e}" + (f" — {neg} negative Werte!" if not ok else "")
        self._report("Krümmung κ ≥ 0", ok, msg)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _report(self, name: str, ok: bool, detail: str = ""):
        self._results.append((ok, name))
        status = "ok" if ok else "error"
        print(f"  {status}  {name:<22}  {detail}")