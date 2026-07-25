from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class GenerationMetadataDTO:
    provider: str
    model: str
    tokens_used: int
    latency_ms: float
    estimated_cost_usd: float = 0.0
    is_fallback: bool = False
    prompt_version: str = "1.0"


@dataclass(frozen=True)
class GenerationResultDTO:
    content: str
    quality_score: float
    metadata: GenerationMetadataDTO
    suggested_edits: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class TailoredResumeDTO:
    original_id: str
    tailored_text: str
    match_score_improvement: float
    changes_summary: str


@dataclass(frozen=True)
class CareerAssistantResponseDTO:
    """Unified response for all generation use cases."""

    result: GenerationResultDTO
    tracking_id: str
