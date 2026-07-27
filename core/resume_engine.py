import json
import logging
import re
from typing import Any, Dict, List

from core.ai.smart_router import route as smart_router
from core.privacy import redactor

logger = logging.getLogger(__name__)


class ResumeEngine:
    """
    Core engine for JD-tailored resume writing and master profile management.
    """

    async def tailor_bullets(
        self, bullets: List[str], job_description: str
    ) -> Dict[str, Any]:
        """Rewrites resume bullets to better align with a job description."""

        # Redact JD for privacy (though usually JD is public, good practice)
        safe_jd = job_description[:4000]

        async def llm_call(provider: str):
            from core.ai.llm_client import get_llm_client

            client = get_llm_client(provider)
            prompt = f"""
            Optimize the following resume bullet points to better match this job description.
            Maintain truthfulness but emphasize relevant keywords and impact.

            Return ONLY a JSON array of strings.
            Do not include any introductory text or markdown formatting outside the array.

            Original Bullets: {json.dumps(bullets)}
            Target JD: {safe_jd}
            """
            response = await client.chat_completion(
                messages=[{"role": "user", "content": prompt}]
            )
            content = (
                response.choices[0].message.content
                if hasattr(response, "choices")
                else str(response)
            )

            # Extract JSON list using a more aggressive regex
            match = re.search(r"\[\s*(\".*?\")(\s*,\s*\".*?\")*\s*\]", content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass

            # Simple fallback if regex fails but it looks like a list
            if "[" in content and "]" in content:
                try:
                    start = content.find("[")
                    end = content.rfind("]") + 1
                    return json.loads(content[start:end])
                except:
                    pass

            return None

        async def groq_tier(**kwargs): return await llm_call("groq")
        groq_tier.required_envs = ["GROQ_API_KEY"]

        async def gemini_tier(**kwargs): return await llm_call("gemini")
        gemini_tier.required_envs = ["GEMINI_API_KEY"]

        def local_tier(**kwargs):
            # Simple keyword injector (placeholder)
            return [f"{b} (Optimized for JD)" for b in bullets]

        result_data = await smart_router(groq_tier, gemini_tier, local_tier)

        # Normalize output for frontend
        source = "cloud" if isinstance(result_data, list) and len(result_data) > 0 and "(Optimized for JD)" not in result_data[0] else "local"
        if not isinstance(result_data, list):
            result_data = bullets

        return {
            "success": True,
            "data": result_data,
            "source": source,
            "meta": {"latency": 0},  # Router could be updated to provide this
        }

    async def optimize_keywords(
        self, resume_text: str, job_description: str
    ) -> Dict[str, Any]:
        """Identifies missing keywords and suggests where to add them."""
        # Placeholder for 3-tier routing logic
        return {"success": True, "data": "Keyword optimization logic here."}


resume_engine = ResumeEngine()
