import os
import json
import logging
from typing import Dict, Any
from jinja2 import Template
from core.ai.smart_router import route
from core.ai.llm_client import get_llm_client

logger = logging.getLogger("jobhunterai.generator")

# --- Cloud Primary ---
async def cloud_generate_cover(candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, str]:
    """Generates a cover letter using Groq or Gemini."""
    client = get_llm_client()

    prompt = f"""
    Write a professional, high-conversion cover letter.
    Candidate: {json.dumps(candidate)}
    Job: {json.dumps(job)}

    Ensure it highlights technical fit and quantified achievements.
    Return only the cover letter text.
    """

    response = await client.chat_completion(
        model=None, # Use default from client (Groq llama-3.3-70b or Gemini)
        messages=[
            {"role": "system", "content": "You are a professional technical writer creating personalized cover letters."},
            {"role": "user", "content": prompt}
        ]
    )

    if hasattr(response, 'choices'):
        text = response.choices[0].message.content
    else:
        # Handle cases where response might be different (e.g. Gemini direct)
        text = str(response)

    return {"source": "cloud", "cover_letter": text}

# Set required environment variables for primary function
cloud_generate_cover.required_envs = ["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]

# --- Local Fallback ---
async def local_generate_cover(candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, str]:
    """Generates a cover letter using a local Jinja2 template."""
    template_str = """
Dear Hiring Manager,

I am writing to express my strong interest in the {{ job_title }} position at {{ company }}.
With my background as a {{ candidate_title }} and my expertise in {{ skills }}, I am confident I can add significant value to your team.

At my previous role, I focused on {{ achievement }}, which aligns well with {{ company }}'s goals.
I look forward to the possibility of discussing how my experience can benefit your organization.

Best regards,
{{ candidate_name }}
    """

    template = Template(template_str)

    # Extract data with defaults
    data = {
        "job_title": job.get("title", "this role"),
        "company": job.get("company_name", "your company"),
        "candidate_title": candidate.get("title", "professional"),
        "skills": ", ".join(candidate.get("key_skills", ["relevant technologies"]))[:100],
        "achievement": candidate.get("experience_highlights", ["delivering high-quality solutions"])[0],
        "candidate_name": candidate.get("full_name", "the candidate")
    }

    text = template.render(**data)
    return {"source": "local", "cover_letter": text}

local_generate_cover.safe_placeholder = {"source": "error", "cover_letter": "Unable to generate cover letter."}

# --- Public API ---
async def generate_cover_letter(candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, str]:
    return await route(cloud_generate_cover, local_generate_cover, candidate, job)
