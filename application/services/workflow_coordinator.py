import logging

from application.dto.input.interview_input import ScheduleInterviewInputDTO
from application.dto.input.offer_input import CreateOfferInputDTO
from application.results.result import Result
from application.use_cases.application.create_offer import CreateOfferUseCase
from application.use_cases.application.submit_application import \
    SubmitApplicationUseCase
from application.use_cases.interview.schedule_interview import \
    ScheduleInterviewUseCase

logger = logging.getLogger(__name__)


class WorkflowCoordinator:
    """
    Coordinates complex cross-context transitions in the application workflow.
    """

    def __init__(
        self,
        submit_uc: SubmitApplicationUseCase,
        schedule_uc: ScheduleInterviewUseCase,
        offer_uc: CreateOfferUseCase,
    ):
        self._submit_uc = submit_uc
        self._schedule_uc = schedule_uc
        self._offer_uc = offer_uc

    async def advance_to_interview(self, dto: ScheduleInterviewInputDTO) -> Result[str]:
        return await self._schedule_uc.execute(dto)

    async def finalize_with_offer(self, dto: CreateOfferInputDTO) -> Result[str]:
        return await self._offer_uc.execute(dto)
