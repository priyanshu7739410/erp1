from sqlalchemy.orm import Session
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate
from app.utils.exceptions import NotFoundException, ConflictException
from app.utils.pagination import paginate

def create_staff(db: Session, data: StaffCreate) -> Staff:
    existing = db.query(Staff).filter(
        (Staff.employee_id == data.employee_id) | (Staff.email == data.email)
    ).first()
    if existing:
        raise ConflictException(detail="Staff member with this employee ID or email already exists")
    staff = Staff(**data.model_dump(), is_active=True)
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff

def get_staff(db: Session, staff_id: int) -> Staff:
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise NotFoundException(detail="Staff member not found")
    return staff

def list_staff(db: Session, role: str = None, department_id: int = None, page: int = 1, size: int = 10) -> dict:
    query = db.query(Staff).filter(Staff.is_active == True)
    if role:
        query = query.filter(Staff.role.ilike(f"%{role}%"))
    if department_id is not None:
        query = query.filter(Staff.department_id == department_id)
    return paginate(query, page, size)

def update_staff(db: Session, staff_id: int, data: StaffUpdate) -> Staff:
    staff = get_staff(db, staff_id)
    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(staff, key, value)
    db.commit()
    db.refresh(staff)
    return staff

def delete_staff(db: Session, staff_id: int) -> Staff:
    staff = get_staff(db, staff_id)
    staff.is_active = False
    db.commit()
    db.refresh(staff)
    return staff
