from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.audit import AuditLogResponse
from app.services.audit_service import list_audit_logs
from app.auth.dependencies import RoleChecker
from app.utils.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/audit", tags=["Audit Logs"])
require_admin = RoleChecker(["admin"])

@router.get("/", response_model=PaginatedResponse[AuditLogResponse], dependencies=[Depends(require_admin)])
def get_audit_logs(
    entity_name: Optional[str] = None,
    action: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_audit_logs(db, entity_name=entity_name, action=action, page=page, size=size)
