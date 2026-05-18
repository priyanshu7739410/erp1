from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.staff import StaffCreate, StaffUpdate, StaffResponse
from app.services.staff_service import create_staff, get_staff, list_staff, update_staff, delete_staff
from app.auth.dependencies import RoleChecker
from app.utils.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/staff", tags=["Staff"])
allow_staff = RoleChecker(["admin", "doctor", "receptionist", "nurse"])
require_admin = RoleChecker(["admin"])

@router.post("/", response_model=StaffResponse, dependencies=[Depends(require_admin)])
def create_new_staff(data: StaffCreate, db: Session = Depends(get_db)):
    return create_staff(db, data)

@router.get("/", response_model=PaginatedResponse[StaffResponse], dependencies=[Depends(allow_staff)])
def get_staff_endpoint(
    role: Optional[str] = None,
    department_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_staff(db, role=role, department_id=department_id, page=page, size=size)

@router.get("/{staff_id}", response_model=StaffResponse, dependencies=[Depends(allow_staff)])
def get_single_staff(staff_id: int, db: Session = Depends(get_db)):
    return get_staff(db, staff_id)

@router.put("/{staff_id}", response_model=StaffResponse, dependencies=[Depends(require_admin)])
def update_existing_staff(staff_id: int, data: StaffUpdate, db: Session = Depends(get_db)):
    return update_staff(db, staff_id, data)

@router.delete("/{staff_id}", dependencies=[Depends(require_admin)])
def remove_staff(staff_id: int, db: Session = Depends(get_db)):
    delete_staff(db, staff_id)
    return {"message": "Staff member deactivated successfully"}
