from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse
from app.services.medical_record_service import (
    create_medical_record,
    get_medical_record,
    list_medical_records,
    update_medical_record
)
from app.auth.dependencies import RoleChecker
from app.utils.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/medical-records", tags=["Medical Records"])
allow_staff = RoleChecker(["admin", "doctor", "nurse"])

@router.post("/", response_model=MedicalRecordResponse, dependencies=[Depends(allow_staff)])
def create_record(data: MedicalRecordCreate, db: Session = Depends(get_db)):
    return create_medical_record(db, data)

@router.get("/", response_model=PaginatedResponse[MedicalRecordResponse], dependencies=[Depends(RoleChecker(["admin", "doctor", "nurse", "receptionist"]))])
def get_records(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_medical_records(db, patient_id=patient_id, doctor_id=doctor_id, page=page, size=size)

@router.get("/{record_id}", response_model=MedicalRecordResponse, dependencies=[Depends(allow_staff)])
def get_single_record(record_id: int, db: Session = Depends(get_db)):
    return get_medical_record(db, record_id)

@router.put("/{record_id}", response_model=MedicalRecordResponse, dependencies=[Depends(RoleChecker(["admin", "doctor"]))])
def modify_record(record_id: int, data: MedicalRecordUpdate, db: Session = Depends(get_db)):
    return update_medical_record(db, record_id, data)
