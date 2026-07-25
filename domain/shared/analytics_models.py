from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from domain.shared.value_objects import DomainId


class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


@dataclass(frozen=True)
class Trend:
    """Historical comparison of a metric."""

    direction: TrendDirection
    delta_percentage: float
    previous_value: float
    current_value: float


@dataclass(frozen=True)
class TimeSeriesMetric:
    """A data point in a temporal sequence."""

    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KPI:
    """Key Performance Indicator with target tracking."""

    id: str
    name: str
    current_value: float
    target_value: Optional[float] = None
    unit: str = "percentage"  # percentage, count, days
    trend: Optional[Trend] = None
    history: List[TimeSeriesMetric] = field(default_factory=list)


@dataclass(frozen=True)
class Recommendation:
    """A prioritized task to improve a specific metric."""

    id: str
    category: str  # resume, matching, interview
    priority: str  # critical, high, medium, low
    message: str
    reason: str
    evidence: str
    expected_impact: float  # 0.0 to 1.0
    confidence: float = 1.0


@dataclass(frozen=True)
class DashboardWidget:
    """Metadata for a UI visualization component."""

    widget_id: str
    title: str
    visualization_type: str  # chart, counter, table, list
    metric_source: str  # ID of the KPI or data stream
    display_order: int
    refresh_interval_seconds: int = 3600
    is_visible: bool = True
