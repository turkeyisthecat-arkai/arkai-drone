import json

from arkai_drone.autopilot.adapter import AutopilotAdapter
from arkai_drone.config.settings import DroneSettings
from arkai_drone.core.orchestrator import DroneOrchestrator
from arkai_drone.navigation.planner import TrajectoryCommand


class FakeAutopilot(AutopilotAdapter):
    def __init__(self) -> None:
        self.commands: list[TrajectoryCommand] = []

    def connect(self) -> None:
        return

    def send_trajectory(self, command: TrajectoryCommand) -> None:
        self.commands.append(command)


def test_orchestrator_emits_command_and_snapshots(tmp_path) -> None:
    fake = FakeAutopilot()
    settings = DroneSettings(
        telemetry_snapshot_path=str(tmp_path / "telemetry.json"),
        status_snapshot_path=str(tmp_path / "status.json"),
    )
    orchestrator = DroneOrchestrator(settings, fake)

    snapshot = orchestrator.step()

    assert len(fake.commands) == 1
    assert snapshot.chosen_command["mode"] in {"cruise", "hover", "return_to_home", "land"}
    assert (tmp_path / "telemetry.json").exists()
    assert (tmp_path / "status.json").exists()

    telemetry = json.loads((tmp_path / "telemetry.json").read_text(encoding="utf-8"))
    assert "mission_state" in telemetry
    assert "safety_state" in telemetry
