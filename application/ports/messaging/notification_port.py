from abc import ABC, abstractmethod
from typing import Any, Dict


class INotificationPort(ABC):
    """
    Port for sending external notifications.
    """

    @abstractmethod
    async def send_notification(
        self, recipient_id: str, template_name: str, context: Dict[str, Any]
    ) -> bool:
        pass
