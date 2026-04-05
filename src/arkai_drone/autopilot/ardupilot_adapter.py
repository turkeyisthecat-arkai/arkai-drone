from arkai_drone.autopilot.adapter import AutopilotAdapter, TelemetryPacket
from arkai_drone.navigation.planner import TrajectoryCommand


class ArduPilotAdapter(AutopilotAdapter):
    def __init__(self) -> None:
        self.mode = "GUIDED"

    def connect(self) -> None:
        print("ArduPilot adapter connected")

    def send_trajectory(self, command: TrajectoryCommand) -> None:
        print(f"ArduPilot command: vx={command.vx:.2f} vy={command.vy:.2f} vz={command.vz:.2f}")

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        print(f"ArduPilot mode -> {mode}")

    def read_telemetry(self) -> TelemetryPacket:
        return TelemetryPacket(armed=True, flight_mode=self.mode, battery_pct=79.4, gps_fix_ok=True)
