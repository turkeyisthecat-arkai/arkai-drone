from arkai_drone.autopilot.adapter import AutopilotAdapter, TelemetryPacket
from arkai_drone.navigation.planner import TrajectoryCommand


class PX4Adapter(AutopilotAdapter):
    def __init__(self) -> None:
        self.mode = "MISSION"

    def connect(self) -> None:
        print("PX4 adapter connected")

    def send_trajectory(self, command: TrajectoryCommand) -> None:
        print(f"PX4 command: vx={command.vx:.2f} vy={command.vy:.2f} vz={command.vz:.2f}")

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        print(f"PX4 mode -> {mode}")

    def read_telemetry(self) -> TelemetryPacket:
        return TelemetryPacket(armed=True, flight_mode=self.mode, battery_pct=84.2, gps_fix_ok=True)
