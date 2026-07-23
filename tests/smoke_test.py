import os
import sys
import logging
from pathlib import Path

# Add project root to path so 'from core...' imports work
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smoke_test")

async def test_resume_parser():
    logger.info("Testing Resume Parser...")
    from core.ai.resume_parser import parse_resume
    result = await parse_resume(text="Alex Developer, senior engineer with Python, Docker, and React. Reach me at alex@example.com")
    logger.info(f"Result Source: {result.get('source')}")
    # Local parser returns 'key_skills' in the 'data' dict
    logger.info(f"Skills Found: {result.get('data', {}).get('key_skills')}")

async def test_matcher():
    logger.info("Testing Matcher...")
    from core.ai.matcher import score_match
    candidate = "Experienced Python developer with FastAPI"
    job = "Looking for a Python Backend Engineer with FastAPI skills"
    result = await score_match(candidate, job)
    logger.info(f"Result Source: {result.get('source')}")
    logger.info(f"Score: {result.get('score')}")

async def test_generator():
    logger.info("Testing Generator...")
    from core.ai.generator import generate_cover_letter
    candidate = {"full_name": "Alex", "key_skills": ["Python"], "experience_highlights": ["Built a cloud platform"]}
    job = {"title": "Engineer", "company_name": "Tech Corp"}
    result = await generate_cover_letter(candidate, job)
    logger.info(f"Result Source: {result.get('source')}")
    logger.info(f"Cover Letter Preview: {result.get('cover_letter')[:100]}...")

async def test_enricher():
    logger.info("Testing Enricher...")
    from core.enricher import find_decision_makers
    result = await find_decision_makers("Google", "Recruiter")
    logger.info(f"Result Source: {result[0].get('source') if isinstance(result, list) and len(result) > 0 else 'N/A'}")
    logger.info(f"Leads Found: {len(result)}")

async def test_scraper():
    logger.info("Testing Scraper...")
    from core.scraper import scrape_jobs
    result = await scrape_jobs({"query": "Python Developer", "limit": 2})
    logger.info(f"Result Source: {result.get('source')}")
    logger.info(f"Jobs Discovered: {len(result.get('data', []))}")

async def run_tests():
    logger.info("Starting JobHunterAI Dual-Engine Smoke Tests")

    # Run tests
    try: await test_resume_parser()
    except Exception as e: logger.error(f"Resume Parser test failed: {e}")

    try: await test_matcher()
    except Exception as e: logger.error(f"Matcher test failed: {e}")

    try: await test_generator()
    except Exception as e: logger.error(f"Generator test failed: {e}")

    try: await test_enricher()
    except Exception as e: logger.error(f"Enricher test failed: {e}")

    try: await test_scraper()
    except Exception as e: logger.error(f"Scraper test failed: {e}")

    logger.info("Smoke Tests Completed.")

if __name__ == "__main__":
    asyncio.run(run_tests())
