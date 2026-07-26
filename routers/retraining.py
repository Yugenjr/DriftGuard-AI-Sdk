import os
import json
import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from driftguard.alert import send_alert
from main import (
    get_db, get_current_user, verify_model_access, check_and_recover_all_stale_jobs_for_user,
    run_retraining_process, DBModel, DBModelVersion, DBRetrainingEvent, DBAuditLogEntry, DBUser,
    RetrainTriggerRequest, RetrainCompleteRequest, retrain_counter, accuracy_gauge
)

router = APIRouter(tags=["Retraining"])

@router.post("/retrain/{model_id}", summary="Triggers retraining flow process asynchronously")
def trigger_retraining(model_id: str, req: RetrainTriggerRequest, background_tasks: BackgroundTasks, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Main trigger endpoint. Creates a retraining event record.
    """
    check_and_recover_all_stale_jobs_for_user(current_user.id, db)

    models = db.query(DBModel).filter(
        DBModel.model_id == model_id
    ).with_for_update().all()
    if not models:
        raise HTTPException(status_code=404, detail="Model not registered.")
    model = next((m for m in models if m.owner_id == current_user.id), None)
    if not model:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this model.")

    if model.status == "retraining":
        return {"status": "already_running", "message": "Retraining is currently running."}

    model.status = "retraining"
    db.commit()

    event = DBRetrainingEvent(
        project_id=model.project_id,
        model_id=model_id,
        status="running",
        triggered_by=req.triggered_by,
        old_accuracy=model.accuracy,
        old_version=model.version,
        last_heartbeat=datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
    )
    db.add(event)
    db.commit()

    retrain_counter.labels(model_id=model_id, triggered_by=req.triggered_by).inc()

    if req.source == "sdk_callback":
        return {
            "status": "recorded",
            "event_id": event.id,
            "message": "Event recorded. SDK callback pipeline will report results via /complete.",
        }

    if model.retrain_webhook_url:
        import httpx
        def fire_webhook():
            try:
                payload = {
                    "event_id": event.id,
                    "model_id": model_id,
                    "drift_score": req.drift_score,
                    "callback_url": f"http://localhost:8000/retrain/{model_id}/complete"
                }
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(model.retrain_webhook_url, json=payload)
            except Exception:
                pass
    
        background_tasks.add_task(fire_webhook)
        return {"status": "triggered_webhook", "event_id": event.id, "message": "Webhook fired to orchestrator."}

    background_tasks.add_task(
        run_retraining_process,
        model_id=model_id,
        event_id=event.id,
        drift_score=req.drift_score,
        triggered_by=req.triggered_by
    )

    return {"status": "triggered", "event_id": event.id, "message": "Retraining initiated in background task."}

@router.post("/retrain/{model_id}/complete", summary="SDK callback pipeline reports its results")
def complete_retraining(model_id: str, req: RetrainCompleteRequest, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Called exclusively by the SDK's ``RetrainerCallbackRunner`` after its local pipeline finishes.
    """
    model = verify_model_access(db, current_user, model_id)

    event = None
    if req.event_id:
        event = db.query(DBRetrainingEvent).filter(
            DBRetrainingEvent.id == req.event_id,
            DBRetrainingEvent.project_id == model.project_id
        ).first()
    if event is None:
        event = (
            db.query(DBRetrainingEvent)
            .filter(
                DBRetrainingEvent.model_id == model_id,
                DBRetrainingEvent.project_id == model.project_id,
                DBRetrainingEvent.status == "running",
            )
            .order_by(DBRetrainingEvent.start_time.desc())
            .first()
        )

    if req.validation_passed and req.new_version and req.new_accuracy is not None:
        old_version = model.version
        old_accuracy = req.old_accuracy if req.old_accuracy is not None else model.accuracy

        model.status = "healthy"
        model.accuracy = req.new_accuracy
        model.version = req.new_version

        db.query(DBModelVersion).filter(
            DBModelVersion.model_id == model_id,
            DBModelVersion.project_id == model.project_id,
            DBModelVersion.status == "champion"
        ).update({"status": "archived"})

        db.query(DBModelVersion).filter(
            DBModelVersion.model_id == model_id,
            DBModelVersion.project_id == model.project_id,
            DBModelVersion.status == "candidate"
        ).delete(synchronize_session=False)

        new_version_rec = DBModelVersion(
            project_id=model.project_id,
            model_id=model_id,
            version=req.new_version,
            status="champion",
            accuracy=req.new_accuracy
        )
        db.add(new_version_rec)

        if event:
            event.status = "completed"
            event.end_time = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
            event.new_accuracy = req.new_accuracy
            event.old_accuracy = req.old_accuracy if req.old_accuracy is not None else event.old_accuracy
            event.new_version = req.new_version
            event.details_json = json.dumps(
                {"message": "Promoted by SDK callback pipeline.", "source": "sdk_callback"}
            )

        db.add(DBAuditLogEntry(
            project_id=model.project_id,
            model_id=model_id,
            event_type="model_promoted",
            model_version=req.new_version,
            drift_score=0.0,
            triggered_by="automatic",
            details_json=json.dumps({
                "message": f"SDK callback challenger {req.new_version} promoted. Accuracy {old_accuracy:.4f} → {req.new_accuracy:.4f}.",
                "source": "sdk_callback",
                "old_version": old_version,
                "new_version": req.new_version,
                "old_accuracy": old_accuracy,
                "new_accuracy": req.new_accuracy,
            })
        ))
        db.commit()

        accuracy_gauge.labels(model_id=model_id, version=req.new_version).set(req.new_accuracy)

        send_alert(
            event_type="model_promoted",
            message=f"SDK callback: '{model_id}' v{req.new_version} promoted to champion!",
            details={
                "model_id": model_id,
                "old_version": old_version,
                "new_version": req.new_version,
                "old_accuracy": f"{old_accuracy:.4f}",
                "new_accuracy": f"{req.new_accuracy:.4f}",
                "source": "sdk_callback",
            },
        )

        return {
            "status": "promoted",
            "model_id": model_id,
            "new_version": req.new_version,
            "new_accuracy": req.new_accuracy,
        }

    else:
        model.status = "healthy"

        db.query(DBModelVersion).filter(
            DBModelVersion.model_id == model_id,
            DBModelVersion.project_id == model.project_id,
            DBModelVersion.status == "candidate"
        ).delete(synchronize_session=False)

        if event:
            event.status = "failed"
            event.end_time = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
            event.new_accuracy = req.new_accuracy
            event.old_accuracy = req.old_accuracy if req.old_accuracy is not None else event.old_accuracy
            event.details_json = json.dumps(
                {"error": req.error or "Challenger did not pass validation.", "source": "sdk_callback"}
            )

        db.add(DBAuditLogEntry(
            project_id=model.project_id,
            model_id=model_id,
            event_type="validation_failed",
            model_version=model.version,
            drift_score=0.0,
            triggered_by="automatic",
            details_json=json.dumps(
                {"error": req.error or "Challenger did not pass validation.", "source": "sdk_callback"}
            ),
        ))
        db.commit()

        send_alert(
            event_type="validation_failed",
            message=f"SDK callback: challenger for '{model_id}' rejected. Champion retained.",
            details={"model_id": model_id, "reason": req.error or "N/A", "source": "sdk_callback"},
        )

        return {
            "status": "rejected",
            "model_id": model_id,
            "reason": req.error or "Challenger did not pass validation.",
        }

@router.get("/retraining/history/{model_id}", summary="Get retraining events timeline")
def get_retraining_history(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Exposes full retraining executions details.
    """
    model = verify_model_access(db, current_user, model_id)
    events = db.query(DBRetrainingEvent)\
               .filter(DBRetrainingEvent.model_id == model_id, DBRetrainingEvent.project_id == model.project_id)\
               .order_by(DBRetrainingEvent.start_time.desc())\
               .all()
    if not events:
        return []

    return [{
        "id": e.id,
        "model_id": e.model_id,
        "status": e.status,
        "triggered_by": e.triggered_by,
        "start_time": e.start_time.isoformat(),
        "end_time": e.end_time.isoformat() if e.end_time else None,
        "old_accuracy": e.old_accuracy,
        "new_accuracy": e.new_accuracy,
        "old_version": e.old_version,
        "new_version": e.new_version,
        "details": json.loads(e.details_json)
    } for e in events]
