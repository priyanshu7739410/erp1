from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class PatientCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    age: int
    gender: str
    phone: str
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_provider: Optional[str] = None
    medical_history_summary: Optional[str] = None

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_provider: Optional[str] = None
    medical_history_summary: Optional[str] = None
    is_active: Optional[bool] = None

class PatientResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    age: int
    gender: str
    phone: str
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_provider: Optional[str] = None
    medical_history_summary: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True