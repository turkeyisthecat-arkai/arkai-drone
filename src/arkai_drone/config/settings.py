from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Literal


@dataclass(slots=True)
class DroneSettings:
    platform: str = "jetson-orin-nano"
    autopilot: Literal["px4", "ardupilot"] = "px4"
    control_hz: int = 30
    perception_hz: int = 15
    obstacle_distance_m: float = 3.0
    max_velocity_mps: float = 8.0
    cameras: list[str] = field(default_factory=lambda: ["front", "left", "right", "down"])
    geofence_radius_m: float = 200.0
    return_to_home_enabled: bool = True
    simulation_mode: bool = True
    status_snapshot_path: str = "runtime_status.json"
    telemetry_snapshot_path: str = "telemetry_snapshot.json"

    def validate(self) -> None:
        if self.autopilot not in {"px4", "ardupilot"}:
            raise ValueError("autopilot must be 'px4' or 'ardupilot'")
        if self.control_hz <= 0 or self.perception_hz <= 0:
            raise ValueError("control_hz and perception_hz must be positive")
        if self.obstacle_distance_m <= 0:
            raise ValueError("obstacle_distance_m must be positive")
        if self.max_velocity_mps <= 0:
            raise ValueError("max_velocity_mps must be positive")
        if self.geofence_radius_m <= 0:
            raise ValueError("geofence_radius_m must be positive")
        if not self.cameras:
            raise ValueError("at least one camera must be configured")

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "DroneSettings":
        data = payload.get("drone", payload)
        defaults = cls()
        settings = cls(
            platform=str(data.get("platform", defaults.platform)),
            autopilot=data.get("autopilot", defaults.autopilot),
            control_hz=int(data.get("control_hz", defaults.control_hz)),
            perception_hz=int(data.get("perception_hz", defaults.perception_hz)),
            obstacle_distance_m=float(data.get("obstacle_distance_m", defaults.obstacle_distance_m)),
            max_velocity_mps=float(data.get("max_velocity_mps", defaults.max_velocity_mps)),
            cameras=list(data.get("cameras", defaults.cameras)),
            geofence_radius_m=float(data.get("geofence_radius_m", defaults.geofence_radius_m)),
            return_to_home_enabled=bool(data.get("return_to_home_enabled", defaults.return_to_home_enabled)),
            simulation_mode=bool(data.get("simulation_mode", defaults.simulation_mode)),
            status_snapshot_path=str(data.get("status_snapshot_path", defaults.status_snapshot_path)),
            telemetry_snapshot_path=str(data.get("telemetry_snapshot_path", defaults.telemetry_snapshot_path)),
        )
        settings.validate()
        return settings


def _parse_toml_flat(text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or "=" not in line or line.startswith("["):
            continue
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        if raw_value.startswith("[") and raw_value.endswith("]"):
            inner = raw_value[1:-1].strip()
            parsed[key] = [] if not inner else [item.strip().strip('"\'') for item in inner.split(",")]
        elif raw_value.lower() in {"true", "false"}:
            parsed[key] = raw_value.lower() == "true"
        elif raw_value.startswith('"') and raw_value.endswith('"'):
            parsed[key] = raw_value[1:-1]
        elif raw_value.startswith("'") and raw_value.endswith("'"):
            parsed[key] = raw_value[1:-1]
        else:
            parsed[key] = float(raw_value) if "." in raw_value else int(raw_value)
    return parsed


def load_settings(config_path: str | Path | None = None) -> DroneSettings:
    if config_path is None:
        settings = DroneSettings()
        settings.validate()
        return settings

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file does not exist: {path}")

    suffix = path.suffix.lower()
    raw: dict[str, Any]
    if suffix == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
    elif suffix in {".toml", ".tml"}:
        raw = _parse_toml_flat(path.read_text(encoding="utf-8"))
    else:
        raise ValueError("Unsupported config type. Use JSON or TOML.")

    return DroneSettings.from_mapping(raw)


DEFAULT_SETTINGS = DroneSettings()
