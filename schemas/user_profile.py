from typing import List, Optional
from pydantic import BaseModel, Field

class ParsedProfileDTO(BaseModel):
    full_name: Optional[str] = Field(None, description="Candidate full name")
    target_roles: List[str] = Field(default_factory=list, description="Extracted target job titles")
    key_skills: List[str] = Field(default_factory=list, description="Extracted technical and domain skills")
    education: List[str] = Field(default_factory=list, description="Degrees, certifications, and institutions")
    total_experience_years: Optional[float] = Field(0.0, description="Estimated total experience in years")
    experience_highlights: List[str] = Field(default_factory=list, description="Notable past accomplishments")
    recommended_search_queries: List[str] = Field(default_factory=list, description="AI-generated search queries based on skills")