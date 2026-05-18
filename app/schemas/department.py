from pydantic import BaseModel
from typing import Optional

class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
