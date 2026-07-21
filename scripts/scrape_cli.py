#!/usr/bin/env python3
"""CLI bridge for the Node server.

Reads a JSON object on stdin: {search_query, location, job_type, limit}.
Runs the real scraper fleet and prints a JSON array of listings on stdout.
All logging goes to stderr so stdout stays pure JSON.
"""
import os
import sys
import json
import asyncio

# Ensure the repo root is importable so `import scrapers...` resolves.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _configure_logging():
    try:
        from loguru import logger
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    except ImportError:
        pass


def _serialize(job):
    data = job.model_dump() if hasattr(job, "model_dump") else dict(job)
    posted = data.get("date_posted")
    if posted is not None and hasattr(posted, "isoformat"):
        data["date_posted"] = posted.isoformat()
    return data


async def _run(params):
    from scrapers.manager import ScraperManager  # lazy: pulls in playwright
    manager = ScraperManager()
    listings = await manager.run_all(
        search_query=params["search_query"],
        location=params.get("location") or "Remote",
        limit_per_site=int(params.get("limit") or 10),
        job_type=params.get("job_type") or "Full-Time",
    )
    return [_serialize(job) for job in listings]


def main():
    _configure_logging()
    raw = sys.stdin.read() or "{}"
    params = json.loads(raw)
    if not params.get("search_query"):
        sys.stdout.write(json.dumps([]))
        return
    results = asyncio.run(_run(params))
    sys.stdout.write(json.dumps(results))


if __name__ == "__main__":
    main()
