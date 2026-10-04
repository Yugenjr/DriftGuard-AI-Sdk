import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from main import get_db, get_current_user, DBUser, verify_model_access, DBModelVersion
from driftguard.config import settings
from driftguard.artifact_store import get_artifact_store, S3ArtifactStore, LocalArtifactStore

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])

def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

@router.get("/{model_id}/versions/{version}/download", summary="Download model artifact")
def download_artifact(model_id: str, version: str, background_tasks: BackgroundTasks, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieves the actual .pkl artifact for a specific model version.
    """
    model = verify_model_access(db, current_user, model_id)
    
    # Verify version exists in DB
    db_version = db.query(DBModelVersion).filter(
        DBModelVersion.model_id == model_id,
        DBModelVersion.project_id == model.project_id,
        DBModelVersion.version == version
    ).first()
    
    if not db_version:
        raise HTTPException(status_code=404, detail="Version not found")
        
    store = get_artifact_store(settings.ARTIFACT_ROOT)
    
    if not store.exists(str(model.project_id), model_id, version):
        raise HTTPException(status_code=404, detail="Artifact file not found in storage")

    if isinstance(store, LocalArtifactStore):
        path = store._get_path(str(model.project_id), model_id, version)
        return FileResponse(path, filename=f"{model_id}_v{version}.pkl")
        
    elif isinstance(store, S3ArtifactStore):
        # Download to temp file and serve
        key = store._get_key(str(model.project_id), model_id, version)
        tmp = tempfile.NamedTemporaryFile(suffix='.pkl', delete=False)
        tmp.close()
        try:
            store.s3_client.download_file(store.bucket, key, tmp.name)
            background_tasks.add_task(remove_file, tmp.name)
            return FileResponse(tmp.name, filename=f"{model_id}_v{version}.pkl")
        except Exception as e:
            remove_file(tmp.name)
            raise HTTPException(status_code=500, detail=f"Failed to fetch artifact from S3: {e}")
            
    raise HTTPException(status_code=500, detail="Unsupported artifact store type")
