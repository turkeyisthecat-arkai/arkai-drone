from abc import ABC, abstractmethod
from dataclasses import dataclass

from arkai_drone.navigation.planner import TrajectoryCommand


@dataclass(slots=True)
class TelemetryPacket:
    armed: bool
    flight_mode: str
    battery_pct: float
    gps_fix_ok: bool


class AutopilotAdapter(ABC):
    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_trajectory(self, command: TrajectoryCommand) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_mode(self, mode: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_telemetry(self) -> TelemetryPacket:
        raise NotImplementedError
