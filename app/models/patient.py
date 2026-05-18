from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database.session import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    age = Column(Integer)
    gender = Column(String)
    phone = Column(String, index=True)
    address = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    insurance_provider = Column(String, nullable=True)
    medical_history_summary = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)