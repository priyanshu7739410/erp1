from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.utils.exceptions import NotFoundException
from app.utils.pagination import paginate

def create_patient(db: Session, patient: PatientCreate) -> Patient:
    new_patient = Patient(
        name=patient.name,
        email=patient.email,
        age=patient.age,
        gender=patient.gender,
        phone=patient.phone,
        address=patient.address,
        emergency_contact=patient.emergency_contact,
        insurance_provider=patient.insurance_provider,
        medical_history_summary=patient.medical_history_summary,
        is_active=True
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

def get_patient(db: Session, patient_id: int) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise NotFoundException(detail="Patient not found")
    return patient

def search_patients(db: Session, query: str = None, is_active: bool = True, page: int = 1, size: int = 10) -> dict:
    db_query = db.query(Patient)
    if is_active is not None:
        db_query = db_query.filter(Patient.is_active == is_active)
    if query:
        db_query = db_query.filter(
            (Patient.name.ilike(f"%{query}%")) |
            (Patient.email.ilike(f"%{query}%")) |
            (Patient.phone.ilike(f"%{query}%"))
        )
    return paginate(db_query, page, size)

def update_patient(db: Session, patient_id: int, update_data: PatientUpdate) -> Patient:
    patient = get_patient(db, patient_id)
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(db: Session, patient_id: int) -> Patient:
    patient = get_patient(db, patient_id)
    patient.is_active = False
    db.commit()
    db.refresh(patient)
    return patient