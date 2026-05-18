from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String, nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String, nullable=False) # CREATE, UPDATE, DELETE
    changes = Column(String, nullable=True) # JSON summary of changes
    performed_by = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
