import time
import json
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from driftguard.alert import send_alert
from main import (
    get_db, get_current_user, verify_model_access, DBModel, DBProject, DBPredictionLog, DBAuditLogEntry,
    DBUser, PredictTelemetryRequest, predictions_counter, drift_gauge, latency_histogram
)

router = APIRouter(tags=["Telemetry"])

@router.post("/predict/{model_id}", summary="Log model telemetry and execute ADWIN tracking")
def log_prediction(model_id: str, req: PredictTelemetryRequest, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Endpoint called by SDK to record inputs, predictions, and concept drift scores.
    Updates active Prometheus scrapers.
    """
    model = verify_model_access(db, current_user, model_id, allow_missing=True)
    if not model:
        raise HTTPException(status_code=404, detail="Model must be registered before telemetry.")

    log_entry = DBPredictionLog(
        project_id=model.project_id,
        model_id=model_id,
        features_json=json.dumps(req.features),
        prediction_json=json.dumps(req.prediction),
        drift_score=req.drift_score
    )
    t0 = time.time()
    db_commit_latency_seconds = 0.0
    try:
        db.add(log_entry)
        db.commit()
    except Exception as db_err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database write failed: {db_err}")
    finally:
        db_commit_latency_seconds = time.time() - t0

    predictions_counter.labels(model_id=model_id).inc()

    for i in range(len(req.features)):
        drift_gauge.labels(model_id=model_id, feature_index=str(i)).set(req.drift_score)

    latency_histogram.labels(model_id=model_id).observe(db_commit_latency_seconds)

    if req.drift_score > model.drift_threshold and model.status != "retraining":
        model.status = "degraded"
        db.commit()
        
        audit = DBAuditLogEntry(
            project_id=model.project_id,
            model_id=model_id,
            event_type="drift_detected",
            model_version=model.version,
            drift_score=req.drift_score,
            triggered_by="automatic",
            details_json=json.dumps({"message": f"Real-time drift score {req.drift_score:.4f} exceeded threshold {model.drift_threshold}."})
        )
        db.add(audit)
        db.commit()

        send_alert(
            event_type="drift_detected",
            message=f"Concept drift detected on model '{model_id}'!",
            details={
                "model_id": model_id,
                "version": model.version,
                "current_drift_score": f"{req.drift_score:.4f}",
                "threshold": f"{model.drift_threshold}"
            }
        )

    return {"status": "logged", "drift_score": req.drift_score}

@router.get("/drift/{model_id}", summary="Fetch active drift metrics of a model")
def get_drift_metrics(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Fetches drift metrics history for Recharts visualization.
    """
    model = verify_model_access(db, current_user, model_id)
    logs = db.query(DBPredictionLog)\
             .filter(DBPredictionLog.model_id == model_id, DBPredictionLog.project_id == model.project_id)\
             .order_by(DBPredictionLog.timestamp.desc())\
             .limit(500)\
             .all()
             
    if not logs:
        return []

    return [{
        "timestamp": log.timestamp.isoformat(),
        "drift_score": log.drift_score,
        "features": json.loads(log.features_json),
        "prediction": json.loads(log.prediction_json)
    } for log in reversed(logs)]
