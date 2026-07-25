from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class TrendDTO:
    direction: str
    delta: float
    previous: float
    current: float


@dataclass(frozen=True)
class KPIDTO:
    id: str
    name: str
    value: float
    target: Optional[float]
    unit: str
    trend: Optional[TrendDTO]


@dataclass(frozen=True)
class RecommendationDTO:
    priority: str
    category: str
    message: str
    impact: float


@dataclass(frozen=True)
class DashboardDTO:
    kpis: List[KPIDTO]
    recommendations: List[RecommendationDTO]
    funnel: Dict[str, int]
    conversion_rate: float


@dataclass(frozen=True)
class ExecutiveSummaryDTO:
    content: str
    generated_at: str
    is_ai_generated: bool


@dataclass(frozen=True)
class ObservabilityMetricsDTO:
    latency_ms: Dict[str, float]  # e.g. {"dashboard": 120.0, "matching": 45.0}
    request_counts: Dict[str, int]
    error_rates: Dict[str, float]
    cache_stats: Dict[str, float]  # hit_ratio, etc.
