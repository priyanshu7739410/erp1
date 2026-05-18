from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MedicalRecordCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    notes: Optional[str] = None
    diagnosis: str
    treatment_plan: Optional[str] = None
    documents: Optional[str] = None

class MedicalRecordUpdate(BaseModel):
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    documents: Optional[str] = None

class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    notes: Optional[str] = None
    diagnosis: str
    treatment_plan: Optional[str] = None
    documents: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
