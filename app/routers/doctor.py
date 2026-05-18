from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse
from app.services.doctor_service import create_doctor, get_doctor, list_doctors, update_doctor, delete_doctor
from app.auth.dependencies import RoleChecker
from app.utils.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/doctors", tags=["Doctors"])
allow_staff = RoleChecker(["admin", "doctor", "receptionist", "nurse"])
require_admin = RoleChecker(["admin"])

@router.post("/", response_model=DoctorResponse, dependencies=[Depends(require_admin)])
def create_new_doctor(data: DoctorCreate, db: Session = Depends(get_db)):
    return create_doctor(db, data)

@router.get("/", response_model=PaginatedResponse[DoctorResponse], dependencies=[Depends(allow_staff)])
def get_doctors_endpoint(
    specialty: Optional[str] = None,
    department_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_doctors(db, specialty=specialty, department_id=department_id, page=page, size=size)

@router.get("/{doc_id}", response_model=DoctorResponse, dependencies=[Depends(allow_staff)])
def get_single_doctor(doc_id: int, db: Session = Depends(get_db)):
    return get_doctor(db, doc_id)

@router.put("/{doc_id}", response_model=DoctorResponse, dependencies=[Depends(require_admin)])
def update_existing_doctor(doc_id: int, data: DoctorUpdate, db: Session = Depends(get_db)):
    return update_doctor(db, doc_id, data)

@router.delete("/{doc_id}", dependencies=[Depends(require_admin)])
def remove_doctor(doc_id: int, db: Session = Depends(get_db)):
    delete_doctor(db, doc_id)
    return {"message": "Doctor deactivated successfully"}
