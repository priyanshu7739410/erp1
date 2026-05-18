from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.utils.exceptions import NotFoundException, ConflictException, BadRequestException
from app.utils.pagination import paginate
from datetime import datetime

def create_appointment(db: Session, data: AppointmentCreate) -> Appointment:
    if data.scheduled_start >= data.scheduled_end:
        raise BadRequestException(detail="Scheduled end time must be after start time")
    
    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id, Doctor.is_active == True).first()
    if not doctor:
        raise NotFoundException(detail="Active doctor not found")
        
    patient = db.query(Patient).filter(Patient.id == data.patient_id, Patient.is_active == True).first()
    if not patient:
        raise NotFoundException(detail="Active patient not found")
    
    # Overlap check
    overlapping = db.query(Appointment).filter(
        Appointment.doctor_id == data.doctor_id,
        Appointment.status != "cancelled",
        Appointment.scheduled_start < data.scheduled_end,
        Appointment.scheduled_end > data.scheduled_start
    ).first()
    if overlapping:
        raise ConflictException(detail="Doctor already has an appointment during this time window")
    
    # Daily maximum check (e.g. max 16 appointments per day)
    day_start = data.scheduled_start.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = data.scheduled_start.replace(hour=23, minute=59, second=59, microsecond=999999)
    daily_count = db.query(Appointment).filter(
        Appointment.doctor_id == data.doctor_id,
        Appointment.status != "cancelled",
        Appointment.scheduled_start >= day_start,
        Appointment.scheduled_start <= day_end
    ).count()
    if daily_count >= 16:
        raise ConflictException(detail="Doctor has reached maximum appointment capacity for this day")
        
    appt = Appointment(**data.model_dump(), status="scheduled")
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt

def get_appointment(db: Session, appt_id: int) -> Appointment:
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        raise NotFoundException(detail="Appointment not found")
    return appt

def list_appointments(
    db: Session, doctor_id: int = None, patient_id: int = None, date_str: str = None, page: int = 1, size: int = 10
) -> dict:
    query = db.query(Appointment)
    if doctor_id is not None:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        query = query.filter(Appointment.patient_id == patient_id)
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            day_start = target_date.replace(hour=0, minute=0, second=0)
            day_end = target_date.replace(hour=23, minute=59, second=59)
            query = query.filter(Appointment.scheduled_start >= day_start, Appointment.scheduled_start <= day_end)
        except ValueError:
            raise BadRequestException(detail="Date must be in YYYY-MM-DD format")
    return paginate(query, page, size)

def update_appointment(db: Session, appt_id: int, data: AppointmentUpdate) -> Appointment:
    appt = get_appointment(db, appt_id)
    
    if data.scheduled_start or data.scheduled_end:
        new_start = data.scheduled_start or appt.scheduled_start
        new_end = data.scheduled_end or appt.scheduled_end
        if new_start >= new_end:
            raise BadRequestException(detail="Scheduled end time must be after start time")
        
        overlapping = db.query(Appointment).filter(
            Appointment.id != appt_id,
            Appointment.doctor_id == appt.doctor_id,
            Appointment.status != "cancelled",
            Appointment.scheduled_start < new_end,
            Appointment.scheduled_end > new_start
        ).first()
        if overlapping:
            raise ConflictException(detail="Doctor already has an appointment during this time window")
            
    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(appt, key, value)
    db.commit()
    db.refresh(appt)
    return appt

def cancel_appointment(db: Session, appt_id: int) -> Appointment:
    appt = get_appointment(db, appt_id)
    appt.status = "cancelled"
    db.commit()
    db.refresh(appt)
    return appt
