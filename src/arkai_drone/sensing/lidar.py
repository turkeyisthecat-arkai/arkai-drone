from dataclasses import dataclass


@dataclass(slots=True)
class LidarScan:
    points_xyz: list[tuple[float, float, float]]


class LidarSensor:
    def read(self) -> LidarScan:
        return LidarScan(points_xyz=[(2.0, 0.0, 0.3), (4.0, 1.0, 0.2)])
