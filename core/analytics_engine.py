import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database.models import (
    ApplicationStatus, JobApplication, JobListing,
    Resume, CoverLetter, InterviewSession,
    RecruiterContact, MatchHistory, UserProfile
)
from core.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Unified Career Intelligence Engine.
    Aggregates data from all modules to provide holistic career insights.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_comprehensive_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Main entry point for fetching the full dashboard state.
        """
        logger.info(f"Aggregating comprehensive analytics for last {days} days...")

        # Calculate time threshold
        since = datetime.now(timezone.utc) - timedelta(days=days)

        # 1. Fetch data from all tables
        # Use a single gather if possible, but for simplicity we'll run sequential selects
        kpis = await self._get_kpis()
        timeline = await self._get_timeline(limit=20)
        job_stats = await self._get_job_stats()
        ats_trends = await self._get_ats_trends()
        skill_insights = await self._get_skill_insights()

        # 2. Generate AI Insights
        recommendations = await self._generate_ai_recommendations(kpis, skill_insights)

        # 3. Infer Career Status
        status = "Discovery Phase"
        if kpis["funnel"]["offers"] > 0:
            status = "Offer Received"
        elif kpis["funnel"]["interviews"] > 0:
            status = "Active Interviewing"
        elif kpis["funnel"]["applied"] > 10:
            status = "Volume Hunting"

        return {
            "kpis": kpis,
            "current_status": status,
            "timeline": timeline,
            "job_distribution": job_stats,
            "ats_trends": ats_trends,
            "skill_insights": skill_insights,
            "recommendations": recommendations,
            "meta": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "time_range_days": days
            }
        }

    async def _get_kpis(self) -> Dict[str, Any]:
        """Aggregates high-level metrics from every platform module."""

        # Resumes
        resumes_count = await self.db.scalar(select(func.count(Resume.id)))

        # Applications
        stmt = select(JobApplication)
        res = await self.db.execute(stmt)
        apps = res.scalars().all()

        total_applied = len([a for a in apps if a.status != ApplicationStatus.WISHLIST])
        interviews = len([a for a in apps if a.status == ApplicationStatus.INTERVIEWING])
        offers = len([a for a in apps if a.status == ApplicationStatus.OFFERED])
        rejections = len([a for a in apps if a.status == ApplicationStatus.REJECTED])

        # Average ATS
        avg_ats = await self.db.scalar(select(func.avg(MatchHistory.match_score))) or 0.0

        # Recruiters
        recruiters_count = await self.db.scalar(select(func.count(RecruiterContact.id)))
        outreach_sent = await self.db.scalar(
            select(func.count(RecruiterContact.id)).where(RecruiterContact.status == "Sent")
        ) or 0
        replies = await self.db.scalar(
            select(func.count(RecruiterContact.id)).where(RecruiterContact.status == "Replied")
        ) or 0

        # Interview Prep
        interview_sessions = await self.db.scalar(select(func.count(InterviewSession.id)))
        avg_interview_score = await self.db.scalar(select(func.avg(InterviewSession.overall_score))) or 0.0

        return {
            "resume": {
                "total": resumes_count,
                "avg_ats_score": round(float(avg_ats), 1)
            },
            "funnel": {
                "applied": total_applied,
                "interviews": interviews,
                "offers": offers,
                "rejections": rejections,
                "success_rate": round((offers / total_applied * 100) if total_applied > 0 else 0, 1)
            },
            "networking": {
                "total_contacts": recruiters_count,
                "outreach_sent": outreach_sent,
                "response_rate": round((replies / outreach_sent * 100) if outreach_sent > 0 else 0, 1)
            },
            "practice": {
                "sessions_completed": interview_sessions,
                "avg_score": round(float(avg_interview_score), 1)
            }
        }

    async def _get_timeline(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Collates recent events from all modules into a sorted timeline."""
        events = []

        # Resumes
        res = await self.db.execute(select(Resume).order_by(Resume.created_at.desc()).limit(limit))
        for r in res.scalars().all():
            events.append({"type": "resume_created", "title": f"Created Resume: {r.name}", "date": r.created_at.isoformat()})

        # Applications
        res = await self.db.execute(select(JobApplication).order_by(JobApplication.date_created.desc()).limit(limit))
        for a in res.scalars().all():
            events.append({"type": "application_added", "title": f"Tracked: {a.job_title} at {a.company_name}", "date": a.date_created.isoformat()})

        # Recruiters
        res = await self.db.execute(select(RecruiterContact).order_by(RecruiterContact.created_at.desc()).limit(limit))
        for c in res.scalars().all():
            events.append({"type": "contact_found", "title": f"Discovered Lead: {c.name} ({c.company})", "date": c.created_at.isoformat()})

        # Cover Letters
        res = await self.db.execute(select(CoverLetter).order_by(CoverLetter.created_at.desc()).limit(limit))
        for cl in res.scalars().all():
            events.append({"type": "cl_generated", "title": f"Generated Letter: {cl.name}", "date": cl.created_at.isoformat()})

        # Interview Sessions
        res = await self.db.execute(select(InterviewSession).order_by(InterviewSession.created_at.desc()).limit(limit))
        for s in res.scalars().all():
            events.append({"type": "interview_session", "title": f"Interview Practice: {s.name}", "date": s.created_at.isoformat()})

        # Sort by date descending
        events.sort(key=lambda x: x["date"], reverse=True)
        return events[:limit]

    async def _get_job_stats(self) -> Dict[str, Any]:
        """Calculates job distribution metrics."""
        stmt = select(JobListing)
        res = await self.db.execute(stmt)
        jobs = res.scalars().all()

        if not jobs:
            return {}

        df = pd.DataFrame([{"source": j.source, "work_mode": j.work_place_type} for j in jobs])

        return {
            "by_source": df["source"].value_counts().to_dict(),
            "by_mode": df["work_mode"].value_counts().to_dict()
        }

    async def _get_ats_trends(self) -> List[Dict[str, Any]]:
        """Fetches historical ATS scores for trend analysis."""
        stmt = select(MatchHistory).order_by(MatchHistory.timestamp.asc())
        res = await self.db.execute(stmt)
        history = res.scalars().all()

        return [
            {
                "date": h.timestamp.strftime("%Y-%m-%d"),
                "score": h.match_score,
                "readability": h.readability_score
            }
            for h in history
        ]

    async def _get_skill_insights(self) -> Dict[str, Any]:
        """Identifies top requested skills and current gaps."""
        # 1. Get user skills
        res = await self.db.execute(select(UserProfile).order_by(UserProfile.updated_at.desc()).limit(1))
        profile = res.scalar_one_or_none()
        user_skills = set([s.lower() for s in (profile.key_skills or [])]) if profile else set()

        # 2. Get requested skills from saved jobs
        res = await self.db.execute(select(JobListing.required_skills))
        all_req_skills = res.scalars().all()

        skill_freq = {}
        for skills in all_req_skills:
            if not skills: continue
            for s in skills:
                s_low = s.lower()
                skill_freq[s_low] = skill_freq.get(s_low, 0) + 1

        # 3. Calculate gaps
        top_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        missing = [s for s, count in top_skills if s not in user_skills]

        return {
            "user_skill_count": len(user_skills),
            "top_market_skills": [{"name": s, "demand": c} for s, c in top_skills],
            "identified_gaps": missing[:5]
        }

    async def _generate_ai_recommendations(self, kpis: dict, skills: dict) -> List[str]:
        """Uses LLM to provide grounded career coaching advice."""

        prompt = f"""
        You are an elite career strategist. Analyze this candidate's job search data and provide 3-4 specific, actionable recommendations.

        KPIs:
        - Funnel: {kpis['funnel']}
        - Networking: {kpis['networking']}
        - ATS Avg: {kpis['resume']['avg_ats_score']}%

        Skill Gaps:
        - {skills['identified_gaps']}

        Instructions:
        1. Be specific (e.g., "Your response rate is low, try tailoring your outreach drafts").
        2. Prioritize actions with the highest impact on getting an offer.
        3. Keep each recommendation under 20 words.
        Return a simple JSON array of strings.
        """

        try:
            client = get_llm_client()
            res = await client.chat_completion(messages=[{"role": "user", "content": prompt}])
            content = res.choices[0].message.content if hasattr(res, "choices") else str(res)

            import re
            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.error(f"Advice generation failed: {e}")

        return ["Keep applying to high-match roles.", "Continue practicing your interview responses."]


    async def get_career_metrics(self) -> Dict[str, Any]:
        """Legacy compatibility method for basic metrics."""
        kpis = await self._get_kpis()
        return {
            "total_applied": kpis["funnel"]["applied"],
            "interview_conversion": kpis["funnel"]["interviews"],
            "offer_rate": kpis["funnel"]["success_rate"],
            "status_distribution": {},
            "average_match_score": kpis["resume"]["avg_ats_score"]
        }
