from application.dto.output.workflow_output import (ApplicationWorkflowDTO,
                                                    InterviewDTO, OfferDTO,
                                                    WorkflowHistoryDTO)
from domain.tracking.application import Application, WorkflowHistory
from domain.tracking.entities import Interview
from domain.tracking.offer import Offer


class WorkflowMapper:
    @staticmethod
    def to_history_dto(history: WorkflowHistory) -> WorkflowHistoryDTO:
        return WorkflowHistoryDTO(
            timestamp=history.timestamp.isoformat(),
            previous_state=history.previous_state.value,
            new_state=history.new_state.value,
            actor=history.actor,
            reason=history.reason,
        )

    @staticmethod
    def to_interview_dto(interview: Interview) -> InterviewDTO:
        return InterviewDTO(
            id=str(interview.id),
            scheduled_at=interview.scheduled_at.isoformat(),
            status=interview.status.value,
            location=interview.location,
        )

    @staticmethod
    def to_offer_dto(offer: Offer) -> OfferDTO:
        return OfferDTO(
            id=str(offer.id),
            salary=offer.salary.amount,
            currency=offer.salary.currency,
            status=offer.status,
            expires_at=offer.expires_at.isoformat() if offer.expires_at else None,
        )

    @staticmethod
    def to_workflow_dto(app: Application) -> ApplicationWorkflowDTO:
        return ApplicationWorkflowDTO(
            id=str(app.id),
            status=app.status.value,
            days_in_stage=app.days_in_current_stage,
            history=[WorkflowMapper.to_history_dto(h) for h in app.history],
            interviews=[WorkflowMapper.to_interview_dto(i) for i in app.interviews],
            offer=WorkflowMapper.to_offer_dto(app._offer) if app._offer else None,
        )
