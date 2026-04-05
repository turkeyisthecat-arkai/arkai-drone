from arkai_drone.config.settings import DroneSettings
from arkai_drone.core.orchestrator import DroneOrchestrator
from arkai_drone.navigation.planner import TrajectoryCommand
from arkai_drone.autopilot.adapter import AutopilotAdapter


class FakeAutopilot(AutopilotAdapter):
    def __init__(self) -> None:
        self.commands: list[TrajectoryCommand] = []

    def connect(self) -> None:
        return

    def send_trajectory(self, command: TrajectoryCommand) -> None:
        self.commands.append(command)


def test_orchestrator_emits_command() -> None:
    fake = FakeAutopilot()
    orchestrator = DroneOrchestrator(DroneSettings(), fake)
    orchestrator.step()
    assert len(fake.commands) == 1
