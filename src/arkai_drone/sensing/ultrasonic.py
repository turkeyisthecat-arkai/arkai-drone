from dataclasses import dataclass


@dataclass(slots=True)
class UltrasonicReading:
    distance_m: float


class UltrasonicSensor:
    """Short-range redundancy sensor for close obstacle detection."""

    def read(self) -> UltrasonicReading:
        return UltrasonicReading(distance_m=1.8)
