import re
import json
import logging
import io
from typing import Dict, Any, Optional, List
from core.ai.smart_router import route
from core.ai.llm_client import get_llm_client
from core.schemas.user_profile import ParsedProfileDTO

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

logger = logging.getLogger("jobhunterai.resume_parser")

# --- Cloud Primary ---
async def cloud_parse_resume(text: str = "", **kwargs) -> Dict[str, Any]:
    """Parses resume text using Groq or Gemini for structured JSON."""
    client = get_llm_client()

    prompt = f"""
    Analyze the following candidate resume text and extract structured profile parameters.
    Resume Text:
    ---
    {text[:4500]}
    ---

    Return strict JSON strictly matching this structure:
    {{
        "full_name": "Full Name or null",
        "target_roles": ["Role 1", "Role 2"],
        "key_skills": ["Skill 1", "Skill 2"],
        "education": ["Degree/Institution"],
        "total_experience_years": 3.5,
        "experience_highlights": ["Highlight 1"],
        "recommended_search_queries": ["Query 1"]
    }}
    """

    response = await client.chat_completion(
        model=None,
        messages=[
            {"role": "system", "content": "You are an AI career analyst extracting structured candidate profiles into JSON."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content if hasattr(response, 'choices') else str(response)
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        return {"source": "cloud", "data": json.loads(match.group())}

    raise ValueError("Cloud returned invalid JSON format")

cloud_parse_resume.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

# --- Local Fallback ---
async def local_parse_resume(text: Optional[str] = None, file_bytes: Optional[bytes] = None, **kwargs) -> Dict[str, Any]:
    """Fallback: Regex-based extraction when AI is unavailable."""
    raw_text = text or ""
    if file_bytes and pdfplumber:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                raw_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        except:
            pass

    # Basic skill extraction via regex
    taxonomy = [
        r"Python", r"Java", r"React", r"Node", r"FastAPI", r"Docker", r"SQL", r"AWS", r"TypeScript", r"Machine Learning"
    ]
    found_skills = [s.replace("\\", "") for s in taxonomy if re.search(rf"\b{s}\b", raw_text, re.I)]

    # Try to find name (simple heuristic: first line if short)
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    name = lines[0] if lines and len(lines[0]) < 30 else "Candidate"

    return {
        "source": "local",
        "data": {
            "full_name": name,
            "target_roles": ["Extracted Locally"],
            "key_skills": found_skills or ["General Skills"],
            "education": [],
            "total_experience_years": 0.0,
            "experience_highlights": ["Parsed via local heuristic fallback."],
            "recommended_search_queries": [found_skills[0] if found_skills else "Software Engineer"]
        }
    }

local_parse_resume.safe_placeholder = {
    "source": "error",
    "data": {
        "full_name": "User", "target_roles": [], "key_skills": [],
        "education": [], "total_experience_years": 0, "experience_highlights": [], "recommended_search_queries": []
    }
}

# --- Public API & Compatibility Class ---
class ResumeParser:
    """Backward-compatible class wrapper for tiered parsing logic."""
    async def parse_resume(self, text: str) -> ParsedProfileDTO:
        res = await route(cloud_parse_resume, local_parse_resume, text)
        return ParsedProfileDTO(**res["data"])

async def parse_resume(file_bytes: Optional[bytes] = None, text: Optional[str] = None) -> Dict[str, Any]:
    """Functional API returning source info and raw data."""
    return await route(cloud_parse_resume, local_parse_resume, text=text or "", file_bytes=file_bytes)
