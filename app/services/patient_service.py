from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate


def create_patient(db: Session, patient: PatientCreate):

    new_patient = Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        phone=patient.phone
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


def get_patient(db: Session, patient_id: int):

    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    return patient


def delete_patient(db: Session, patient_id: int):

    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if patient:
        db.delete(patient)
        db.commit()

    return patient