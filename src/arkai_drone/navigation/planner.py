from dataclasses import dataclass

from arkai_drone.ai.avoidance import AvoidanceDecision
from arkai_drone.sensing.fusion import StateEstimate


@dataclass(slots=True)
class TrajectoryCommand:
    vx: float
    vy: float
    vz: float
    yaw_rate: float


class LocalPlanner:
    def next_command(self, state: StateEstimate, avoidance: AvoidanceDecision) -> TrajectoryCommand:
        base_vx = min(5.0, avoidance.limit_velocity_mps)
        return TrajectoryCommand(vx=base_vx + avoidance.avoid_vector_xyz[0], vy=avoidance.avoid_vector_xyz[1], vz=0.0, yaw_rate=-state.yaw_rad * 0.2)
