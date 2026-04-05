from dataclasses import dataclass
from arkai_drone.ai.avoidance import AvoidanceDecision
from arkai_drone.ai.decision_engine import DecisionOutput
from arkai_drone.navigation.mission_manager import MissionPhase
from arkai_drone.sensing.fusion import StateEstimate


@dataclass(slots=True)
class TrajectoryCommand:
    vx: float
    vy: float
    vz: float
    yaw_rate: float


class LocalPlanner:
    def next_command(
        self,
        state: StateEstimate,
        avoidance: AvoidanceDecision,
        decision: DecisionOutput,
    ) -> TrajectoryCommand:
        base_vx = min(5.0, decision.target_velocity_mps)
        if decision.mission_phase == MissionPhase.TAKEOFF:
            return TrajectoryCommand(vx=0.0, vy=0.0, vz=1.2, yaw_rate=-state.yaw_rad * 0.1)

        return TrajectoryCommand(
            vx=base_vx + avoidance.avoid_vector_xyz[0],
            vy=avoidance.avoid_vector_xyz[1],
            vz=avoidance.avoid_vector_xyz[2],
            yaw_rate=-state.yaw_rad * 0.2,
        )
