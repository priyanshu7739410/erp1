from sqlalchemy.orm import Session
from app.models.medical_record import MedicalRecord
from app.models.appointment import Appointment
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate
from app.utils.exceptions import NotFoundException
from app.utils.pagination import paginate

def create_medical_record(db: Session, data: MedicalRecordCreate) -> MedicalRecord:
    record = MedicalRecord(**data.model_dump())
    db.add(record)
    
    # If linked to an appointment, complete the appointment
    if data.appointment_id:
        appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
        if appt:
            appt.status = "completed"
            
    db.commit()
    db.refresh(record)
    return record

def get_medical_record(db: Session, record_id: int) -> MedicalRecord:
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise NotFoundException(detail="Medical record not found")
    return record

def list_medical_records(
    db: Session, patient_id: int = None, doctor_id: int = None, page: int = 1, size: int = 10
) -> dict:
    query = db.query(MedicalRecord)
    if patient_id is not None:
        query = query.filter(MedicalRecord.patient_id == patient_id)
    if doctor_id is not None:
        query = query.filter(MedicalRecord.doctor_id == doctor_id)
    return paginate(query.order_by(MedicalRecord.created_at.desc()), page, size)

def update_medical_record(db: Session, record_id: int, data: MedicalRecordUpdate) -> MedicalRecord:
    record = get_medical_record(db, record_id)
    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record
