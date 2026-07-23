import logging
import os
import json
import re
from typing import Dict, Any, List
from core.ai.smart_router import route
from core.ai.llm_client import get_llm_client
from core.schemas.ai_analysis import AIAnalysisCreate

logger = logging.getLogger("jobhunterai.matcher")

# Global cache for local model to avoid reloading
_local_model = None

def get_local_model():
    global _local_model
    if _local_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _local_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            logger.warning("sentence-transformers not installed. Local semantic match will use basic keyword counting.")
    return _local_model

# --- Cloud Primary ---
async def cloud_analyze_fit(job_description: str, user_profile: str) -> Dict[str, Any]:
    """Uses Groq/Gemini to compute detailed match alignment."""
    client = get_llm_client()

    prompt = f"""
    Evaluate the fit compatibility between the candidate profile and the job description.
    Candidate Profile: {user_profile[:4000]}
    Job Description: {job_description[:4000]}

    Return strict JSON:
    {{
        "match_score": 85.5,
        "fit_summary": "Concise summary...",
        "keywords_matched": ["Skill 1", "Skill 2"],
        "keywords_missing": ["Skill 3"]
    }}
    """

    response = await client.chat_completion(
        model=None,
        messages=[
            {"role": "system", "content": "You are an expert technical recruiter analyzing resume-to-job alignment."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content if hasattr(response, 'choices') else str(response)
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        return {"source": "cloud", "data": json.loads(match.group())}

    raise ValueError("Cloud failed to return valid JSON for alignment")

cloud_analyze_fit.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

# --- Local Fallback ---
async def local_analyze_fit(job_description: str, user_profile: str) -> Dict[str, Any]:
    """Uses sentence-transformers and keyword overlap for detailed fit analysis."""
    job_lower = job_description.lower()
    profile_lower = user_profile.lower()

    tech_keywords = ["python", "java", "react", "node", "typescript", "aws", "docker", "kubernetes", "sql", "nosql", "fastapi", "express", "kotlin", "swift", "flutter", "react native"]
    matched = [k for k in tech_keywords if k in job_lower and k in profile_lower]
    missing = [k for k in tech_keywords if k in job_lower and k not in profile_lower]

    score = 50.0
    model = get_local_model()
    if model:
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            embeddings = model.encode([user_profile, job_description])
            score = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]) * 100
        except:
            pass
    elif tech_keywords:
        job_tech_count = len([k for k in tech_keywords if k in job_lower])
        if job_tech_count > 0:
            score = (len(matched) / job_tech_count) * 100

    return {
        "source": "local",
        "data": {
            "match_score": round(score, 1),
            "fit_summary": "Evaluated via local semantic/heuristic fallback.",
            "keywords_matched": matched,
            "keywords_missing": missing
        }
    }

local_analyze_fit.safe_placeholder = {
    "source": "error",
    "data": {"match_score": 0, "fit_summary": "Analysis failed", "keywords_matched": [], "keywords_missing": []}
}

# --- Public API & Compatibility Class ---
class JobMatcher:
    """Backward-compatible class wrapper for tiered matching logic."""
    async def analyze_fit(self, job_description: str, user_profile: str) -> Dict[str, Any]:
        return await route(cloud_analyze_fit, local_analyze_fit, job_description, user_profile)

    async def evaluate_match(self, job_description: str, user_profile: str) -> AIAnalysisCreate:
        res = await self.analyze_fit(job_description, user_profile)
        data = res["data"]
        return AIAnalysisCreate(
            match_score=data.get("match_score", 0),
            fit_summary=data.get("fit_summary", ""),
            keywords_matched=data.get("keywords_matched", []),
            keywords_missing=data.get("keywords_missing", []),
            quota_safe=True
        )

async def score_match(candidate: str, job: str) -> Dict[str, Any]:
    """Simple functional score API."""
    res = await route(cloud_analyze_fit, local_analyze_fit, job, candidate)
    return {"source": res["source"], "score": res["data"].get("match_score", 0) / 100.0}
