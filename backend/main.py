import os
import sys
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Add core/ to sys.path to resolve internal imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "core"))

from database.connection import get_db_session
from api import jobs, profile, ats, cover_letter, interview, outreach, system

app = FastAPI(title="JobHunterAI Pro", version="3.0.0")

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

@app.on_event("startup")
async def startup_event():
    from db import init_db
    await init_db()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "JobHunterAI Backend"}

@app.get("/api/jobs", response_model=List[JobListingRead])
async def get_jobs(db: AsyncSession = Depends(get_db_session)):
    # Implementation using JobService
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
