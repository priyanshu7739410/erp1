from pydantic import BaseModel, EmailStr
from typing import Optional

class DoctorCreate(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    license_number: str
    phone: str
    email: EmailStr
    department_id: Optional[int] = None

class DoctorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialty: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None

class DoctorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    specialty: str
    license_number: str
    phone: str
    email: str
    department_id: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True
