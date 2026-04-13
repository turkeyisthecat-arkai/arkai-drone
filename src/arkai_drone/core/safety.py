from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
import time

from arkai_drone.config.settings import DroneSettings
from arkai_drone.sensing.fusion import StateEstimate
from arkai_drone.sensing.gps import GPSFix
from arkai_drone.sensing.lidar import LidarScan


class FallbackAction(str, Enum):
    CONTINUE = "continue"
    HOVER = "hover"
    RETURN_TO_HOME = "return_to_home"
    LAND = "land"


@dataclass(slots=True)
class SafetyAssessment:
    action: FallbackAction
    degraded: bool
    reasons: list[str] = field(default_factory=list)


class SafetyWatchdog:
    def __init__(self, settings: DroneSettings, stale_sensor_sec: float = 1.5, heartbeat_timeout_sec: float = 2.5) -> None:
        self.settings = settings
        self.stale_sensor_sec = stale_sensor_sec
        self.heartbeat_timeout_sec = heartbeat_timeout_sec

    def evaluate(
        self,
        *,
        sensor_timestamps: dict[str, float],
        gps_fix: GPSFix | None,
        lidar_scan: LidarScan | None,
        heartbeat_ts: float | None,
        state: StateEstimate,
        home_lat: float,
        home_lon: float,
        now_monotonic: float | None = None,
    ) -> SafetyAssessment:
        now_ts = now_monotonic if now_monotonic is not None else time.monotonic()
        reasons: list[str] = []

        stale = [name for name, ts in sensor_timestamps.items() if now_ts - ts > self.stale_sensor_sec]
        if stale:
            reasons.append(f"stale_sensor_data:{','.join(sorted(stale))}")

        if gps_fix is None or not (-90.0 <= gps_fix.lat <= 90.0 and -180.0 <= gps_fix.lon <= 180.0):
            reasons.append("invalid_gps")

        if lidar_scan is None or not lidar_scan.points_xyz:
            reasons.append("lidar_missing")

        if heartbeat_ts is None or now_ts - heartbeat_ts > self.heartbeat_timeout_sec:
            reasons.append("heartbeat_timeout")

        distance_from_home_m = _haversine_m(home_lat, home_lon, state.lat, state.lon)
        if distance_from_home_m > self.settings.geofence_radius_m:
            reasons.append("geofence_breach")

        if not reasons:
            return SafetyAssessment(action=FallbackAction.CONTINUE, degraded=False)

        if "heartbeat_timeout" in reasons:
            return SafetyAssessment(action=FallbackAction.LAND, degraded=True, reasons=reasons)

        if "geofence_breach" in reasons and self.settings.return_to_home_enabled:
            return SafetyAssessment(action=FallbackAction.RETURN_TO_HOME, degraded=True, reasons=reasons)

        if "invalid_gps" in reasons and self.settings.return_to_home_enabled:
            return SafetyAssessment(action=FallbackAction.HOVER, degraded=True, reasons=reasons)

        if "lidar_missing" in reasons or stale:
            return SafetyAssessment(action=FallbackAction.HOVER, degraded=True, reasons=reasons)

        return SafetyAssessment(action=FallbackAction.CONTINUE, degraded=True, reasons=reasons)


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))
