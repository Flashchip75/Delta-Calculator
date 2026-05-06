# Struct zum Speichern der Geometrieiengaben


from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class GlobalStruct:
    gravity: List[float]
    mass_kg: float
    payload_mass: float
    singularity_margin_deg: float
    trajectory_csv: str
    output_dir: str


@dataclass
class WorkspaceStruct:
    resolution: int
    range_x: List[float]
    range_y: List[float]
    range_z: List[float]


@dataclass
class PathStruct:
    duration_s: float
    points: int
    gain: float
    blend: float
    scale_m: float


@dataclass
class CVisionStruct:
    reCalibration: bool
    aruco_dict: str
    mmToPixel: float
    calibration_source: str
    calibration_norm_mm: float
    calibration_id: int


@dataclass
class MotorStruct:
    position: List[float]
    axis: Union[str, List[float]]
    upper_length: float
    upper_mass: float
    lower_length: float
    lower_mass: float
    theta_min: float
    theta_max: float



@dataclass
class GeoStruct:
    global_data: GlobalStruct
    workspace: WorkspaceStruct
    path: PathStruct
    cVision: CVisionStruct
    motors: Dict[str, MotorStruct]


def write_geo_struct():
    """
    Erstellt das komplette GeoStruct.
    """

    global_data = GlobalStruct(
        gravity=[0.0, 0.0, -9.81],
        mass_kg=1.0,
        payload_mass=0.100,
        singularity_margin_deg=5.0,
        trajectory_csv="trajectory.csv",
        output_dir="output"
    )

    workspace = WorkspaceStruct(
        resolution=25,
        range_x=[-0.4, 0.4],
        range_y=[-0.4, 0.4],
        range_z=[-1.3, -0.1]
    )

    path = PathStruct(
        duration_s=5.0,
        points=1000,
        gain=50.0,
        blend=0.0,
        scale_m=0.001
    )

    cVision = CVisionStruct(
        reCalibration=True,
        aruco_dict="DICT_4X4_100",
        mmToPixel=0,
        calibration_source="media/calibrationTest.jpg",
        calibration_norm_mm=100,
        calibration_id=0
    )

    motors = {
        "A": MotorStruct(
            position=[0.400, 0.100, -0.100],
            axis="AUTO",
            upper_length=0.700,
            upper_mass=0.600,
            lower_length=1.00,
            lower_mass=0.150,
            theta_min=5.0,
            theta_max=90.0
        ),
        "B": MotorStruct(
            position=[-0.50, 0.260, 0.00],
            axis="AUTO",
            upper_length=0.800,
            upper_mass=0.300,
            lower_length=1.00,
            lower_mass=0.150,
            theta_min=5.0,
            theta_max=90.0
        ),
        "C": MotorStruct(
            position=[-0.150, -0.260, -0.120],
            axis="AUTO",
            upper_length=0.700,
            upper_mass=0.300,
            lower_length=1.00,
            lower_mass=0.150,
            theta_min=5.0,
            theta_max=90.0
        )
    }

    return GeoStruct(
        global_data=global_data,
        workspace=workspace,
        path=path,
        cVision=cVision,
        motors=motors
    )