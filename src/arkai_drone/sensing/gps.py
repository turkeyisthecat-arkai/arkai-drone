from dataclasses import dataclass


@dataclass(slots=True)
class GPSFix:
    lat: float
    lon: float
    alt_m: float


class GPSSensor:
    def read(self) -> GPSFix:
        return GPSFix(lat=37.4219999, lon=-122.0840575, alt_m=10.5)
