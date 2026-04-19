from pydantic import BaseModel
from datetime import datetime


class CVResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    requirements: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluateRequest(BaseModel):
    cv_id: int
    job_id: int


class ExtractedData(BaseModel):
    name: str
    email: str
    phone: str
    years_experience: int
    education: list[str]
    skills: list[str]
    languages: list[str]
    previous_positions: list[str]


class EvaluationResponse(BaseModel):
    id: int
    cv_id: int
    job_id: int
    score: float
    feedback: str
    extracted_data: str
    created_at: datetime
    cv_filename: str | None = None
    job_title: str | None = None

    model_config = {"from_attributes": True}
