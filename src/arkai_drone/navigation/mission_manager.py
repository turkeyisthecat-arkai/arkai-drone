from dataclasses import dataclass
from enum import Enum


class MissionPhase(str, Enum):
    TAKEOFF = "takeoff"
    NAVIGATE = "navigate"
    COLLISION_AVOIDANCE = "collision_avoidance"
    HOLD = "hold"


@dataclass(slots=True)
class Waypoint:
    lat: float
    lon: float
    alt_m: float


class MissionManager:
    def __init__(self, waypoints: list[Waypoint]) -> None:
        self.waypoints = waypoints
        self.current_index = 0

    def current_goal(self) -> Waypoint | None:
        if self.current_index >= len(self.waypoints):
            return None
        return self.waypoints[self.current_index]
