from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ScheduleInterviewInputDTO:
    application_id: str
    scheduled_at: datetime
    location: Optional[str] = None
