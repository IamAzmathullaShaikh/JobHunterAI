import os
import logging
import urllib.parse
from typing import List, Dict, Any
from core.ai.smart_router import route
from core.ai.generator import generate_cover_letter # We can reuse this or specialized outreach

logger = logging.getLogger("jobhunterai.enricher")

# --- Cloud Primary ---
async def cloud_find_decision_makers(company: str, role: str) -> List[Dict[str, Any]]:
    """Uses Hunter.io or Apify to find verified emails/leads."""
    import requests

    # Attempt Apify first if token exists, fallback to Hunter
    apify_token = os.getenv("APIFY_API_TOKEN")
    if apify_token:
        # Placeholder for Apify enrichment logic
        pass

    hunter_key = os.getenv("HUNTER_API_KEY")
    if hunter_key:
        domain = f"{company.lower().replace(' ', '')}.com" # Simple heuristic
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={hunter_key}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if "data" in data and "emails" in data["data"]:
                leads = []
                for email in data["data"]["emails"][:5]:
                    leads.append({
                        "person_name": f"{email.get('first_name', '')} {email.get('last_name', '')}".strip() or "Verified Contact",
                        "title": email.get("position", role),
                        "email": email.get("value"),
                        "source": "hunter.io",
                        "confidence_score": 0.9
                    })
                return leads
        except Exception as e:
            logger.error(f"Hunter.io call failed: {e}")

    raise ValueError("Cloud providers (Apify/Hunter) returned no results or failed")

cloud_find_decision_makers.required_envs = [["APIFY_API_TOKEN", "HUNTER_API_KEY"]]

# --- Local Fallback ---
async def local_find_decision_makers(company: str, role: str) -> List[Dict[str, Any]]:
    """Returns structured search card results for manual exploration."""
    logger.info(f"Local fallback: Generating search leads for {company}")

    q_linkedin = urllib.parse.quote(f'site:linkedin.com/in/ "{company}" "{role}"')
    q_google = urllib.parse.quote(f'"{company}" "{role}" contact email')

    return [
        {
            "person_name": "LinkedIn Search",
            "title": f"Search for {role}",
            "email": "Use LinkedIn Message",
            "type": "search_card",
            "url": f"https://www.linkedin.com/search/results/people/?keywords={q_linkedin}",
            "desc": "Search for decision makers directly on LinkedIn.",
            "source": "local_search",
            "confidence_score": 0.5
        },
        {
            "person_name": "Google Search",
            "title": f"Find {company} Contacts",
            "email": "Find on Google",
            "type": "search_card",
            "url": f"https://www.google.com/search?q={q_google}",
            "desc": "Find publicly listed contact information.",
            "source": "local_search",
            "confidence_score": 0.4
        }
    ]

local_find_decision_makers.safe_placeholder = []

# --- Public API & Compatibility Class ---
class Enricher:
    """Backward-compatible class for recruiter discovery and outreach."""

    async def find_decision_makers(self, company: str, role: str = "Engineering") -> List[Dict[str, Any]]:
        return await route(cloud_find_decision_makers, local_find_decision_makers, company, role)

    async def draft_outreach(
        self,
        resume_text: str,
        job_title: str,
        company: str,
        recruiter_name: str,
        user_name: str
    ) -> Dict[str, Any]:
        """Drafts a cold outreach email by calling the generator."""
        from core.ai.generator import generate_cover_letter

        # We'll treat the outreach as a short cover letter for simplicity in this tiering
        candidate = {
            "full_name": user_name,
            "resume_text": resume_text,
            "key_skills": ["Software Engineering"] # Heuristic if not parsed
        }
        job = {
            "title": job_title,
            "company_name": company,
            "recruiter_name": recruiter_name
        }

        res = await generate_cover_letter(candidate, job)
        return {
            "success": True,
            "source": res["source"],
            "data": res["cover_letter"]
        }

enricher = Enricher()

async def find_decision_makers(company: str, role: str) -> List[Dict[str, Any]]:
    return await route(cloud_find_decision_makers, local_find_decision_makers, company, role)
