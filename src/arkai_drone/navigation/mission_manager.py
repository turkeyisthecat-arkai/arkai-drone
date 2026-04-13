from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MissionType(str, Enum):
    IDLE = "idle"
    WAYPOINT_PATROL = "waypoint_patrol"
    OBSERVE_TARGET_AREA = "observe_target_area"
    RETURN_HOME = "return_home"


class MissionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class Waypoint:
    lat: float
    lon: float
    alt_m: float


@dataclass(slots=True)
class Mission:
    mission_type: MissionType
    status: MissionStatus = MissionStatus.PENDING
    waypoints: list[Waypoint] = field(default_factory=list)


class MissionManager:
    def __init__(self, waypoints: list[Waypoint] | None = None) -> None:
        self.current_index = 0
        self.mission = Mission(mission_type=MissionType.IDLE, status=MissionStatus.ACTIVE)
        if waypoints:
            self.set_mission(MissionType.WAYPOINT_PATROL, waypoints)

    def set_mission(self, mission_type: MissionType, waypoints: list[Waypoint] | None = None) -> None:
        self.current_index = 0
        self.mission = Mission(
            mission_type=mission_type,
            status=MissionStatus.ACTIVE,
            waypoints=waypoints or [],
        )

    def current_goal(self) -> Waypoint | None:
        if self.mission.mission_type != MissionType.WAYPOINT_PATROL:
            return None
        if self.current_index >= len(self.mission.waypoints):
            return None
        return self.mission.waypoints[self.current_index]

    def advance_if_reached(self, distance_to_goal_m: float, threshold_m: float = 1.5) -> None:
        if self.mission.mission_type != MissionType.WAYPOINT_PATROL:
            return

        goal = self.current_goal()
        if goal is None:
            self.mission.status = MissionStatus.COMPLETED
            return

        if distance_to_goal_m <= threshold_m:
            self.current_index += 1
            if self.current_index >= len(self.mission.waypoints):
                self.mission.status = MissionStatus.COMPLETED

    def mark_target_observed(self) -> None:
        if self.mission.mission_type == MissionType.OBSERVE_TARGET_AREA:
            self.mission.status = MissionStatus.COMPLETED

    def trigger_return_home(self) -> None:
        self.set_mission(MissionType.RETURN_HOME)

    def status_snapshot(self) -> dict[str, str | int]:
        return {
            "mission_type": self.mission.mission_type.value,
            "mission_status": self.mission.status.value,
            "current_index": self.current_index,
        }
