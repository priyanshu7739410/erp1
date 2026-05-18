from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from app.utils.exceptions import NotFoundException, ConflictException
from app.utils.pagination import paginate

def create_doctor(db: Session, data: DoctorCreate) -> Doctor:
    existing = db.query(Doctor).filter(
        (Doctor.license_number == data.license_number) | (Doctor.email == data.email)
    ).first()
    if existing:
        raise ConflictException(detail="Doctor with this license number or email already exists")
    doc = Doctor(**data.model_dump(), is_active=True)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_doctor(db: Session, doc_id: int) -> Doctor:
    doc = db.query(Doctor).filter(Doctor.id == doc_id).first()
    if not doc:
        raise NotFoundException(detail="Doctor not found")
    return doc

def list_doctors(db: Session, specialty: str = None, department_id: int = None, page: int = 1, size: int = 10) -> dict:
    query = db.query(Doctor).filter(Doctor.is_active == True)
    if specialty:
        query = query.filter(Doctor.specialty.ilike(f"%{specialty}%"))
    if department_id is not None:
        query = query.filter(Doctor.department_id == department_id)
    return paginate(query, page, size)

def update_doctor(db: Session, doc_id: int, data: DoctorUpdate) -> Doctor:
    doc = get_doctor(db, doc_id)
    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(doc, key, value)
    db.commit()
    db.refresh(doc)
    return doc

def delete_doctor(db: Session, doc_id: int) -> Doctor:
    doc = get_doctor(db, doc_id)
    doc.is_active = False
    db.commit()
    db.refresh(doc)
    return doc
