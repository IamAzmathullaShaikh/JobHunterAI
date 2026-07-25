import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from domain.shared.value_objects import CandidateId, DomainId


@dataclass(frozen=True)
class AnalyticsEvent:
    """Immutable record of an analytics-significant occurrence."""

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    candidate_id: CandidateId
    event_type: str  # kpi_change, milestone_reached, report_exported
    metric_id: str
    previous_value: float
    new_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"


@dataclass(frozen=True)
class HistoricalSnapshot:
    """A point-in-time state of multiple KPIs for trend analysis."""

    snapshot_id: uuid.UUID = field(default_factory=uuid.uuid4)
    candidate_id: CandidateId
    timestamp: datetime = field(default_factory=datetime.now)
    kpis: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
