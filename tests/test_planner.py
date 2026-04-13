from arkai_drone.ai.avoidance import AvoidanceDecision
from arkai_drone.core.safety import FallbackAction
from arkai_drone.navigation.mission_manager import MissionType
from arkai_drone.navigation.planner import LocalPlanner
from arkai_drone.sensing.fusion import StateEstimate


def _state() -> StateEstimate:
    return StateEstimate(lat=37.0, lon=-122.0, alt_m=10.0, yaw_rad=0.2, obstacle_min_distance_m=4.0)


def test_planner_generates_cruise_command() -> None:
    planner = LocalPlanner()
    command = planner.next_command(
        _state(),
        AvoidanceDecision(limit_velocity_mps=3.0, avoid_vector_xyz=(0.1, -0.1, 0.0)),
        mission_type=MissionType.WAYPOINT_PATROL,
        fallback_action=FallbackAction.CONTINUE,
    )
    assert command.mode == "cruise"
    assert command.vx > 0


def test_planner_hover_fallback() -> None:
    planner = LocalPlanner()
    command = planner.next_command(
        _state(),
        AvoidanceDecision(limit_velocity_mps=3.0, avoid_vector_xyz=(0.1, -0.1, 0.0)),
        fallback_action=FallbackAction.HOVER,
    )
    assert command.mode == "hover"
    assert command.vx == 0.0 and command.vz == 0.0
