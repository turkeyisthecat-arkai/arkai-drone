from arkai_drone.autopilot.adapter import AutopilotAdapter
from arkai_drone.navigation.planner import TrajectoryCommand


class ArduPilotAdapter(AutopilotAdapter):
    def connect(self) -> None:
        print("ArduPilot adapter connected")

    def send_trajectory(self, command: TrajectoryCommand) -> None:
        print(f"ArduPilot command: vx={command.vx:.2f} vy={command.vy:.2f} vz={command.vz:.2f}")
