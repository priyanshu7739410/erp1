from pydantic import BaseModel, EmailStr
from typing import Optional

class StaffCreate(BaseModel):
    first_name: str
    last_name: str
    role: str
    employee_id: str
    phone: str
    email: EmailStr
    department_id: Optional[int] = None
    salary: Optional[float] = None
    shift_time: Optional[str] = "day"

class StaffUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None
    salary: Optional[float] = None
    shift_time: Optional[str] = None

class StaffResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: str
    employee_id: str
    phone: str
    email: str
    department_id: Optional[int] = None
    is_active: bool
    salary: Optional[float] = None
    shift_time: Optional[str] = "day"


    class Config:
        from_attributes = True
