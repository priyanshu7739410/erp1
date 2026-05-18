from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class InsurancePolicyCreate(BaseModel):
    patient_id: int
    provider_name: str
    policy_number: str
    group_number: Optional[str] = None
    deductible: float = 0.0
    co_pay: float = 0.0
    coverage_summary: Optional[str] = None
    network_status: str = "in-network"
    exclusions: Optional[str] = None

class InsurancePolicyUpdate(BaseModel):
    provider_name: Optional[str] = None
    group_number: Optional[str] = None
    deductible: Optional[float] = None
    co_pay: Optional[float] = None
    coverage_summary: Optional[str] = None
    network_status: Optional[str] = None
    exclusions: Optional[str] = None
    is_active: Optional[bool] = None

class InsurancePolicyResponse(BaseModel):
    id: int
    patient_id: int
    provider_name: str
    policy_number: str
    group_number: Optional[str] = None
    deductible: float
    co_pay: float
    coverage_summary: Optional[str] = None
    network_status: str
    exclusions: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class PolicyTextUpload(BaseModel):
    patient_id: int
    policy_text: str

class CoverageReviewResponse(BaseModel):
    id: int
    patient_id: int
    appointment_id: int
    insurance_policy_id: int
    review_date: datetime
    status: str
    coverage_issue: Optional[str] = None
    recommended_actions: Optional[str] = None
    estimated_patient_cost: float

    class Config:
        from_attributes = True
