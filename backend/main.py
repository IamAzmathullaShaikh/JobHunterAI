import os
import sys
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
MAX_REQUEST_SIZE = 100 * 1024 # 100KB

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.method == "POST":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                content={"detail": "Payload too large. Max size is 100KB."}
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
app.include_router(jobs.router)
app.include_router(profile.router)
app.include_router(ats.router)
app.include_router(cover_letter.router)
app.include_router(interview.router)
app.include_router(outreach.router)
app.include_router(system.router)
app.include_router(resumes.router)
app.include_router(recruiters.router)
app.include_router(tracker.router)

@app.on_event("startup")
async def startup_event():
    from core.db import init_db
    await init_db()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "JobHunterAI Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
