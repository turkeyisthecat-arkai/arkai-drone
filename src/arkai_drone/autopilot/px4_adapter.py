import logging

from arkai_drone.autopilot.adapter import AutopilotAdapter
from arkai_drone.navigation.planner import TrajectoryCommand


logger = logging.getLogger(__name__)


class PX4Adapter(AutopilotAdapter):
    def connect(self) -> None:
        logger.info("autopilot_connect", extra={"autopilot": "px4"})

    def send_trajectory(self, command: TrajectoryCommand) -> None:
        logger.info(
            "autopilot_command",
            extra={
                "autopilot": "px4",
                "mode": command.mode,
                "vx": command.vx,
                "vy": command.vy,
                "vz": command.vz,
                "yaw_rate": command.yaw_rate,
            },
        )
