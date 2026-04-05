from dataclasses import dataclass

from arkai_drone.ai.perception import PerceptionOutput

from .gps import GPSFix
from .imu import IMUSample
from .lidar import LidarScan
from .ultrasonic import UltrasonicReading


@dataclass(slots=True)
class StateEstimate:
    lat: float
    lon: float
    alt_m: float
    yaw_rad: float
    obstacle_min_distance_m: float
    confidence: float


class SensorFusion:
    """Fuses GPS + IMU + LiDAR + ultrasonic + camera perception into a single state."""

    def fuse(
        self,
        gps: GPSFix,
        imu: IMUSample,
        lidar: LidarScan,
        ultrasonic: UltrasonicReading,
        perception: PerceptionOutput,
    ) -> StateEstimate:
        lidar_min = min((p[0] ** 2 + p[1] ** 2 + p[2] ** 2) ** 0.5 for p in lidar.points_xyz)
        camera_min = min((p[0] ** 2 + p[1] ** 2 + p[2] ** 2) ** 0.5 for p in perception.obstacles) if perception.obstacles else float("inf")
        fused_min = min(lidar_min, ultrasonic.distance_m, camera_min)

        confidence = 0.35
        if perception.obstacles:
            confidence += 0.25
        if ultrasonic.distance_m < 4.0:
            confidence += 0.2
        if lidar.points_xyz:
            confidence += 0.2

        return StateEstimate(
            lat=gps.lat,
            lon=gps.lon,
            alt_m=gps.alt_m,
            yaw_rad=imu.gyro_rads[2],
            obstacle_min_distance_m=fused_min,
            confidence=min(1.0, confidence),
        )
