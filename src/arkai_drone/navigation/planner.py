from __future__ import annotations

from dataclasses import dataclass

from arkai_drone.ai.avoidance import AvoidanceDecision
from arkai_drone.core.safety import FallbackAction
from arkai_drone.navigation.mission_manager import MissionType
from arkai_drone.sensing.fusion import StateEstimate


@dataclass(slots=True)
class TrajectoryCommand:
    vx: float
    vy: float
    vz: float
    yaw_rate: float
    mode: str = "cruise"


class LocalPlanner:
    def next_command(
        self,
        state: StateEstimate,
        avoidance: AvoidanceDecision,
        mission_type: MissionType = MissionType.IDLE,
        fallback_action: FallbackAction = FallbackAction.CONTINUE,
    ) -> TrajectoryCommand:
        if fallback_action == FallbackAction.HOVER:
            return TrajectoryCommand(vx=0.0, vy=0.0, vz=0.0, yaw_rate=0.0, mode="hover")
        if fallback_action == FallbackAction.RETURN_TO_HOME:
            return TrajectoryCommand(vx=-1.0, vy=0.0, vz=0.0, yaw_rate=0.0, mode="return_to_home")
        if fallback_action == FallbackAction.LAND:
            return TrajectoryCommand(vx=0.0, vy=0.0, vz=-0.5, yaw_rate=0.0, mode="land")

        mission_speed_factor = 0.6 if mission_type == MissionType.OBSERVE_TARGET_AREA else 1.0
        base_vx = min(5.0, avoidance.limit_velocity_mps) * mission_speed_factor
        return TrajectoryCommand(
            vx=base_vx + avoidance.avoid_vector_xyz[0],
            vy=avoidance.avoid_vector_xyz[1],
            vz=0.0,
            yaw_rate=-state.yaw_rad * 0.2,
            mode="cruise",
        )
