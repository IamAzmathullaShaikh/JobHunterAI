from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from domain.shared.value_objects import DomainId, Money


@dataclass(frozen=True)
class OfferId(DomainId):
    pass


@dataclass
class Offer:
    id: OfferId
    application_id: str
    salary: Money
    benefits: str
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    _is_accepted: bool = False
    _is_rejected: bool = False

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    @property
    def status(self) -> str:
        if self._is_accepted:
            return "accepted"
        if self._is_rejected:
            return "rejected"
        if self.is_expired:
            return "expired"
        return "pending"

    def accept(self):
        if self.is_expired:
            raise ValueError("Cannot accept an expired offer.")
        self._is_accepted = True

    def reject(self):
        self._is_rejected = True
