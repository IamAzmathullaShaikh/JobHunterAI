from dotenv import load_dotenv
import os
import sys

# Load environment variables from the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, ".env"), override=True)

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Add project root and core/ to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "core"))

from core.database.connection import get_db_session
from backend.api import jobs, profile, ats, cover_letter, interview, outreach, system, resumes, recruiters, tracker
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import logging

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/backend.log")
    ]
)
logger = logging.getLogger("jobhunterai")

app = FastAPI(title="JobHunterAI Pro", version="3.0.0")

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Request Size Limiting Middleware
MAX_REQUEST_SIZE = 5 * 1024 * 1024 # 5MB

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.method == "POST":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                content={"detail": "Payload too large. Max size is 5MB."}
            )
    return await call_next(request)

# Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    err_str = str(exc).lower()
    if "quota" in err_str or "rate limit" in err_str:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Cloud AI quota reached. Falling back to local engine.", "quota_exhausted": True}
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(system.router)
app.include_router(profile.router)
app.include_router(ats.router)
app.include_router(cover_letter.router)
app.include_router(interview.router)
app.include_router(outreach.router)
app.include_router(resumes.router)
app.include_router(recruiters.router)
app.include_router(tracker.router)
app.include_router(jobs.router)

# Compatibility Route for Scraper
from core.scraper import scrape_jobs
@app.post("/api/scrape")
async def legacy_scrape(payload: dict):
    return await scrape_jobs(payload)

@app.on_event("startup")
async def startup_event():
    from core.db import init_db
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "JobHunterAI Backend"}

# Serve Frontend Static Files (Production)
frontend_path = os.path.join(project_root, "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        # Support SPA routing by serving index.html on 404
        return FileResponse(os.path.join(frontend_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
