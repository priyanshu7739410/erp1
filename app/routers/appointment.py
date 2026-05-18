from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.services.appointment_service import (
    create_appointment,
    get_appointment,
    list_appointments,
    update_appointment,
    cancel_appointment
)
from app.auth.dependencies import RoleChecker
from app.utils.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/appointments", tags=["Appointments"])
allow_staff = RoleChecker(["admin", "doctor", "receptionist", "nurse"])

@router.post("/", response_model=AppointmentResponse, dependencies=[Depends(allow_staff)])
def book_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    return create_appointment(db, data)

@router.get("/", response_model=PaginatedResponse[AppointmentResponse], dependencies=[Depends(allow_staff)])
def get_appointments_endpoint(
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    date: Optional[str] = Query(None, description="Filter by date YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_appointments(db, doctor_id=doctor_id, patient_id=patient_id, date_str=date, page=page, size=size)

@router.get("/{appt_id}", response_model=AppointmentResponse, dependencies=[Depends(allow_staff)])
def get_single_appointment(appt_id: int, db: Session = Depends(get_db)):
    return get_appointment(db, appt_id)

@router.put("/{appt_id}", response_model=AppointmentResponse, dependencies=[Depends(allow_staff)])
def modify_appointment(appt_id: int, data: AppointmentUpdate, db: Session = Depends(get_db)):
    return update_appointment(db, appt_id, data)

@router.delete("/{appt_id}", response_model=AppointmentResponse, dependencies=[Depends(allow_staff)])
def cancel_appointment_endpoint(appt_id: int, db: Session = Depends(get_db)):
    return cancel_appointment(db, appt_id)
