from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CreateOfferInputDTO:
    application_id: str
    salary_amount: float
    currency: str = "USD"
    benefits: str = ""
    expires_at: Optional[datetime] = None
