from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ComponentHealthDTO:
    name: str
    status: str
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlatformStatusDTO:
    overall_status: str
    version: str
    environment: str
    timestamp: str
    components: List[ComponentHealthDTO]
    configuration_valid: bool
    config_errors: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class PerformanceMetricDTO:
    name: str
    value: float
    unit: str


@dataclass(frozen=True)
class PerformanceReportDTO:
    timestamp: str
    metrics: List[PerformanceMetricDTO]
    summary: str
