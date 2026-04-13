from arkai_drone.config.settings import DroneSettings
from arkai_drone.core.safety import FallbackAction, SafetyWatchdog
from arkai_drone.sensing.fusion import StateEstimate
from arkai_drone.sensing.gps import GPSFix
from arkai_drone.sensing.lidar import LidarScan


def _state() -> StateEstimate:
    return StateEstimate(lat=37.4220, lon=-122.0840, alt_m=10.0, yaw_rad=0.1, obstacle_min_distance_m=4.0)


def test_safety_continue_when_nominal() -> None:
    watchdog = SafetyWatchdog(DroneSettings())
    assessment = watchdog.evaluate(
        sensor_timestamps={"gps": 10.0, "lidar": 10.0, "imu": 10.0, "camera": 10.0},
        gps_fix=GPSFix(lat=37.4220, lon=-122.0840, alt_m=10.0),
        lidar_scan=LidarScan(points_xyz=[(1.0, 0.0, 0.0)]),
        heartbeat_ts=10.0,
        state=_state(),
        home_lat=37.4220,
        home_lon=-122.0840,
        now_monotonic=10.2,
    )
    assert assessment.action == FallbackAction.CONTINUE
    assert assessment.degraded is False


def test_safety_return_home_on_geofence_breach() -> None:
    watchdog = SafetyWatchdog(DroneSettings(geofence_radius_m=5.0, return_to_home_enabled=True))
    far_state = StateEstimate(lat=37.5, lon=-122.0840, alt_m=10.0, yaw_rad=0.1, obstacle_min_distance_m=4.0)
    assessment = watchdog.evaluate(
        sensor_timestamps={"gps": 2.0, "lidar": 2.0, "imu": 2.0, "camera": 2.0},
        gps_fix=GPSFix(lat=37.5, lon=-122.0840, alt_m=10.0),
        lidar_scan=LidarScan(points_xyz=[(1.0, 0.0, 0.0)]),
        heartbeat_ts=2.0,
        state=far_state,
        home_lat=37.4220,
        home_lon=-122.0840,
        now_monotonic=2.1,
    )
    assert assessment.action == FallbackAction.RETURN_TO_HOME


def test_safety_land_on_heartbeat_timeout() -> None:
    watchdog = SafetyWatchdog(DroneSettings())
    assessment = watchdog.evaluate(
        sensor_timestamps={"gps": 1.0, "lidar": 1.0, "imu": 1.0, "camera": 1.0},
        gps_fix=GPSFix(lat=37.4220, lon=-122.0840, alt_m=10.0),
        lidar_scan=LidarScan(points_xyz=[(1.0, 0.0, 0.0)]),
        heartbeat_ts=1.0,
        state=_state(),
        home_lat=37.4220,
        home_lon=-122.0840,
        now_monotonic=10.0,
    )
    assert assessment.action == FallbackAction.LAND
