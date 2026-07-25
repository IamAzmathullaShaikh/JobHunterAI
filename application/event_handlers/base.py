from abc import ABC, abstractmethod

from domain.shared.events import DomainEvent


class IEventHandler(ABC):
    """
    Interface for handling domain events within the application layer.
    """

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        pass
