from dataclasses import dataclass, field


@dataclass
class MotorGeoData:
    position: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    upper_length: float = 0.7
    upper_mass: float = 0.3
    lower_length: float = 2.5
    lower_mass: float = 0.15
    theta_min: float = 5.0
    theta_max: float = 90.0


@dataclass
class GeoData:
    advanced: bool = False
    gravity: list[float] = field(default_factory=lambda: [0.0, 0.0, -9.81])
    mass_kg: float = 1.0
    payload_mass: float = 0.1
    singularity_margin_deg: float = 5.0
    workspace_resolution: int = 25
    range_x: list[float] = field(default_factory=lambda: [-0.4, 0.4])
    range_y: list[float] = field(default_factory=lambda: [-0.4, 0.4])
    range_z: list[float] = field(default_factory=lambda: [-1.3, -0.1])
    common_upper_length: float = 0.7
    common_upper_mass: float = 0.3
    common_lower_length: float = 2.5
    common_lower_mass: float = 0.15
    motors: dict[str, MotorGeoData] = field(default_factory=lambda: {
        "A": MotorGeoData(position=[1.0, 0.0, 0.0]),
        "B": MotorGeoData(position=[-0.5, 0.866, 0.0]),
        "C": MotorGeoData(position=[-0.5, -0.866, 0.0]),
    })

    def apply_common_motor_values(self):
        for motor in self.motors.values():
            motor.upper_length = self.common_upper_length
            motor.upper_mass = self.common_upper_mass
            motor.lower_length = self.common_lower_length
            motor.lower_mass = self.common_lower_mass
