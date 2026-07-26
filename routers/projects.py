from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from main import get_db, DBProject, DBUser, ProjectCreateRequest, get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", summary="Create a new logical project scope")
def create_project(req: ProjectCreateRequest, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Creates a project scope mapping registered models to ownership permissions.
    """
    existing = db.query(DBProject).filter(DBProject.name == req.name, DBProject.owner_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project with this name already exists under your ownership.")
        
    new_proj = DBProject(
        name=req.name,
        owner_id=current_user.id
    )
    db.add(new_proj)
    db.commit()
    db.refresh(new_proj)
    
    return {
        "id": new_proj.id,
        "name": new_proj.name,
        "owner_id": new_proj.owner_id
    }

@router.get("", summary="List all projects under current user scope")
def get_user_projects(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieves all projects owned by authenticated user.
    """
    projects = db.query(DBProject).filter(DBProject.owner_id == current_user.id).all()
    return [{"id": p.id, "name": p.name} for p in projects]
