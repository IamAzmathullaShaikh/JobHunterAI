import logging
import threading
from typing import List, Set

from core.providers.telemetry_events import BaseTelemetryEvent
from core.providers.telemetry_subscriber import BaseTelemetrySubscriber

logger = logging.getLogger(__name__)


class TelemetryDispatcher:
    """
    Lightweight Pub/Sub hub for telemetry events.
    Thread-safe distribution to multiple subscribers.
    """

    def __init__(self):
        self._subscribers: Set[BaseTelemetrySubscriber] = set()
        self._lock = threading.Lock()

    def subscribe(self, subscriber: BaseTelemetrySubscriber) -> None:
        """Adds a new observer to the event stream."""
        with self._lock:
            self._subscribers.add(subscriber)
            logger.debug(f"Subscriber registered: {subscriber.__class__.__name__}")

    def unsubscribe(self, subscriber: BaseTelemetrySubscriber) -> None:
        """Removes an observer."""
        with self._lock:
            self._subscribers.discard(subscriber)
            logger.debug(f"Subscriber removed: {subscriber.__class__.__name__}")

    def publish(self, event: BaseTelemetryEvent) -> None:
        """Broadcasts an event to all active subscribers."""
        # Snapshot subscribers to minimize lock hold time
        with self._lock:
            current_subscribers = list(self._subscribers)

        for subscriber in current_subscribers:
            try:
                subscriber.on_event(event)
            except Exception as e:
                # We do NOT want a subscriber crash to break the main application flow
                logger.error(
                    f"Telemetry subscriber '{subscriber.__class__.__name__}' crashed: {e}"
                )


# Global singleton dispatcher
dispatcher = TelemetryDispatcher()
