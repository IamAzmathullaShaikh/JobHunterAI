import os
import sys
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Add core/ to sys.path to resolve internal imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "core"))

from database.connection import get_db_session
from api import jobs, profile

app = FastAPI(title="JobHunterAI API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(profile.router)

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
