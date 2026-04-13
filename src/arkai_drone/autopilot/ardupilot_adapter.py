import logging

from arkai_drone.autopilot.adapter import AutopilotAdapter
from arkai_drone.navigation.planner import TrajectoryCommand


logger = logging.getLogger(__name__)


class ArduPilotAdapter(AutopilotAdapter):
    def connect(self) -> None:
        logger.info("autopilot_connect", extra={"autopilot": "ardupilot"})

    def send_trajectory(self, command: TrajectoryCommand) -> None:
        logger.info(
            "autopilot_command",
            extra={
                "autopilot": "ardupilot",
                "mode": command.mode,
                "vx": command.vx,
                "vy": command.vy,
                "vz": command.vz,
                "yaw_rate": command.yaw_rate,
            },
        )
