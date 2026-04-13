from arkai_drone.navigation.mission_manager import MissionManager, MissionStatus, MissionType, Waypoint


def test_waypoint_patrol_transitions_to_completed() -> None:
    manager = MissionManager([Waypoint(lat=1.0, lon=2.0, alt_m=3.0)])
    assert manager.mission.mission_type == MissionType.WAYPOINT_PATROL
    manager.advance_if_reached(distance_to_goal_m=0.5)
    assert manager.mission.status == MissionStatus.COMPLETED


def test_return_home_transition() -> None:
    manager = MissionManager()
    manager.trigger_return_home()
    assert manager.mission.mission_type == MissionType.RETURN_HOME
    assert manager.mission.status == MissionStatus.ACTIVE
