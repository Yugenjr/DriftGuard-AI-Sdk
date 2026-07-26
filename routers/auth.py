import hashlib
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from main import get_db, DBUser, UserRegisterRequest, get_current_user

router = APIRouter(prefix="/users", tags=["Authentication"])

@router.post("/register", summary="Register new user credentials")
def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user, generates a unique API key, and stores its SHA-256 hash.
    """
    existing = db.query(DBUser).filter(DBUser.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already registered.")
        
    api_key = f"dg-{secrets.token_hex(16)}"
    hash_val = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    
    new_user = DBUser(
        email=req.email,
        name=req.name,
        api_key_hash=hash_val,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "email": req.email,
        "api_key": api_key  # Plaintext key only returned on creation
    }

@router.post("/rotate-key", summary="Rotate active user key credentials")
def rotate_api_key(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Invalidates current API key and issues a newly generated token.
    """
    db_user = db.query(DBUser).filter(DBUser.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User profile not found.")
        
    new_key = f"dg-{secrets.token_hex(16)}"
    hash_val = hashlib.sha256(new_key.encode("utf-8")).hexdigest()
    
    db_user.api_key_hash = hash_val
    db.commit()
    
    return {
        "status": "rotated",
        "api_key": new_key
    }
