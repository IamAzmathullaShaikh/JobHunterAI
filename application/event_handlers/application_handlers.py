import logging

from application.event_handlers.base import IEventHandler
from domain.shared.events import ApplicationSubmitted

logger = logging.getLogger(__name__)


class ApplicationSubmittedHandler(IEventHandler):
    async def handle(self, event: ApplicationSubmitted) -> None:
        logger.info(
            f"Recording external application submission for aggregate: {event.aggregate_id}"
        )
        # Could trigger outreach automation or status logging here
