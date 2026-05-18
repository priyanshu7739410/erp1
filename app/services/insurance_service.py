from sqlalchemy.orm import Session
from app.models.insurance import InsurancePolicy, CoverageReview
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.schemas.insurance import InsurancePolicyCreate, InsurancePolicyUpdate
from app.utils.exceptions import NotFoundException, ConflictException, BadRequestException
from app.utils.pagination import paginate
import re

def create_policy(db: Session, data: InsurancePolicyCreate) -> InsurancePolicy:
    existing = db.query(InsurancePolicy).filter(InsurancePolicy.policy_number == data.policy_number).first()
    if existing:
        raise ConflictException(detail="Policy with this number already exists")
    policy = InsurancePolicy(**data.model_dump(), is_active=True)
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy

def extract_policy_from_text(db: Session, patient_id: int, text: str) -> InsurancePolicy:
    # Rule-based NLP extraction pipeline for free policy reading
    provider_match = re.search(r"(?:Provider|Insurance Company|Insurer):\s*([A-Za-z0-9 ]+)", text, re.IGNORECASE)
    policy_match = re.search(r"(?:Policy No|Policy Number|ID):\s*([A-Z0-9-]+)", text, re.IGNORECASE)
    deductible_match = re.search(r"(?:Deductible):\s*\$?(\d+(?:\.\d{2})?)", text, re.IGNORECASE)
    copay_match = re.search(r"(?:Co-pay|Copay):\s*(\d+)%", text, re.IGNORECASE)
    if not copay_match:
        copay_match = re.search(r"(?:Co-pay|Copay):\s*\$?(\d+(?:\.\d{2})?)", text, re.IGNORECASE)
        
    exclusions_match = re.search(r"(?:Exclusions|Not Covered):\s*([^.\n]+)", text, re.IGNORECASE)

    provider_name = provider_match.group(1).strip() if provider_match else "Standard Health Care Inc"
    policy_number = policy_match.group(1).strip() if policy_match else f"POL-{patient_id}-999"
    deductible = float(deductible_match.group(1)) if deductible_match else 500.0
    co_pay = float(copay_match.group(1)) if copay_match else 20.0
    exclusions = exclusions_match.group(1).strip() if exclusions_match else "Cosmetic surgery, Experimental treatments"

    data = InsurancePolicyCreate(
        patient_id=patient_id,
        provider_name=provider_name,
        policy_number=policy_number,
        deductible=deductible,
        co_pay=co_pay,
        coverage_summary=text[:200] + "...",
        network_status="in-network",
        exclusions=exclusions
    )
    return create_policy(db, data)

def get_policy(db: Session, policy_id: int) -> InsurancePolicy:
    policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
    if not policy:
        raise NotFoundException(detail="Insurance policy not found")
    return policy

def list_policies(db: Session, patient_id: int = None, page: int = 1, size: int = 10) -> dict:
    query = db.query(InsurancePolicy)
    if patient_id is not None:
        query = query.filter(InsurancePolicy.patient_id == patient_id)
    return paginate(query.filter(InsurancePolicy.is_active == True), page, size)

def validate_appointment_coverage(db: Session, appointment_id: int) -> CoverageReview:
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise NotFoundException(detail="Appointment not found")
        
    policy = db.query(InsurancePolicy).filter(
        InsurancePolicy.patient_id == appt.patient_id,
        InsurancePolicy.is_active == True
    ).first()
    
    if not policy:
        # No policy found, create a flagged review
        review = CoverageReview(
            patient_id=appt.patient_id,
            appointment_id=appt.id,
            insurance_policy_id=0,
            status="flagged",
            coverage_issue="No active insurance policy found on file for patient",
            recommended_actions="Collect insurance policy details or notify patient of out-of-pocket payment requirement",
            estimated_patient_cost=150.0
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    doctor = db.query(Doctor).filter(Doctor.id == appt.doctor_id).first()
    doc_specialty = doctor.specialty.lower() if doctor else ""
    reason = (appt.reason or "").lower()
    notes = (appt.notes or "").lower()

    exclusions = [e.strip().lower() for e in (policy.exclusions or "").split(",") if e.strip()]
    
    status = "approved"
    issue = "Coverage verified successfully"
    recommended = "Proceed with appointment check-in"
    est_cost = policy.co_pay if policy.co_pay <= 100 else 30.0 # simple co-pay estimate

    # Check network status
    if policy.network_status != "in-network":
        status = "flagged"
        issue = "Insurance provider is out-of-network for this hospital facility"
        recommended = "Notify patient of out-of-network deductible requirements before consultation"
        est_cost = 150.0

    # Check exclusions against reason or notes
    for excl in exclusions:
        if excl in reason or excl in doc_specialty or excl in notes:
            status = "denied"
            issue = f"Treatment category matches insurance policy exclusion: {excl.title()}"
            recommended = "Inform patient that procedure/consultation is excluded from policy coverage. Provide self-pay cost estimates."
            est_cost = 150.0
            break

    review = CoverageReview(
        patient_id=appt.patient_id,
        appointment_id=appt.id,
        insurance_policy_id=policy.id,
        status=status,
        coverage_issue=issue,
        recommended_actions=recommended,
        estimated_patient_cost=est_cost
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

def list_coverage_reviews(db: Session, patient_id: int = None, status: str = None, page: int = 1, size: int = 10) -> dict:
    query = db.query(CoverageReview)
    if patient_id is not None:
        query = query.filter(CoverageReview.patient_id == patient_id)
    if status:
        query = query.filter(CoverageReview.status == status)
    return paginate(query.order_by(CoverageReview.review_date.desc()), page, size)
