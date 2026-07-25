import logging

from application.event_handlers.base import IEventHandler
from domain.shared.events import ResumeCreated

logger = logging.getLogger(__name__)


class ResumeCreatedHandler(IEventHandler):
    async def handle(self, event: ResumeCreated) -> None:
        logger.info(
            f"Triggering automated analysis for new resume: {event.aggregate_id}"
        )
        # In a real app, this might queue an AnalyzeResumeUseCase
