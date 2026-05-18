from sqlalchemy.orm import Session
from app.models.department import Department
from app.schemas.department import DepartmentCreate
from app.utils.exceptions import NotFoundException, ConflictException
from typing import List

def create_department(db: Session, data: DepartmentCreate) -> Department:
    existing = db.query(Department).filter(Department.name == data.name).first()
    if existing:
        raise ConflictException(detail="Department with this name already exists")
    dept = Department(name=data.name, description=data.description)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

def get_department(db: Session, dept_id: int) -> Department:
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise NotFoundException(detail="Department not found")
    return dept

def get_all_departments(db: Session) -> List[Department]:
    return db.query(Department).all()
