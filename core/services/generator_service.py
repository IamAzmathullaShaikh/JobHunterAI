import json
import logging
import re
from typing import Any, Dict, List, Optional
from jinja2 import Template
from core.ai.llm_client import get_llm_client, Capability
from core.ai.smart_router import route as smart_route
from core.privacy import redactor
from core.caching import AICache
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("jobhunterai.generator_service")

class GeneratorService:
    """Specialized service for AI-generated career documents and outreach."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.cache = AICache(db_session)

    def _truncate_text(self, text: str, max_chars: int = 4000) -> str:
        if not text: return ""
        if len(text) <= max_chars: return text
        return text[:max_chars] + "... [Truncated]"

    async def generate_cover_letter_structured(
        self,
        resume_content: Dict[str, Any],
        job_description: str,
        writing_style: str = "Professional",
        company_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Workflow: Grounded, styled, and structured cover letter generation."""
        safe_jd = self._truncate_text(job_description, 3000)
        cache_key = f"cl_struct_{hash(str(resume_content))}_{safe_jd[:500]}_{writing_style}"

        cached = await self.cache.get(cache_key)
        if cached:
            return {"success": True, "source": "local_cache", "data": cached}

        prompt = f"""
        You are an expert career coach and technical writer.
        Generate a highly personalized, structured cover letter.

        Writing Style: {writing_style}
        Target Company: {company_name or 'the company'}

        Candidate Resume Context:
        {json.dumps(resume_content)}

        Target Job Description:
        {safe_jd}

        Strict Output Format (JSON only):
        {{
            "salutation": "...",
            "opening": "...",
            "why_us": "...",
            "experience_highlight": "...",
            "closing": "...",
            "sign_off": "..."
        }}
        """

        async def llm_call(provider: str):
            client = get_llm_client(provider)
            model = client.get_model_for_capability(Capability.REASONING)
            response = await client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = (
                response.choices[0].message.content
                if hasattr(response, "choices")
                else str(response)
            )

            import re
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return None

        async def groq_tier(**kwargs): return await llm_call("groq")
        groq_tier.required_envs = ["GROQ_API_KEY"]

        async def gemini_tier(**kwargs): return await llm_call("gemini")
        gemini_tier.required_envs = ["GEMINI_API_KEY"]

        def local_call():
            return {
                "salutation": "Dear Hiring Manager,",
                "opening": f"I am writing to express my interest in the role at {company_name or 'your company'}.",
                "why_us": "Your company's mission aligns perfectly with my career goals.",
                "experience_highlight": "In my previous roles, I have demonstrated a strong ability to deliver results.",
                "closing": "Thank you for your time and consideration.",
                "sign_off": "Best regards,"
            }

        result_data = await smart_route(groq_tier, gemini_tier, local_call)

        final_result = {
            "success": True,
            "data": result_data,
            "source": "cloud" if "opening" in result_data and len(result_data["opening"]) > 50 else "local"
        }

        await self.cache.set(cache_key, result_data)
        return final_result

    async def regenerate_cl_section(
        self,
        section_id: str,
        resume_content: Dict[str, Any],
        job_description: str,
        writing_style: str = "Professional"
    ) -> Dict[str, Any]:
        """Regenerates a single section of a cover letter."""

        prompt = f"""
        You are an elite career coach. Regenerate ONLY the "{section_id}" section of a cover letter.
        Writing Style: {writing_style}
        Candidate Context: {json.dumps(resume_content)}
        Target JD: {job_description[:2000]}
        Return ONLY the text for the "{section_id}" paragraph.
        """

        async def llm_call(provider: str):
            client = get_llm_client(provider)
            model = client.get_model_for_capability(Capability.REASONING)
            response = await client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content if hasattr(response, "choices") else str(response)

        async def groq_tier(**kwargs): return await llm_call("groq")
        groq_tier.required_envs = ["GROQ_API_KEY"]

        async def gemini_tier(**kwargs): return await llm_call("gemini")
        gemini_tier.required_envs = ["GEMINI_API_KEY"]

        result_text = await smart_route(groq_tier, gemini_tier, lambda: f"Refined {section_id} paragraph.")

        return {"success": True, "data": result_text}

    async def generate_recruiter_outreach(
        self,
        recruiter_name: str,
        recruiter_title: str,
        company_name: str,
        resume_content: Dict[str, Any],
        message_type: str = "Intro",
        writing_style: str = "Professional"
    ) -> Dict[str, Any]:
        """Context-aware and styled recruiter outreach generation."""

        prompt = f"""
        Draft a high-conversion {message_type} message for a recruiter on LinkedIn.
        Writing Style: {writing_style}
        Recruiter: {recruiter_name} ({recruiter_title} at {company_name})
        Candidate Context: {json.dumps(resume_content)}
        Guidelines: Concise (under 100 words). Tone: {writing_style}.
        Return ONLY the message text.
        """

        async def llm_call(provider: str):
            client = get_llm_client(provider)
            model = client.get_model_for_capability(Capability.REASONING)
            response = await client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content if hasattr(response, "choices") else str(response)

        async def groq_tier(**kwargs): return await llm_call("groq")
        groq_tier.required_envs = ["GROQ_API_KEY"]

        async def gemini_tier(**kwargs): return await llm_call("gemini")
        gemini_tier.required_envs = ["GEMINI_API_KEY"]

        result_text = await smart_route(groq_tier, gemini_tier, lambda: f"Hi {recruiter_name}, I'm following up...")

        return {"success": True, "data": result_text}

    async def generate_outreach(self, target_role: str, company: str) -> Dict[str, Any]:
        """Workflow: 3-Tiered outreach message generation (generic)."""
        cache_key = f"outreach_{target_role}_{company}"
        cached = await self.cache.get(cache_key)
        if cached:
            return {"success": True, "source": "cache", "data": cached}

        prompt = f"Draft a short, professional LinkedIn outreach message for a {target_role} position at {company}."

        async def llm_call(provider: str):
            client = get_llm_client(provider)
            model = client.get_model_for_capability(Capability.REASONING)
            response = await client.chat_completion(
                model=model, messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content if hasattr(response, "choices") else str(response)

        async def groq_tier(**kwargs): return await llm_call("groq")
        groq_tier.required_envs = ["GROQ_API_KEY"]

        async def gemini_tier(**kwargs): return await llm_call("gemini")
        gemini_tier.required_envs = ["GEMINI_API_KEY"]

        result_data = await smart_route(groq_tier, gemini_tier, lambda: f"Hi [Name], I noticed the {target_role} opening at {company}...")

        if result_data:
            await self.cache.set(cache_key, result_data)

        return {"success": True, "data": result_data, "source": "ai"}
