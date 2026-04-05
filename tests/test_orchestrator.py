from arkai_drone.autopilot.adapter import AutopilotAdapter, TelemetryPacket
from arkai_drone.config.settings import DroneSettings
from arkai_drone.core.orchestrator import DroneOrchestrator
from arkai_drone.navigation.planner import TrajectoryCommand


class FakeAutopilot(AutopilotAdapter):
    def __init__(self) -> None:
        self.commands: list[TrajectoryCommand] = []
        self.modes: list[str] = []

    def connect(self) -> None:
        return

    def send_trajectory(self, command: TrajectoryCommand) -> None:
        self.commands.append(command)

    def set_mode(self, mode: str) -> None:
        self.modes.append(mode)

    def read_telemetry(self) -> TelemetryPacket:
        return TelemetryPacket(armed=True, flight_mode="MISSION", battery_pct=92.0, gps_fix_ok=True)


def test_orchestrator_emits_command() -> None:
    fake = FakeAutopilot()
    orchestrator = DroneOrchestrator(DroneSettings(), fake)
    orchestrator.step()
    assert len(fake.commands) == 1
    assert len(fake.modes) >= 1
