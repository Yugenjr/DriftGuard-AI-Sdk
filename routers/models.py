import os
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from driftguard.config import settings
from driftguard.alert import send_alert
from main import (
    get_db, get_current_user, verify_model_access, check_and_recover_all_stale_jobs_for_user,
    DBModel, DBModelVersion, DBPredictionLog, DBRetrainingEvent, DBAuditLogEntry, DBProject, DBUser,
    RegisterModelRequest, ExplicitRegisterModelRequest, WebhookUpdateRequest, RollbackRequest,
    accuracy_gauge
)

router = APIRouter(tags=["Models"])

@router.post("/register", summary="Register a model for platform tracking")
def register_model(req: RegisterModelRequest, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Registers a new model version for automatic tracking and concept drift monitoring.
    """
    proj_id = req.project_id
    if proj_id is None:
        # Fallback to the default project for this user
        project = db.query(DBProject).filter(DBProject.owner_id == current_user.id).first()
        if not project:
            project = DBProject(name="Default Project", owner_id=current_user.id)
            db.add(project)
            db.commit()
            db.refresh(project)
        proj_id = project.id
    else:
        project = db.query(DBProject).filter(DBProject.id == proj_id, DBProject.owner_id == current_user.id).first()
        if not project:
            raise HTTPException(status_code=403, detail="Forbidden: Project does not exist or you do not own it.")

    existing = db.query(DBModel).filter(DBModel.model_id == req.model_id, DBModel.project_id == proj_id).first()
    if existing:
        existing.drift_threshold = req.drift_threshold
        existing.features_json = json.dumps(req.features)
        existing.reference_data_path = req.reference_data_path
        db.commit()
        return {"status": "updated", "model_id": req.model_id}
        
    new_model = DBModel(
        model_id=req.model_id,
        project_id=proj_id,
        owner_id=current_user.id,
        drift_threshold=req.drift_threshold,
        status="healthy",
        accuracy=req.accuracy,
        version=req.version,
        features_json=json.dumps(req.features),
        reference_data_path=req.reference_data_path
    )
    db.add(new_model)
    
    # Insert first version as champion in model version registry
    init_version = DBModelVersion(
        project_id=proj_id,
        model_id=req.model_id,
        version=req.version,
        status="champion",
        accuracy=req.accuracy
    )
    db.add(init_version)
    db.commit()
    
    # Persist a placeholder v1.0.0 artifact on disk so rollback to the initial
    # version is always possible — even before the SDK sends a real champion model.
    try:
        import joblib as _joblib
        _art_dir = os.path.join(settings.ARTIFACT_ROOT, str(proj_id), req.model_id)
        os.makedirs(_art_dir, exist_ok=True)
        _art_path = os.path.join(_art_dir, f"version_{req.version}.pkl")
        if not os.path.exists(_art_path):
            _joblib.dump({"model_id": req.model_id, "version": req.version, "placeholder": True}, _art_path)
    except Exception as _art_err:
        pass
    
    # Initialize metrics
    if req.accuracy is not None:
        accuracy_gauge.labels(model_id=req.model_id, version=req.version).set(req.accuracy)
    
    return {"status": "registered", "model_id": req.model_id}

@router.post("/models/register", summary="Explicitly register a model with metadata")
def register_model_explicit(req: ExplicitRegisterModelRequest, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Explicitly registers a new model and its metadata (threshold, version, accuracy, features).
    """
    proj_id = req.project_id
    if proj_id is None:
        project = db.query(DBProject).filter(DBProject.owner_id == current_user.id).first()
        if not project:
            project = DBProject(name="Default Project", owner_id=current_user.id)
            db.add(project)
            db.commit()
            db.refresh(project)
        proj_id = project.id
    else:
        project = db.query(DBProject).filter(DBProject.id == proj_id, DBProject.owner_id == current_user.id).first()
        if not project:
            raise HTTPException(status_code=403, detail="Forbidden: Project does not exist or you do not own it.")

    existing = db.query(DBModel).filter(DBModel.model_id == req.model_id, DBModel.project_id == proj_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Model already registered.")

    new_model = DBModel(
        model_id=req.model_id,
        project_id=proj_id,
        owner_id=current_user.id,
        drift_threshold=req.drift_threshold,
        status="healthy",
        accuracy=req.accuracy,
        version=req.version,
        features_json=json.dumps(req.features),
        reference_data_path=""
    )
    db.add(new_model)

    init_version = DBModelVersion(
        project_id=proj_id,
        model_id=req.model_id,
        version=req.version,
        status="champion",
        accuracy=req.accuracy
    )
    db.add(init_version)
    db.commit()

    try:
        import joblib as _joblib
        _art_dir = os.path.join(settings.ARTIFACT_ROOT, str(proj_id), req.model_id)
        os.makedirs(_art_dir, exist_ok=True)
        _art_path = os.path.join(_art_dir, f"version_{req.version}.pkl")
        if not os.path.exists(_art_path):
            _joblib.dump({"model_id": req.model_id, "version": req.version, "placeholder": True}, _art_path)
    except Exception as _art_err:
        pass

    if req.accuracy is not None:
        accuracy_gauge.labels(model_id=req.model_id, version=req.version).set(req.accuracy)

    return {"status": "registered", "model_id": req.model_id}

@router.put("/models/{model_id}/webhook", summary="Update the webhook URL for external retraining orchestrators")
def update_webhook(model_id: str, req: WebhookUpdateRequest, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    model = verify_model_access(db, current_user, model_id)
    model.retrain_webhook_url = req.webhook_url
    db.commit()
    return {"status": "updated", "webhook_url": req.webhook_url}

@router.delete("/models/{model_id}", summary="Delete a model and all its historical telemetry, versions, and events")
def delete_model(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    model = verify_model_access(db, current_user, model_id)
    try:
        db.query(DBPredictionLog).filter(DBPredictionLog.model_id == model_id).delete(synchronize_session=False)
        db.query(DBRetrainingEvent).filter(DBRetrainingEvent.model_id == model_id).delete(synchronize_session=False)
        db.query(DBAuditLogEntry).filter(DBAuditLogEntry.model_id == model_id).delete(synchronize_session=False)
        db.query(DBModelVersion).filter(DBModelVersion.model_id == model_id).delete(synchronize_session=False)
        db.delete(model)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete model: {e}")
    return {"status": "deleted", "model_id": model_id}

@router.get("/models", summary="List all monitored models")
def list_models(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    check_and_recover_all_stale_jobs_for_user(current_user.id, db)
    models = db.query(DBModel).filter(DBModel.owner_id == current_user.id).all()
    return [{
        "model_id": m.model_id,
        "drift_threshold": m.drift_threshold,
        "status": m.status,
        "accuracy": m.accuracy,
        "version": m.version,
        "features": json.loads(m.features_json),
        "reference_data_path": m.reference_data_path,
        "retrain_webhook_url": m.retrain_webhook_url,
        "created_at": m.created_at.isoformat()
    } for m in models]

@router.get("/models/{model_id}", summary="Get detailed health of a model")
def get_model_details(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    check_and_recover_all_stale_jobs_for_user(current_user.id, db)
    model = verify_model_access(db, current_user, model_id)
    return {
        "model_id": model.model_id,
        "drift_threshold": model.drift_threshold,
        "status": model.status,
        "accuracy": model.accuracy,
        "version": model.version,
        "features": json.loads(model.features_json),
        "reference_data_path": model.reference_data_path,
        "retrain_webhook_url": model.retrain_webhook_url,
        "created_at": model.created_at.isoformat()
    }

@router.get("/models/{model_id}/versions", summary="Get version history of a model")
def get_model_versions(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    model = verify_model_access(db, current_user, model_id)
    versions = db.query(DBModelVersion)\
                 .filter(DBModelVersion.model_id == model_id, DBModelVersion.project_id == model.project_id)\
                 .order_by(DBModelVersion.created_at.desc())\
                 .all()
    if not versions:
        return [{"version": model.version, "status": "champion", "accuracy": model.accuracy}]
    return [{
        "version": v.version,
        "status": v.status,
        "accuracy": v.accuracy
    } for v in versions]

@router.post("/models/{model_id}/rollback", summary="Roll back model to a specified previous version")
def rollback_model_version(model_id: str, req: RollbackRequest, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    model = verify_model_access(db, current_user, model_id)
    target_ver = db.query(DBModelVersion).filter(
        DBModelVersion.model_id == model_id,
        DBModelVersion.project_id == model.project_id,
        DBModelVersion.version == req.target_version
    ).first()
    
    if not target_ver:
        raise HTTPException(status_code=404, detail=f"Target version {req.target_version} not found in registry.")
        
    if target_ver.status == "champion":
        raise HTTPException(status_code=400, detail=f"Target version {req.target_version} is already the current champion.")

    artifact_path = os.path.join(settings.ARTIFACT_ROOT, str(model.project_id), model_id, f"version_{target_ver.version}.pkl")
    if not os.path.exists(artifact_path):
        raise HTTPException(
            status_code=404,
            detail=f"Rollback failed: Model artifact file for version {target_ver.version} not found on disk at {artifact_path}."
        )
        
    try:
        import joblib
        loaded_artifact = joblib.load(artifact_path)
        if isinstance(loaded_artifact, dict) and loaded_artifact.get("placeholder") is True:
            raise HTTPException(
                status_code=404,
                detail=f"Rollback failed: Model artifact file for version {target_ver.version} not found on disk at {artifact_path}."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Rollback failed: Model artifact file for version {target_ver.version} is corrupted or cannot be loaded: {str(e)}."
        )
        
    old_version = model.version
    old_accuracy = model.accuracy
    
    db.query(DBModelVersion).filter(
        DBModelVersion.model_id == model_id,
        DBModelVersion.project_id == model.project_id,
        DBModelVersion.status == "champion"
    ).update({"status": "archived"})

    target_ver.status = "champion"
    model.version = target_ver.version
    model.accuracy = target_ver.accuracy
    model.status = "healthy"
    
    db.add(DBAuditLogEntry(
        project_id=model.project_id,
        model_id=model_id,
        event_type="rollback",
        model_version=target_ver.version,
        drift_score=0.0,
        triggered_by="manual",
        details_json=json.dumps({
            "message": f"Emergency rollback initiated. Reverted model version from {old_version} to {target_ver.version}.",
            "old_version": old_version,
            "new_version": target_ver.version,
            "old_accuracy": old_accuracy,
            "new_accuracy": target_ver.accuracy
        })
    ))
    
    db.commit()
    
    if target_ver.accuracy is not None:
        accuracy_gauge.labels(model_id=model_id, version=target_ver.version).set(target_ver.accuracy)
    
    send_alert(
        event_type="rollback",
        message=f"CRITICAL: Emergency rollback initiated for model '{model_id}'! Reverted from v{old_version} to v{target_ver.version}.",
        details={
            "model_id": model_id,
            "old_version": old_version,
            "new_version": target_ver.version,
            "old_accuracy": f"{old_accuracy:.4f}" if old_accuracy is not None else "N/A",
            "new_accuracy": f"{target_ver.accuracy:.4f}" if target_ver.accuracy is not None else "N/A",
            "action": "reverted_to_champion"
        }
    )
    
    return {
        "status": "rolled_back",
        "model_id": model_id,
        "previous_version": old_version,
        "current_version": target_ver.version
    }
