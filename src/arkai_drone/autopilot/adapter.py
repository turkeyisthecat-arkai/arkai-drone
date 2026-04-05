from abc import ABC, abstractmethod

from arkai_drone.navigation.planner import TrajectoryCommand


class AutopilotAdapter(ABC):
    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_trajectory(self, command: TrajectoryCommand) -> None:
        raise NotImplementedError
