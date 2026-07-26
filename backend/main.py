import logging
import os
import sys

from dotenv import load_dotenv

# Add project root and core/ to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "core"))

# Load environment variables from the project root
load_dotenv(os.path.join(project_root, ".env"), override=True)

# Configure logging using standard library
from core.utils.logging_config import RequestIDMiddleware

logger = logging.getLogger("jobhunterai")

from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add project root and core/ to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "core"))

from contextlib import asynccontextmanager

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api import (ats, cover_letter, interview, jobs, outreach, profile,
                         recruiters, resumes, system, tracker)
from core.config.settings import settings
from core.database.connection import get_db_session
from core.lifecycle import AppLifecycleManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Modernized startup orchestrated via AppLifecycleManager
    await AppLifecycleManager.startup()
    yield
    # Modernized shutdown
    await AppLifecycleManager.shutdown()


app = FastAPI(title="JobHunterAI Pro", version="1.0.0", lifespan=lifespan)
app.add_middleware(RequestIDMiddleware)

# Ensure logs directory exists
os.makedirs(settings.LOG_DIR, exist_ok=True)

# Request Size Limiting Middleware
MAX_REQUEST_SIZE = 5 * 1024 * 1024  # 5MB


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.method == "POST":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                content={"detail": "Payload too large. Max size is 5MB."},
            )
    return await call_next(request)


from core.exceptions import JobHunterException


# Global Exception Handlers
@app.exception_handler(JobHunterException)
async def jobhunter_exception_handler(request: Request, exc: JobHunterException):
    logger.error(f"Application Error: {exc.message} | Details: {exc.details}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    err_str = str(exc).lower()
    logger.critical(f"Unhandled Exception: {str(exc)}", exc_info=True)

    if "quota" in err_str or "rate limit" in err_str:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Cloud AI quota reached. Falling back to local engine.",
                "quota_exhausted": True,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error", "error": str(exc)},
    )


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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


@app.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db_session)):
    import psutil
    import time

    process = psutil.Process(os.getpid())

    health = {
        "status": "healthy",
        "service": "JobHunterAI Backend",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": int(time.time() - process.create_time()),
        "memory_usage_mb": round(process.memory_info().rss / 1024 / 1024, 2),
        "database": "connected",
        "ai_providers": {
            "groq": bool(settings.GROQ_API_KEY),
            "gemini": bool(settings.GEMINI_API_KEY),
            "apify": bool(settings.APIFY_API_TOKEN),
        },
    }
    try:
        from sqlalchemy import text

        await db.execute(select(1))
    except Exception as e:
        health["database"] = f"error: {str(e)}"
        health["status"] = "degraded"

    return health


# Serve Frontend Static Files (Production)
frontend_path = os.path.join(project_root, "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        # Support SPA routing by serving index.html on 404
        return FileResponse(os.path.join(frontend_path, "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
