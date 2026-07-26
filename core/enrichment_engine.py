import json
import logging
import re
from typing import Any, Dict, List, Optional

from core.ai.llm_client import get_llm_client

logger = logging.getLogger("jobhunterai.enrichment")

class EnrichmentEngine:
    """
    Extracts structured metadata from raw job descriptions using LLMs.
    """

    async def enrich_job(self, description: str) -> Dict[str, Any]:
        """
        Parses JD to extract skills, seniority, and benefits.
        """
        if not description or len(description) < 50:
            return {}

        prompt = f"""
        Extract professional metadata from this job description.
        Return ONLY valid JSON.

        JD: {description[:3000]}

        Required JSON structure:
        {{
            "required_skills": ["Skill A", "Skill B"],
            "technologies": ["Tech X", "Tech Y"],
            "seniority": "Junior/Mid/Senior/Staff/Lead",
            "benefits": ["Benefit 1", "Benefit 2"],
            "work_model": "Remote/Hybrid/Onsite"
        }}
        """

        try:
            import asyncio
            client = get_llm_client()
            # Simple retry for rate limits
            for attempt in range(2):
                try:
                    res = await client.chat_completion(
                        messages=[{"role": "user", "content": prompt}]
                    )
                    content = res.choices[0].message.content if hasattr(res, "choices") else str(res)

                    match = re.search(r"\{.*\}", content, re.DOTALL)
                    if match:
                        return json.loads(match.group())
                    break
                except Exception as inner_e:
                    if "rate_limit" in str(inner_e).lower() and attempt == 0:
                        await asyncio.sleep(2)
                        continue
                    raise inner_e
        except Exception as e:
            logger.error(f"Job enrichment failed: {e}")

        return {}

enrichment_engine = EnrichmentEngine()
