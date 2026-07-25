from application.dto.input.interview_input import ScheduleInterviewInputDTO
from domain.tracking.entities import Interview


class InterviewMapper:
    """Maps between Interview domain entities and DTOs."""

    @staticmethod
    def to_output_dto(interview: Interview) -> dict:
        # Assuming we might need an InterviewOutputDTO later
        return {
            "id": str(interview.id),
            "application_id": str(interview.application_id),
            "scheduled_at": str(interview.scheduled_at),
            "status": interview.status.value,
            "location": interview.location,
        }
