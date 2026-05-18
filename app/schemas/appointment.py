from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    status: str
    reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
