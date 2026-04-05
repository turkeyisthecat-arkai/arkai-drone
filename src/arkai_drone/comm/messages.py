from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


@dataclass(slots=True)
class Message:
    topic: str
    source: str
    payload: dict[str, Any]
    timestamp: float = field(default_factory=now_ts)
