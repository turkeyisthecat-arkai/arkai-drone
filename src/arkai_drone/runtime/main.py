import time

from arkai_drone.autopilot.ardupilot_adapter import ArduPilotAdapter
from arkai_drone.autopilot.px4_adapter import PX4Adapter
from arkai_drone.config.settings import DEFAULT_SETTINGS
from arkai_drone.core.orchestrator import DroneOrchestrator


def build_autopilot():
    if DEFAULT_SETTINGS.autopilot == "px4":
        return PX4Adapter()
    return ArduPilotAdapter()


def run() -> None:
    autopilot = build_autopilot()
    autopilot.connect()
    orchestrator = DroneOrchestrator(DEFAULT_SETTINGS, autopilot)

    for _ in range(5):
        orchestrator.step()
        time.sleep(1.0 / DEFAULT_SETTINGS.control_hz)


if __name__ == "__main__":
    run()
