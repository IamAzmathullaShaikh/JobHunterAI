import logging
from typing import Any, Dict

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import ApplicationStatus, JobApplication

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Engine for calculating career metrics and conversion rates.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_career_metrics(self) -> Dict[str, Any]:
        """Calculates conversion rates and application distributions."""
        logger.info("Calculating career metrics...")

        try:
            stmt = select(JobApplication)
            result = await self.db.execute(stmt)
            applications = result.scalars().all()
        except Exception as e:
            logger.warning(f"Database query failed (possible schema mismatch): {e}")
            return self._empty_metrics()

        if not applications:
            return self._empty_metrics()

        # Convert to DataFrame for easy analysis
        try:
            df = pd.DataFrame(
                [
                    {
                        "status": app.status,
                        "match_score": app.match_score,
                        "applied_date": app.applied_date,
                    }
                    for app in applications
                ]
            )
        except AttributeError as e:
            logger.error(f"Missing expected column in JobApplication: {e}")
            return self._empty_metrics()

        total_applied = len(df[df["status"] != ApplicationStatus.WISHLIST])
        total_interviews = len(df[df["status"] == ApplicationStatus.INTERVIEWING])
        total_offers = len(df[df["status"] == ApplicationStatus.OFFERED])

        # Safer rate calculation
        interview_rate = (
            (total_interviews / total_applied * 100) if total_applied > 0 else 0.0
        )
        offer_rate = (total_offers / total_applied * 100) if total_applied > 0 else 0.0

        status_counts = df["status"].value_counts().to_dict()
        # Convert enum keys to strings for JSON serializability
        status_counts = {
            str(k.value if hasattr(k, "value") else k): int(v)
            for k, v in status_counts.items()
        }

        avg_match = (
            df["match_score"].mean() if not df["match_score"].isnull().all() else 0.0
        )

        return {
            "total_applied": total_applied,
            "interview_conversion": round(interview_rate, 2),
            "offer_rate": round(offer_rate, 2),
            "status_distribution": status_counts,
            "average_match_score": round(avg_match, 2),
        }

    def _empty_metrics(self) -> Dict[str, Any]:
        return {
            "total_applied": 0,
            "interview_conversion": 0.0,
            "offer_rate": 0.0,
            "status_distribution": {},
            "average_match_score": 0.0,
        }
