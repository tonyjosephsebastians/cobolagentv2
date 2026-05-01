"""Observer hooks for workflow progress."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class AgentEvent:
    """A progress event emitted by commands and workflows."""

    name: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)


class EventObserver(Protocol):
    """Callable event observer protocol."""

    def __call__(self, event: AgentEvent) -> None:
        """Handle an emitted event."""


class EventBus:
    """Small observer implementation used by SDK and CLI."""

    def __init__(self, observers: list[EventObserver] | None = None) -> None:
        self._observers = observers or []

    def subscribe(self, observer: EventObserver) -> None:
        self._observers.append(observer)

    def emit(self, name: str, message: str, **data: Any) -> None:
        event = AgentEvent(name=name, message=message, data=data)
        for observer in self._observers:
            observer(event)
