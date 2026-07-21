from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class JobListingBase(BaseModel):
    title: str = Field(..., description="Job title, e.g., Territory Sales Executive")
    company_name: str = Field(..., description="Hiring organization name")
    location: str = Field(..., description="Geographic bounds or Remote status")
    work_place_type: Optional[str] = Field("Onsite", description="Onsite, Hybrid, or Remote")
    job_type: str = Field("Full-Time", description="Full-Time, Internship, or Apprenticeship")
    source: str = Field(..., description="Origin channel (LinkedIn, Indeed, Naukri)")
    url: str = Field(..., description="Direct link to application")
    description_raw: str = Field(..., description="Unprocessed raw job description text")
    description_clean: Optional[str] = Field(None, description="Sanitized description text")
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = "USD"
    date_posted: Optional[datetime] = None

class JobListingCreate(JobListingBase):
    job_id_raw: str = Field(..., description="Unique platform ID string from the target job board")

class JobListingRead(JobListingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id_raw: str
    date_scraped: datetime