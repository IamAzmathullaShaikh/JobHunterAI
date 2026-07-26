import json
import logging
from typing import Any, Dict, List

from core.ai.llm_client import get_llm_client

logger = logging.getLogger("jobhunterai.ranking")

class RankingEngine:
    """
    Ranks recruiter leads based on resume relevance and departmental overlap.
    """

    async def rank_recruiters(
        self,
        resume_content: Dict[str, Any],
        target_department: str,
        recruiters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Uses LLM to rank discovered recruiters and provide match explanations.
        """
        if not recruiters:
            return []

        prompt = f"""
        Rank the following recruiter leads for a candidate with this resume summary.
        Candidate Summary: {resume_content.get('summary', 'Experienced professional')}
        Target Department: {target_department}

        Recruiters:
        {json.dumps(recruiters)}

        Return a JSON array of objects, each including:
        1. "person_name": (exact match from input)
        2. "confidence_score": (0.0 - 1.0)
        3. "match_explanation": (one sentence explaining why they are a good match)
        """

        try:
            client = get_llm_client()
            res = await client.chat_completion(
                messages=[{"role": "user", "content": prompt}]
            )
            content = res.choices[0].message.content if hasattr(res, "choices") else str(res)

            import re
            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                rankings = json.loads(match.group())
                # Merge rankings back into recruiters
                rank_map = {r["person_name"]: r for r in rankings}

                for rec in recruiters:
                    rank_info = rank_map.get(rec.get("person_name", ""), {})
                    rec["confidence_score"] = rank_info.get("confidence_score", rec.get("confidence_score", 0.5))
                    rec["match_explanation"] = rank_info.get("match_explanation", "Standard department match.")

                # Sort by score descending
                recruiters.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)

            return recruiters
        except Exception as e:
            logger.error(f"Ranking failed: {e}")
            return recruiters

ranking_engine = RankingEngine()
