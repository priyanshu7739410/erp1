from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditLogResponse(BaseModel):
    id: int
    entity_name: str
    entity_id: int
    action: str
    changes: Optional[str] = None
    performed_by: str
    timestamp: datetime

    class Config:
        from_attributes = True
