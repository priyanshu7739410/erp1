from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.department import DepartmentCreate, DepartmentResponse
from app.services.department_service import create_department, get_department, get_all_departments
from app.auth.dependencies import RoleChecker

router = APIRouter(prefix="/api/v1/departments", tags=["Departments"])
allow_all_staff = RoleChecker(["admin", "doctor", "receptionist", "nurse"])
require_admin = RoleChecker(["admin"])

@router.post("/", response_model=DepartmentResponse, dependencies=[Depends(require_admin)])
def create_new_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    return create_department(db, data)

@router.get("/", response_model=List[DepartmentResponse], dependencies=[Depends(allow_all_staff)])
def list_departments(db: Session = Depends(get_db)):
    return get_all_departments(db)

@router.get("/{dept_id}", response_model=DepartmentResponse, dependencies=[Depends(allow_all_staff)])
def get_single_department(dept_id: int, db: Session = Depends(get_db)):
    return get_department(db, dept_id)
