from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import logging
import time
from typing import Any

from arkai_drone.autopilot.ardupilot_adapter import ArduPilotAdapter
from arkai_drone.autopilot.px4_adapter import PX4Adapter
from arkai_drone.config.settings import DroneSettings, load_settings
from arkai_drone.core.orchestrator import DroneOrchestrator


class JsonLogFormatter(logging.Formatter):
    _reserved = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
        "asctime",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in self._reserved:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def _configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)


def build_autopilot(settings: DroneSettings):
    if settings.autopilot == "px4":
        return PX4Adapter()
    return ArduPilotAdapter()


def run(config_path: str | None = None, cycles: int = 5) -> None:
    _configure_logging()
    logger = logging.getLogger(__name__)
    settings = load_settings(config_path)
    logger.info("startup", extra={"settings": asdict(settings)})

    autopilot = build_autopilot(settings)
    autopilot.connect()
    orchestrator = DroneOrchestrator(settings, autopilot)

    for _ in range(cycles):
        try:
            snapshot = orchestrator.step()
            logger.info("cycle_complete", extra={"mode": snapshot.current_mode, "mission": snapshot.mission_state})
        except Exception:
            logger.exception("runtime_cycle_failed")
        time.sleep(1.0 / settings.control_hz)


def main() -> None:
    parser = argparse.ArgumentParser(description="ARKAI drone simulation runtime")
    parser.add_argument("--config", type=str, default=None, help="Path to JSON/TOML settings file")
    parser.add_argument("--cycles", type=int, default=5, help="Number of runtime cycles")
    args = parser.parse_args()
    run(config_path=args.config, cycles=args.cycles)


if __name__ == "__main__":
    main()
