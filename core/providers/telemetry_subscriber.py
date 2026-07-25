from abc import ABC, abstractmethod

from core.providers.telemetry_events import BaseTelemetryEvent


class BaseTelemetrySubscriber(ABC):
    """
    Interface for objects that wish to consume telemetry events.
    """

    @abstractmethod
    def on_event(self, event: BaseTelemetryEvent) -> None:
        """
        Hook called by the Dispatcher whenever a new event is published.
        """
        pass
