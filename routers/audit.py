import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from main import get_db, get_current_user, verify_model_access, DBUser, DBAuditLogEntry

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("/{model_id}", summary="Fetch governance audit log entries")
def get_audit_logs(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns structured audit entries.
    """
    model = verify_model_access(db, current_user, model_id)
    logs = db.query(DBAuditLogEntry)\
             .filter(DBAuditLogEntry.model_id == model_id, DBAuditLogEntry.project_id == model.project_id)\
             .order_by(DBAuditLogEntry.timestamp.desc())\
             .all()
             
    if not logs:
        return []

    return [{
        "timestamp": log.timestamp.isoformat(),
        "event_type": log.event_type,
        "model_id": log.model_id,
        "model_version": log.model_version,
        "drift_score": log.drift_score,
        "triggered_by": log.triggered_by,
        "details": json.loads(log.details_json)
    } for log in logs]
