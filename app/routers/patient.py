from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.services.patient_service import (
    create_patient,
    get_patient,
    update_patient,
    delete_patient,
    search_patients
)
from app.auth.dependencies import get_current_active_user, RoleChecker
from app.utils.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/patients", tags=["Patients"])
allow_staff = RoleChecker(["admin", "doctor", "receptionist", "nurse"])

@router.post("/", response_model=PatientResponse, dependencies=[Depends(allow_staff)])
def create_new_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    return create_patient(db, patient)

@router.get("/search", response_model=PaginatedResponse[PatientResponse], dependencies=[Depends(allow_staff)])
def search_patients_endpoint(
    q: Optional[str] = Query(None, description="Search by name, email, or phone"),
    is_active: bool = True,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return search_patients(db, query=q, is_active=is_active, page=page, size=size)

@router.get("/{patient_id}", response_model=PatientResponse, dependencies=[Depends(allow_staff)])
def get_single_patient(patient_id: int, db: Session = Depends(get_db)):
    return get_patient(db, patient_id)

@router.put("/{patient_id}", response_model=PatientResponse, dependencies=[Depends(allow_staff)])
def update_existing_patient(patient_id: int, update_data: PatientUpdate, db: Session = Depends(get_db)):
    return update_patient(db, patient_id, update_data)

@router.delete("/{patient_id}", dependencies=[Depends(RoleChecker(["admin", "doctor", "receptionist"]))])
def remove_patient(patient_id: int, db: Session = Depends(get_db)):
    delete_patient(db, patient_id)
    return {"message": "Patient deactivated successfully"}