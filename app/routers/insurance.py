from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.insurance import (
    InsurancePolicyCreate,
    InsurancePolicyUpdate,
    InsurancePolicyResponse,
    PolicyTextUpload,
    CoverageReviewResponse
)
from app.services.insurance_service import (
    create_policy,
    extract_policy_from_text,
    get_policy,
    list_policies,
    validate_appointment_coverage,
    list_coverage_reviews
)
from app.auth.dependencies import RoleChecker
from app.utils.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/insurance", tags=["Insurance"])
allow_staff = RoleChecker(["admin", "receptionist", "doctor", "nurse", "billing_officer"])

@router.post("/policies", response_model=InsurancePolicyResponse, dependencies=[Depends(allow_staff)])
def add_policy(data: InsurancePolicyCreate, db: Session = Depends(get_db)):
    return create_policy(db, data)

@router.post("/policies/upload-text", response_model=InsurancePolicyResponse, dependencies=[Depends(allow_staff)])
def upload_policy_text(data: PolicyTextUpload, db: Session = Depends(get_db)):
    return extract_policy_from_text(db, data.patient_id, data.policy_text)

@router.get("/policies", response_model=PaginatedResponse[InsurancePolicyResponse], dependencies=[Depends(allow_staff)])
def get_policies(
    patient_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_policies(db, patient_id=patient_id, page=page, size=size)

@router.get("/policies/{policy_id}", response_model=InsurancePolicyResponse, dependencies=[Depends(allow_staff)])
def get_single_policy(policy_id: int, db: Session = Depends(get_db)):
    return get_policy(db, policy_id)

@router.post("/coverage-checks/{appointment_id}", response_model=CoverageReviewResponse, dependencies=[Depends(allow_staff)])
def run_coverage_check(appointment_id: int, db: Session = Depends(get_db)):
    return validate_appointment_coverage(db, appointment_id)

@router.get("/coverage-warnings", response_model=PaginatedResponse[CoverageReviewResponse], dependencies=[Depends(allow_staff)])
def get_coverage_warnings(
    patient_id: Optional[int] = None,
    status: Optional[str] = Query("flagged", description="Filter by status: approved, flagged, denied"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_coverage_reviews(db, patient_id=patient_id, status=status, page=page, size=size)
