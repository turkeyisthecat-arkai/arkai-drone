from dataclasses import dataclass

from .gps import GPSFix
from .imu import IMUSample
from .lidar import LidarScan


@dataclass(slots=True)
class StateEstimate:
    lat: float
    lon: float
    alt_m: float
    yaw_rad: float
    obstacle_min_distance_m: float


class SensorFusion:
    def fuse(self, gps: GPSFix, imu: IMUSample, lidar: LidarScan) -> StateEstimate:
        min_dist = min((p[0] ** 2 + p[1] ** 2 + p[2] ** 2) ** 0.5 for p in lidar.points_xyz)
        return StateEstimate(
            lat=gps.lat,
            lon=gps.lon,
            alt_m=gps.alt_m,
            yaw_rad=imu.gyro_rads[2],
            obstacle_min_distance_m=min_dist,
        )
