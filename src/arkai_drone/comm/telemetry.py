from .bus import EventBus
from .messages import Message


class TelemetryPublisher:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus

    def publish_health(self, component: str, ok: bool, detail: str = "") -> None:
        self.bus.publish(
            Message(
                topic="telemetry.health",
                source=component,
                payload={"ok": ok, "detail": detail},
            )
        )
