from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TaskCreate(BaseModel):
    email: EmailStr
    requirement_text: str = Field(min_length=3)
    schedule: str = Field(description="e.g. daily 07:00 or weekly Monday 08:00")
    timezone: str = Field(default="UTC")
    preferred_report_language: str = Field(default="en")


class TaskUpdate(BaseModel):
    requirement_text: str | None = None
    schedule: str | None = None
    timezone: str | None = None
    preferred_report_language: str | None = None
    is_active: bool | None = None


class TaskRead(BaseModel):
    id: int
    user_email: EmailStr
    requirement_text: str
    schedule_type: str
    schedule_time: str
    schedule_day_of_week: int | None
    timezone: str
    preferred_report_language: str
    is_active: bool
    last_run_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RunNowResponse(BaseModel):
    run_id: int
    report_id: int | None
    status: str
