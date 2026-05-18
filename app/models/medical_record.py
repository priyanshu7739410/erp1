from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database.session import Base

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True, index=True)
    notes = Column(String, nullable=True)
    diagnosis = Column(String, nullable=False)
    treatment_plan = Column(String, nullable=True)
    documents = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
