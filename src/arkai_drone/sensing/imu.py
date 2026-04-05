from dataclasses import dataclass


@dataclass(slots=True)
class IMUSample:
    accel_mps2: tuple[float, float, float]
    gyro_rads: tuple[float, float, float]


class IMUSensor:
    def read(self) -> IMUSample:
        return IMUSample(accel_mps2=(0.0, 0.0, 9.8), gyro_rads=(0.0, 0.0, 0.02))
