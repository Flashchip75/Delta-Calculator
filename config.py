"""
config.py
=========
Zentrale Konfiguration für beide Pipelines.
Lädt config.json einmalig und stellt typisierte Dataclasses bereit.

Verwendung:
    from config import cfg          # Singleton (Standard)
    from config import load_config  # Explizit laden (z.B. für Tests)
"""

import json
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Dataclasses — ein Abschnitt pro JSON-Sektion
# ---------------------------------------------------------------------------

@dataclass
class GlobalConfig:
    """Gemeinsame Felder beider Pipelines -> JSON-Sektion 'global'."""
    gravity: list[float]            # Vektor [x, y, z] in m/s²
    mass_kg: float                  # Nutzlast-Trägermasse in kg
    payload_mass: float             # Nutzlast in kg
    singularity_margin_deg: float   # Sicherheitsabstand zur Singularität in °
    trajectory_csv: str             # Dateiname der Export-CSV
    output_dir: str                 # Ausgabeordner (relativ zum Projekt-Root)


@dataclass
class plottingConfig:
    """Plotting-spezifische Parameter -> JSON-Sektion 'plotting'."""
    dpi: int
    bbox_inches: str
    trajectory_plot: str             # Dateiname für den Trajektorien-Plot
    forces_plot: str                # Dateiname für den Kraft-Plot

@dataclass
class WorkspaceConfig:
    """Arbeitsraum-Raster -> JSON-Sektion 'workspace'."""
    resolution: int                 # Punkte pro Achse
    range_x: list[float]            # [min, max] in m
    range_y: list[float]            # [min, max] in m
    range_z: list[float]            # [min, max] in m


@dataclass
class PathConfig:
    """Trajektorien-Parameter -> JSON-Sektion 'path' (Pipeline 1)."""
    duration_s: float               # Gesamtdauer in Sekunden
    points: int                     # Anzahl Stützpunkte
    gain: float                     # Blend-Gain
    blend: float                    # Übergangsradius
    scale_m: float                  # Skalierungsfaktor m -> m (0.001)
    offset_m: int                   # Offset in m, um Ursprung zu verschieben (z.B. 1000 für 1m über Boden)
    path_profiles: str              # Dateiname der Pfadgeometrie-Profile (relativ zum Projekt-Root)

@dataclass
class VisionConfig:
    """Vision-spezifische Parameter -> JSON-Sektion 'cVision'."""
    reCalibration: bool             # Bei True: Kalibrierung vor Erkennung durchführen
    aruco_dict: str                 # ArUco-Dict für Erkennung
    mToPixel: float                 # Gespeicherter px/m-Wert (verwendet wenn reCalibration=False)
    calibration_source: str         # Bildquelle für Kalibrierung
    calibration_norm_m: int         # Referenzlänge in m für Kalibrierung
    calibration_id: int             # ArUco-Marker-ID für Kalibrierung
    model_path: str                 # Pfad zum YOLO-Modell
    conf_threshold: float           # Mindestvertrauen für YOLO-Erkennung
    visiualisations: dict           # Farben und Stärken für Bounding Boxes und Kreise

@dataclass
class MotorConfig:
    """Konfiguration eines einzelnen Motors -> JSON-Sektion 'motors.<ID>'."""
    position: list[float]           # Montageposition [x, y, z] in m
    axis: str                       # Rotationsachse ("AUTO" oder "X"/"Y"/"Z")
    upper_length: float             # Oberlänge des Arms in m
    upper_mass: float               # Masse des Oberarms in kg
    lower_length: float             # Unterlänge des Arms in m
    lower_mass: float               # Masse des Unterarms in kg
    theta_min: float                # Minimaler Gelenkwinkel in °
    theta_max: float                # Maximaler Gelenkwinkel in °


@dataclass
class MotorsConfig:
    """Alle drei Motoren -> JSON-Sektion 'motors'."""
    A: MotorConfig
    B: MotorConfig
    C: MotorConfig


@dataclass
class AppConfig:
    """Haupt-Config-Objekt — enthält alle Sektionen."""
    global_cfg: GlobalConfig
    plotting: plottingConfig
    workspace: WorkspaceConfig
    path: PathConfig
    cVision: VisionConfig
    motors: MotorsConfig


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def _require(section: dict, key: str, section_name: str):
    """Hilfsfunktion: Wert holen oder KeyError mit klarer Meldung werfen."""
    val = section.get(key)
    if val is None:
        raise KeyError(f"Missing config key: '{section_name}.{key}'")
    return val


def _load_motor(data: dict, motor_id: str) -> MotorConfig:
    """Lädt einen einzelnen Motor-Block aus dem Dict."""
    s = f"motors.{motor_id}"
    return MotorConfig(
        position     = _require(data, "position",     s),
        axis         = _require(data, "axis",         s),
        upper_length = _require(data, "upper_length", s),
        upper_mass   = _require(data, "upper_mass",   s),
        lower_length = _require(data, "lower_length", s),
        lower_mass   = _require(data, "lower_mass",   s),
        theta_min    = _require(data, "theta_min",    s),
        theta_max    = _require(data, "theta_max",    s),
    )


def load_config(config_path: Path | str | None = None) -> AppConfig:
    """
    Lädt config.json und gibt ein typisiertes AppConfig-Objekt zurück.

    Parameters
    ----------
    config_path : Pfad zur config.json.
                  Standard: selbes Verzeichnis wie config.py
    """
    if config_path is None:
        # config.py und config.json liegen im selben Ordner (Projekt-Root)
        config_path = Path(__file__).parent / "config.json"

    with open(config_path, "r") as f:
        raw = json.load(f)

    g  = raw.get("global",    {})
    pl  = raw.get("plotting",  {})
    ws = raw.get("workspace", {})
    p  = raw.get("path",      {})
    cv = raw.get("cVision",   {})
    m  = raw.get("motors",    {})

    global_cfg = GlobalConfig(
        gravity                = _require(g, "gravity",                "global"),
        mass_kg                = _require(g, "mass_kg",                "global"),
        payload_mass           = _require(g, "payload_mass",           "global"),
        singularity_margin_deg = _require(g, "singularity_margin_deg", "global"),
        trajectory_csv         = _require(g, "trajectory_csv",         "global"),
        output_dir             = _require(g, "output_dir",             "global"),
    )

    plotting_cfg = plottingConfig(
        dpi             = _require(pl, "dpi", "plotting"),
        bbox_inches     = _require(pl, "bbox_inches", "plotting"),
        trajectory_plot = _require(pl, "trajectory_plot", "plotting"),
        forces_plot     = _require(pl, "forces_plot", "plotting"),
    )

    workspace_cfg = WorkspaceConfig(
        resolution = _require(ws, "resolution", "workspace"),
        range_x    = _require(ws, "range_x",    "workspace"),
        range_y    = _require(ws, "range_y",    "workspace"),
        range_z    = _require(ws, "range_z",    "workspace"),
    )

    path_cfg = PathConfig(
        duration_s      = _require(p, "duration_s",     "path"),
        points          = _require(p, "points",         "path"),
        gain            = _require(p, "gain",           "path"),
        blend           = _require(p, "blend",          "path"),
        scale_m         = _require(p, "scale_m",        "path"),
        offset_m        = _require(p, "offset_m",       "path"),
        path_profiles   = _require(p, "path_profiles",  "path"),
    )

    vision_cfg = VisionConfig(
        reCalibration           = _require(cv, "reCalibration",         "cVision"),
        aruco_dict              = _require(cv, "aruco_dict",            "cVision"),
        mToPixel                = _require(cv, "mToPixel",              "cVision"),
        calibration_source      = _require(cv, "calibration_source",    "cVision"),
        calibration_norm_m      = _require(cv, "calibration_norm_m",    "cVision"),
        calibration_id          = _require(cv, "calibration_id",        "cVision"),
        model_path              = _require(cv, "model_path",            "cVision"),
        conf_threshold          = _require(cv, "conf_threshold",        "cVision"),
        visiualisations         = _require(cv, "visiualisations",       "cVision"),
    )

    motors_cfg = MotorsConfig(
        A = _load_motor(_require(m, "A", "motors"), "A"),
        B = _load_motor(_require(m, "B", "motors"), "B"),
        C = _load_motor(_require(m, "C", "motors"), "C"),
    )

    return AppConfig(
        global_cfg = global_cfg,
        plotting   = plotting_cfg,
        workspace  = workspace_cfg,
        path       = path_cfg,
        cVision    = vision_cfg,
        motors     = motors_cfg,
    )


# ---------------------------------------------------------------------------
# Singleton — wird beim ersten Import einmalig geladen
# ---------------------------------------------------------------------------
#cfg: AppConfig = load_config()