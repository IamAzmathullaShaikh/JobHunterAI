from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, HttpUrl

class JobListingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="The job title post name.")
    company_name: str = Field(..., min_length=1, max_length=255, description="Hiring organization name.")
    location: str = Field(..., max_length=255, description="Geographic or spatial boundary location.")
    work_place_type: Optional[str] = Field(None, max_length=50, description="Remote, Hybrid, or Onsite.")
    source: str = Field(..., max_length=50, description="Platform source name (e.g., LinkedIn, Indeed).")
    url: str = Field(..., description="Direct operational application linkage URL.")
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    salary_currency: Optional[str] = Field("USD", max_length=10)
    date_posted: Optional[datetime] = None

class JobListingCreate(JobListingBase):
    job_id_raw: str = Field(..., description="Unique immutable platform tracking identifier.")
    description_raw: str = Field(..., description="Unmodified initial scraped payload text block.")

class JobListingDTO(JobListingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id_raw: str
    description_raw: str
    description_clean: Optional[str] = None
    date_scraped: datetime