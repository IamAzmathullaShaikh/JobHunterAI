import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from core.ai.llm_client import get_llm_client, Capability
from core.ai.smart_router import route as smart_route

logger = logging.getLogger("jobhunterai.interview_service")

class InterviewService:
    """Specialized service for AI-powered interview coaching and feedback."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def generate_questions(
        self,
        resume_content: Dict[str, Any],
        job_description: str,
        difficulty: str = "Senior",
    ) -> List[Dict[str, Any]]:
        """Generates 5 role-specific and resume-grounded interview questions."""

        prompt = f"""
        You are an elite technical interviewer. Generate 5 unique interview questions for a candidate.

        Difficulty Level: {difficulty}

        Candidate Resume:
        {json.dumps(resume_content)}

        Target Job Description:
        {job_description[:2000]}

        Requirements:
        1. 2 Technical questions specifically probing technologies mentioned in the resume relative to the JD.
        2. 1 Behavioral question targeting a project or achievement listed in the resume.
        3. 1 System Design or Architecture question relative to the seniority: {difficulty}.
        4. 1 "Company Culture" or HR question based on the JD context.

        Output Format (JSON array only):
        [
            {{"question_text": "...", "category": "Technical"}},
            ...
        ]
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
            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return None

        async def groq_tier(**kwargs): return await llm_call("groq")
        groq_tier.required_envs = ["GROQ_API_KEY"]

        async def gemini_tier(**kwargs): return await llm_call("gemini")
        gemini_tier.required_envs = ["GEMINI_API_KEY"]

        def local_tier(**kwargs):
            return [
                {"question_text": "Tell me about your most challenging project.", "category": "Behavioural"},
                {"question_text": "How do you handle technical debt?", "category": "Technical"},
                {"question_text": f"Why are you a good fit for this {difficulty} role?", "category": "HR"},
            ]

        return await smart_route(groq_tier, gemini_tier, local_tier)

    async def evaluate_answer(
        self, question: str, answer: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provides detailed feedback and scoring for an interview answer."""

        prompt = f"""
        Evaluate this interview answer.
        Question: {question}
        User Answer: {answer}

        {f"Context (Resume/JD): {context}" if context else ""}

        Critique the answer based on:
        1. STAR Method usage (for behavioral).
        2. Technical accuracy (for technical).
        3. Clarity and Confidence.

        Output Format (JSON only):
        {{
            "score": 8.5,
            "strengths": ["...", "..."],
            "weaknesses": ["...", "..."],
            "suggestions": "...",
            "improved_answer": "..."
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

        def local_tier(**kwargs):
            return {
                "score": 5.0,
                "strengths": ["Answer provided"],
                "weaknesses": ["Local analysis limited"],
                "suggestions": "Try to use the STAR method.",
                "improved_answer": "I don't have a local improved answer yet."
            }

        return await smart_route(groq_tier, gemini_tier, local_tier)

    async def provide_star_feedback(self, question: str, response: str) -> Dict[str, Any]:
        """Analyzes response specifically for STAR method compliance."""
        return await self.evaluate_answer(question, response)
