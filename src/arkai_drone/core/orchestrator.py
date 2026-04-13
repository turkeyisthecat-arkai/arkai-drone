from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import time

from arkai_drone.ai.avoidance import ObstacleAvoider
from arkai_drone.ai.perception import LocalPerceptionEngine
from arkai_drone.autopilot.adapter import AutopilotAdapter
from arkai_drone.config.settings import DroneSettings
from arkai_drone.core.safety import FallbackAction, SafetyWatchdog
from arkai_drone.navigation.mission_manager import MissionManager, MissionType, Waypoint
from arkai_drone.navigation.planner import LocalPlanner
from arkai_drone.sensing.camera_manager import MultiCameraSystem
from arkai_drone.sensing.fusion import SensorFusion
from arkai_drone.sensing.gps import GPSSensor
from arkai_drone.sensing.imu import IMUSensor
from arkai_drone.sensing.lidar import LidarSensor

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RuntimeCycleSnapshot:
    timestamp: str
    current_mode: str
    mission_state: str
    gps: dict[str, float]
    yaw: float
    min_obstacle_distance_m: float
    chosen_command: dict[str, float | str]
    safety_state: dict[str, object]


class DroneOrchestrator:
    def __init__(self, settings: DroneSettings, autopilot: AutopilotAdapter) -> None:
        self.settings = settings
        self.autopilot = autopilot
        self.cameras = MultiCameraSystem(settings.cameras)
        self.lidar = LidarSensor()
        self.gps = GPSSensor()
        self.imu = IMUSensor()
        self.fusion = SensorFusion()
        self.perception = LocalPerceptionEngine()
        self.avoider = ObstacleAvoider(settings.obstacle_distance_m)
        self.planner = LocalPlanner()
        self.safety = SafetyWatchdog(settings)
        self.missions = MissionManager(
            waypoints=[
                Waypoint(lat=37.4221, lon=-122.0841, alt_m=12.0),
                Waypoint(lat=37.4222, lon=-122.0842, alt_m=12.0),
            ]
        )
        self.home_lat = 37.4219999
        self.home_lon = -122.0840575
        self.heartbeat_ts = time.monotonic()
        self.last_sensor_timestamps: dict[str, float] = {}
        self.last_cycle: RuntimeCycleSnapshot | None = None

    def step(self) -> RuntimeCycleSnapshot:
        cycle_ts = datetime.now(timezone.utc).isoformat()
        now_mono = time.monotonic()

        frames = self.cameras.capture()
        self.last_sensor_timestamps["camera"] = now_mono
        lidar_scan = self.lidar.read()
        self.last_sensor_timestamps["lidar"] = now_mono
        gps_fix = self.gps.read()
        self.last_sensor_timestamps["gps"] = now_mono
        imu_sample = self.imu.read()
        self.last_sensor_timestamps["imu"] = now_mono
        logger.info("sensor_reads", extra={"frames": len(frames), "lidar_points": len(lidar_scan.points_xyz)})

        state = self.fusion.fuse(gps_fix, imu_sample, lidar_scan)
        logger.info("fusion_state", extra={"lat": state.lat, "lon": state.lon, "yaw": state.yaw_rad})

        perception = self.perception.infer(frames)
        logger.info("perception_result", extra={"obstacles": len(perception.obstacles), "free_space": perception.free_space_score})

        safety = self.safety.evaluate(
            sensor_timestamps=self.last_sensor_timestamps,
            gps_fix=gps_fix,
            lidar_scan=lidar_scan,
            heartbeat_ts=self.heartbeat_ts,
            state=state,
            home_lat=self.home_lat,
            home_lon=self.home_lon,
            now_monotonic=now_mono,
        )
        logger.info(
            "safety_assessment",
            extra={"action": safety.action.value, "degraded": safety.degraded, "reasons": ",".join(safety.reasons)},
        )

        if safety.action == FallbackAction.RETURN_TO_HOME:
            self.missions.trigger_return_home()

        avoidance = self.avoider.decide(
            obstacle_distance_m=state.obstacle_min_distance_m,
            nominal_speed_mps=self.settings.max_velocity_mps,
        )
        logger.info(
            "avoidance_decision",
            extra={"limit_velocity_mps": avoidance.limit_velocity_mps, "vector": avoidance.avoid_vector_xyz},
        )

        command = self.planner.next_command(
            state,
            avoidance,
            mission_type=self.missions.mission.mission_type,
            fallback_action=safety.action,
        )
        logger.info("planner_output", extra={"mode": command.mode, "vx": command.vx, "vy": command.vy, "vz": command.vz})

        self.autopilot.send_trajectory(command)
        self.heartbeat_ts = time.monotonic()

        snapshot = RuntimeCycleSnapshot(
            timestamp=cycle_ts,
            current_mode="degraded" if safety.degraded else "nominal",
            mission_state=self.missions.mission.mission_type.value,
            gps={"lat": state.lat, "lon": state.lon, "alt_m": state.alt_m},
            yaw=state.yaw_rad,
            min_obstacle_distance_m=state.obstacle_min_distance_m,
            chosen_command=asdict(command),
            safety_state={"action": safety.action.value, "reasons": safety.reasons, "degraded": safety.degraded},
        )
        self.last_cycle = snapshot
        self._write_json_file(Path(self.settings.telemetry_snapshot_path), asdict(snapshot))
        self._write_json_file(
            Path(self.settings.status_snapshot_path),
            {
                "timestamp": snapshot.timestamp,
                "mode": snapshot.current_mode,
                "mission": self.missions.status_snapshot(),
                "safety": snapshot.safety_state,
            },
        )
        return snapshot

    @staticmethod
    def _write_json_file(path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(path)
