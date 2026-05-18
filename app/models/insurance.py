from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    provider_name = Column(String, nullable=False, index=True)
    policy_number = Column(String, unique=True, nullable=False, index=True)
    group_number = Column(String, nullable=True)
    deductible = Column(Float, default=0.0)
    co_pay = Column(Float, default=0.0) # percentage or fixed
    coverage_summary = Column(String, nullable=True) # raw text or parsed
    network_status = Column(String, default="in-network") # in-network, out-of-network
    exclusions = Column(String, nullable=True) # comma separated terms
    is_active = Column(Boolean, default=True)

class CoverageReview(Base):
    __tablename__ = "coverage_reviews"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False, index=True)
    insurance_policy_id = Column(Integer, ForeignKey("insurance_policies.id"), nullable=False, index=True)
    review_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="approved") # approved, flagged, denied
    coverage_issue = Column(String, nullable=True) # reason if flagged/denied
    recommended_actions = Column(String, nullable=True)
    estimated_patient_cost = Column(Float, default=0.0)
