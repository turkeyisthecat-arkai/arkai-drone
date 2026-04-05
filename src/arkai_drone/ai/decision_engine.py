from dataclasses import dataclass

from arkai_drone.ai.avoidance import AvoidanceDecision
from arkai_drone.navigation.mission_manager import MissionPhase
from arkai_drone.sensing.fusion import StateEstimate


@dataclass(slots=True)
class DecisionOutput:
    mission_phase: MissionPhase
    target_velocity_mps: float
    reason: str


class AIDecisionEngine:
    """High-level autonomous behavior engine for navigation and mission planning."""

    def decide(self, state: StateEstimate, avoidance: AvoidanceDecision) -> DecisionOutput:
        if avoidance.emergency_brake:
            return DecisionOutput(
                mission_phase=MissionPhase.COLLISION_AVOIDANCE,
                target_velocity_mps=0.0,
                reason="hard stop obstacle",
            )

        if state.confidence < 0.5:
            return DecisionOutput(
                mission_phase=MissionPhase.HOLD,
                target_velocity_mps=1.0,
                reason="low confidence sensor fusion",
            )

        if state.alt_m < 8.0:
            return DecisionOutput(
                mission_phase=MissionPhase.TAKEOFF,
                target_velocity_mps=min(2.0, avoidance.limit_velocity_mps),
                reason="climb to mission altitude",
            )

        return DecisionOutput(
            mission_phase=MissionPhase.NAVIGATE,
            target_velocity_mps=avoidance.limit_velocity_mps,
            reason="nominal autonomous navigation",
        )
