from dataclasses import dataclass


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
