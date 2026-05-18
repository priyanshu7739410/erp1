from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.utils.pagination import paginate

def log_audit_event(
    db: Session, entity_name: str, entity_id: int, action: str, changes: str, performed_by: str
) -> AuditLog:
    log_entry = AuditLog(
        entity_name=entity_name,
        entity_id=entity_id,
        action=action,
        changes=changes,
        performed_by=performed_by
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry

def list_audit_logs(db: Session, entity_name: str = None, action: str = None, page: int = 1, size: int = 10) -> dict:
    query = db.query(AuditLog)
    if entity_name:
        query = query.filter(AuditLog.entity_name == entity_name)
    if action:
        query = query.filter(AuditLog.action == action)
    return paginate(query.order_by(AuditLog.timestamp.desc()), page, size)
