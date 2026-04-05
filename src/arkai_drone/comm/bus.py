from collections import defaultdict
from typing import Callable

from .messages import Message

Subscriber = Callable[[Message], None]


class EventBus:
    """Simple in-process pub/sub used by starter runtime and simulation."""

    def __init__(self) -> None:
        self._subs: dict[str, list[Subscriber]] = defaultdict(list)

    def subscribe(self, topic: str, callback: Subscriber) -> None:
        self._subs[topic].append(callback)

    def publish(self, msg: Message) -> None:
        for callback in self._subs[msg.topic]:
            callback(msg)
