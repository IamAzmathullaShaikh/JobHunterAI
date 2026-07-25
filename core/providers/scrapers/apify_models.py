from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ApifyRunStatus(str, Enum):
    """Standardized execution states for Apify actor runs."""

    READY = "READY"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    ABORTED = "ABORTED"


class ApifyRunMetadata(BaseModel):
    """Detailed metadata about a specific Apify actor run."""

    run_id: str
    actor_id: str
    status: ApifyRunStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    dataset_id: Optional[str] = None
    usage_usd: float = 0.0
    item_count: int = 0


class ApifyScrapeResult(BaseModel):
    """Standardized container for scraper results and telemetry."""

    items: List[Dict[str, Any]]
    metadata: ApifyRunMetadata
    source: str = "apify"
