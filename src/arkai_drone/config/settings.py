from dataclasses import dataclass, field
from typing import Literal


@dataclass(slots=True)
class DroneSettings:
    platform: str = "jetson-orin-nano"
    autopilot: Literal["px4", "ardupilot"] = "px4"
    control_hz: int = 30
    perception_hz: int = 15
    obstacle_distance_m: float = 3.0
    max_velocity_mps: float = 8.0
    cameras: list[str] = field(default_factory=lambda: ["front", "left", "right", "down"])


DEFAULT_SETTINGS = DroneSettings()
