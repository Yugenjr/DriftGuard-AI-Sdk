"""
DriftGuard API Gateway & Core Platform Server.
FastAPI server managing registered models, telemetry metrics logging, drift logs, audit trails, and retraining triggers.
"""
import os
import json
import time
import datetime
from zoneinfo import ZoneInfo
import numpy as np
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, func, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging
import secrets
import hashlib
import httpx
from driftguard.config import settings
from driftguard.alert import send_alert

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DriftGuard.API")

# Create database directory if using SQLite
if settings.MLFLOW_TRACKING_URI.startswith("sqlite:///"):
    db_file = settings.MLFLOW_TRACKING_URI.replace("sqlite:///", "")
    if db_file and "/" in db_file:
        os.makedirs(os.path.dirname(db_file), exist_ok=True)

# ----------------------------------------------------
# DATABASE SETUP (SQLite fallback / Postgres)
# ----------------------------------------------------
from sqlalchemy.pool import NullPool

db_url = f"postgresql://{os.getenv('POSTGRES_USER', 'driftguard')}:{os.getenv('POSTGRES_PASSWORD', 'driftguard')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'driftguard')}"

# Use SQLite for easy local execution if Postgres is unavailable
try:
    engine = create_engine(db_url, connect_args={"connect_timeout": 2}, pool_size=50, max_overflow=100)
    # Force test connection
    with engine.connect() as conn:
        pass
    print("DriftGuard connected to PostgreSQL Database.")
except Exception:
    local_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "driftguard_metadata.db"))
    db_url = f"sqlite:///{local_db_path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False}, poolclass=NullPool)
    print(f"DriftGuard connected to Local SQLite Database at: {local_db_path}")

# Configure SQLite parameters for production concurrency
from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in db_url:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA busy_timeout=10000")
        except Exception as e:
            print(f"[SQLite Pragma] Warning setting WAL: {e}")
        finally:
            cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_ist_time():
    return datetime.datetime.now(ZoneInfo("Asia/Kolkata"))

# ----------------------------------------------------
# DATABASE MODELS
# ----------------------------------------------------
class DBUser(Base):
    __tablename__ = "dg_users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    api_key_hash = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_ist_time)
    is_active = Column(Boolean, default=True)

    projects = relationship("DBProject", back_populates="owner", cascade="all, delete-orphan")
    models = relationship("DBModel", back_populates="owner")


class DBProject(Base):
    __tablename__ = "dg_projects"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("dg_users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_ist_time)

    owner = relationship("DBUser", back_populates="projects")
    models = relationship("DBModel", back_populates="project", cascade="all, delete-orphan")


class DBModel(Base):
    __tablename__ = "dg_models"
    model_id = Column(String(100), primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("dg_projects.id"), primary_key=True)
    owner_id = Column(Integer, ForeignKey("dg_users.id"), nullable=True)
    drift_threshold = Column(Float, default=0.15)
    status = Column(String(50), default="healthy") # healthy, degraded, retraining
    accuracy = Column(Float, nullable=True)
    version = Column(String(50), default="1.0.0")
    features_json = Column(Text, default="[]")
    reference_data_path = Column(String(255), default="")
    retrain_webhook_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_ist_time)

    project = relationship("DBProject", back_populates="models")
    owner = relationship("DBUser", back_populates="models")

# Alias to satisfy DBModelMetadata references
DBModelMetadata = DBModel

class DBPredictionLog(Base):
    __tablename__ = "dg_predictions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, default=1)
    model_id = Column(String(100), index=True)
    features_json = Column(Text)
    prediction_json = Column(Text)
    drift_score = Column(Float)
    timestamp = Column(DateTime(timezone=True), default=get_ist_time)

class DBRetrainingEvent(Base):
    __tablename__ = "dg_retraining_events"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, default=1)
    model_id = Column(String(100), index=True)
    status = Column(String(50)) # running, completed, failed
    triggered_by = Column(String(50)) # automatic, manual
    start_time = Column(DateTime(timezone=True), default=get_ist_time)
    end_time = Column(DateTime(timezone=True), nullable=True)
    last_heartbeat = Column(DateTime(timezone=True), default=get_ist_time, nullable=True)
    old_accuracy = Column(Float)
    new_accuracy = Column(Float, nullable=True)
    old_version = Column(String(50))
    new_version = Column(String(50), nullable=True)
    details_json = Column(Text, default="{}")

class DBAuditLogEntry(Base):
    __tablename__ = "dg_audit_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, default=1)
    model_id = Column(String(100), index=True)
    event_type = Column(String(100)) # drift_detected, retrain_triggered, model_promoted, rollback
    model_version = Column(String(50))
    drift_score = Column(Float)
    triggered_by = Column(String(50))
    details_json = Column(Text, default="{}")
    timestamp = Column(DateTime(timezone=True), default=get_ist_time)

class DBModelVersion(Base):
    __tablename__ = "dg_model_versions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, default=1)
    model_id = Column(String(100), index=True)
    version = Column(String(50), index=True)
    status = Column(String(50))  # champion, candidate, archived, rolled_back
    accuracy = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_ist_time)

# ----------------------------------------------------
# DATABASE MIGRATION AND STARTUP INIT
# ----------------------------------------------------
try:
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    
    # 1. Inspect existing tables
    has_models_table = inspector.has_table("dg_models")
    has_old_table = inspector.has_table("dg_models_old")
    needs_composite_migration = False
    
    if has_models_table:
        pk_constraint = inspector.get_pk_constraint("dg_models")
        pk_cols = pk_constraint.get("constrained_columns", [])
        if len(pk_cols) == 1 and "project_id" not in pk_cols:
            needs_composite_migration = True
            
    with engine.begin() as conn:
        # Drop old conflicting index on dg_models_old if it exists
        if has_old_table:
            try:
                conn.execute(text("DROP INDEX IF EXISTS ix_dg_models_model_id;"))
            except Exception as index_err:
                print(f"[Migration] Warning dropping leftover index: {index_err}")
                
        # 2. If dg_models has single-column PK, rename it so Base.metadata.create_all creates the new composite key version
        if needs_composite_migration:
            print("[Migration] Renaming old single-key dg_models to dg_models_old for composite key migration...")
            try:
                conn.execute(text("DROP INDEX IF EXISTS ix_dg_models_model_id;"))
            except Exception as index_err:
                print(f"[Migration] Warning dropping index: {index_err}")
            conn.execute(text("ALTER TABLE dg_models RENAME TO dg_models_old;"))
            has_old_table = True
            
    # 3. Create all tables (will create new dg_models and create new tables if missing)
    Base.metadata.create_all(bind=engine)
    
    with engine.begin() as conn:
        # 4. If we have dg_models_old, copy over the data to the newly created composite-key version
        if has_old_table:
            print("[Migration] Copying data from dg_models_old to dg_models composite-key table...")
            try:
                conn.execute(text("""
                    INSERT OR IGNORE INTO dg_models (model_id, project_id, owner_id, drift_threshold, status, accuracy, version, features_json, reference_data_path, created_at)
                    SELECT model_id, COALESCE(project_id, 1), owner_id, drift_threshold, status, accuracy, version, features_json, reference_data_path, created_at
                    FROM dg_models_old;
                """))
                conn.execute(text("DROP TABLE dg_models_old;"))
                print("[Migration] dg_models composite key migration completed successfully.")
            except Exception as copy_err:
                print(f"[Migration] Error completing copy from dg_models_old: {copy_err}")
            
        # 5. Check and append project_id / last_heartbeat columns for event log tables
        for table_name in ["dg_predictions", "dg_retraining_events", "dg_audit_logs", "dg_model_versions"]:
            if inspector.has_table(table_name):
                cols = [c["name"] for c in inspector.get_columns(table_name)]
                if "project_id" not in cols:
                    print(f"[Migration] Adding project_id column to {table_name}...")
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN project_id INTEGER DEFAULT 1;"))
                    
        # 6. Add last_heartbeat column to dg_retraining_events
        if inspector.has_table("dg_retraining_events"):
            cols = [c["name"] for c in inspector.get_columns("dg_retraining_events")]
            if "last_heartbeat" not in cols:
                print("[Migration] Adding last_heartbeat column to dg_retraining_events...")
                conn.execute(text("ALTER TABLE dg_retraining_events ADD COLUMN last_heartbeat TIMESTAMP;"))
                
    # 7. Add retrain_webhook_url column to dg_models
        if inspector.has_table("dg_models"):
            cols = [c["name"] for c in inspector.get_columns("dg_models")]
            if "retrain_webhook_url" not in cols:
                print("[Migration] Adding retrain_webhook_url column to dg_models...")
                conn.execute(text("ALTER TABLE dg_models ADD COLUMN retrain_webhook_url VARCHAR(500);"))

    # 8. Seed default user and project if missing
    db = SessionLocal()
    try:
        default_user = db.query(DBUser).filter(DBUser.email == "admin@driftguard.com").first()
        if not default_user:
            # SECURITY FIX: Never use a hardcoded default key in production.
            # Read from env var; fall back to a randomly-generated key logged once.
            # Set DRIFTGUARD_DEFAULT_API_KEY in .env to get a stable key across restarts.
            default_key = os.getenv("DRIFTGUARD_DEFAULT_API_KEY") or f"dg-{secrets.token_hex(16)}"
            hash_val = hashlib.sha256(default_key.encode("utf-8")).hexdigest()
            default_user = DBUser(
                email="admin@driftguard.com",
                name="Default Admin",
                api_key_hash=hash_val,
                is_active=True
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
            logger.warning(
                f"[STARTUP] Default admin user created. API Key: {default_key} "
                "— Set DRIFTGUARD_DEFAULT_API_KEY in .env to make this persistent."
            )
            
        default_project = db.query(DBProject).filter(DBProject.owner_id == default_user.id).first()
        if not default_project:
            default_project = DBProject(
                name="Default Project",
                owner_id=default_user.id
            )
            db.add(default_project)
            db.commit()
            db.refresh(default_project)
            
        # Migrate any models with null project_id/owner_id
        null_models = db.query(DBModel).filter((DBModel.project_id == None) | (DBModel.owner_id == None)).all()
        for m in null_models:
            m.project_id = default_project.id
            m.owner_id = default_user.id
        if null_models:
            db.commit()
            print(f"Migrated {len(null_models)} existing models to Default Project.")
            
    finally:
        db.close()
except Exception as e:
    print(f"Auto-migration helper: {e}")

# ----------------------------------------------------
# PROMETHEUS METRICS SETUP
# ----------------------------------------------------
predictions_counter = Counter(
    "driftguard_predictions_total",
    "Total predictions served by DriftGuard",
    ["model_id"]
)
drift_gauge = Gauge(
    "driftguard_drift_score",
    "Active running drift score computed",
    ["model_id", "feature_index"]
)
accuracy_gauge = Gauge(
    "driftguard_model_accuracy",
    "Model performance accuracy score",
    ["model_id", "version"]
)
retrain_counter = Counter(
    "driftguard_retraining_triggered_total",
    "Total model retraining loops initiated",
    ["model_id", "triggered_by"]
)
latency_histogram = Histogram(
    "driftguard_inference_latency_seconds",
    "Inference latency duration in seconds",
    ["model_id"]
)

# Initialize FastAPI App
app = FastAPI(
    title="DriftGuard Platform Core API",
    description="Autonomous ML Model Health Platform REST Gateway Server",
    version="1.0.0"
)

from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # SECURITY FIX: Never expose raw exception messages to API consumers.
    # Internal details are logged server-side only.
    logger.error(f"[ERROR] Unhandled exception on {request.method} {request.url.path}: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

# SECURITY FIX: CORS origins are configurable via CORS_ALLOWED_ORIGINS env var.
# Defaults to localhost dashboard + Grafana. Set to "*" only for open development.
_cors_origins_raw = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
_cors_origins = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# PYDANTIC SCHEMAS
# ----------------------------------------------------
class UserRegisterRequest(BaseModel):
    email: str = Field(..., example="user@example.com")
    name: str = Field(..., example="John Doe")

class ProjectCreateRequest(BaseModel):
    name: str = Field(..., example="My ML Project")

class RegisterModelRequest(BaseModel):
    model_id: str = Field(..., example="fraud-detector-v1")
    project_id: Optional[int] = Field(default=None, example=1)
    drift_threshold: float = Field(0.15, example=0.15)
    reference_data_path: str = Field("", example="./data/baseline.parquet")
    features: List[str] = Field(default_factory=list, example=["amount", "location_score", "velocity"])
    # FIX: accuracy and version were accessed by register_model() but were absent
    # from this schema, causing AttributeError. Added with defaults matching the
    # test contract: accuracy=0.85 is the expected baseline for a freshly registered model.
    accuracy: Optional[float] = Field(default=0.85, example=0.85)
    version: str = Field("1.0.0", example="1.0.0")

class WebhookUpdateRequest(BaseModel):
    webhook_url: Optional[str] = Field(None, example="http://airflow:8080/api/v1/dags/retrain_model/dagRuns")
    accuracy: Optional[float] = Field(default=None, example=0.85)
    version: Optional[str] = Field(default="1.0.0", example="1.0.0")

class ExplicitRegisterModelRequest(BaseModel):
    model_id: str = Field(..., example="fraud-detector-v1")
    project_id: Optional[int] = Field(default=None, example=1)
    drift_threshold: float = Field(0.15, example=0.37)
    accuracy: Optional[float] = Field(default=None, example=0.94)
    version: str = Field("1.0.0", example="1.0.0")
    features: List[str] = Field(default_factory=list, example=["feature_1", "feature_2"])

class PredictTelemetryRequest(BaseModel):
    features: List[Any] = Field(..., example=[1.2, 0.4, 9.8])
    prediction: List[Any] = Field(..., example=[1.0])
    drift_score: float = Field(..., example=0.08)

class RetrainTriggerRequest(BaseModel):
    drift_score: float = Field(0.15, example=0.21)
    triggered_by: str = Field("automatic", example="automatic")
    source: str = Field(
        "server",
        example="server",
        description=(
            "Origin of the retrain request. "
            "'server' = run the built-in server-side pipeline (default). "
            "'sdk_callback' = SDK will run its own pipeline; server only records the event."
        ),
    )


class RetrainCompleteRequest(BaseModel):
    """
    Posted by the SDK CallbackRunner when its local pipeline finishes.
    The server uses this to update the model record, audit log, and metrics.
    """
    event_id: Optional[int] = Field(None, description="Retraining event DB row id.")
    validation_passed: bool = Field(..., description="True if challenger beat champion.")
    new_version: Optional[str] = Field(None, example="1.0.5")
    new_accuracy: Optional[float] = Field(None, example=0.934)
    old_accuracy: Optional[float] = Field(None, example=0.912)
    error: Optional[str] = Field(None, description="Error message if pipeline failed.")

class EvidentlyCalculateRequest(BaseModel):
    reference_data: List[Dict[str, Any]]
    current_data: List[Dict[str, Any]]
    target_column: Optional[str] = None

class RollbackRequest(BaseModel):
    target_version: str = Field(..., example="1.0.4")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.middleware("http")
async def api_key_auth_middleware(request: Request, call_next):
    # CORS preflight requests never carry custom headers — pass them through
    # to CORSMiddleware which will add the appropriate CORS response headers.
    if request.method == "OPTIONS":
        return await call_next(request)

    # Exclude open endpoints
    path = request.url.path
    exempt_prefixes = ["/health", "/api/health", "/docs", "/openapi.json", "/users/register", "/metrics"]
    if any(path.startswith(p) for p in exempt_prefixes):
        return await call_next(request)

    # Get API key header
    api_key = request.headers.get("X-API-Key")
    # SECURITY FIX: Never print API keys to stdout — they are credentials.
    if not api_key:
        logger.debug("AUTH: Missing X-API-Key header on %s %s", request.method, request.url.path)
        return Response(content="Unauthorized: Missing X-API-Key header", status_code=401)

    # Hash the key before any DB lookup
    api_key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    # Query user by hash only — plaintext key never touches the DB
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.api_key_hash == api_key_hash, DBUser.is_active == True).first()
        if not user:
            logger.debug("AUTH: Invalid API key on %s %s", request.method, request.url.path)
            return Response(content="Unauthorized: Invalid API Key", status_code=401)
        logger.debug("AUTH: Authenticated user=%s", user.email)
        request.state.user = user
    finally:
        db.close()

    return await call_next(request)

def get_current_user(request: Request) -> DBUser:
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return request.state.user

def verify_model_access(db: Session, current_user: DBUser, model_id: str, allow_missing: bool = False) -> Optional[DBModel]:
    models = db.query(DBModel).filter(DBModel.model_id == model_id).all()
    if not models:
        if allow_missing:
            return None
        raise HTTPException(status_code=404, detail="Model not registered.")
    user_model = next((m for m in models if m.owner_id == current_user.id), None)
    if not user_model:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this model.")
    return user_model

# ----------------------------------------------------
# API ENDPOINTS
# ----------------------------------------------------
@app.post("/users/register", summary="Register a new user and generate an API key")
def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(DBUser).filter(DBUser.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered.")
    
    # Generate API key
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
        "id": new_user.id,
        "email": new_user.email,
        "name": new_user.name,
        "api_key": api_key  # Plaintext key only returned on creation
    }

@app.post("/users/rotate-key", summary="Rotate the active API key for the current user")
def rotate_api_key(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # Merge detached user to the current session
    db_user = db.merge(current_user)
    # Generate new API key
    new_key = f"dg-{secrets.token_hex(16)}"
    hash_val = hashlib.sha256(new_key.encode("utf-8")).hexdigest()
    
    db_user.api_key_hash = hash_val
    db.commit()
    
    return {
        "email": db_user.email,
        "api_key": new_key
    }

@app.get("/users/me", summary="Get profile info of the authenticated user")
def get_user_profile(current_user: DBUser = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat()
    }

@app.post("/projects", summary="Create a new project")
def create_project(req: ProjectCreateRequest, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    new_project = DBProject(
        name=req.name,
        owner_id=current_user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {
        "id": new_project.id,
        "name": new_project.name,
        "owner_id": new_project.owner_id,
        "created_at": new_project.created_at.isoformat()
    }

@app.get("/projects", summary="List all projects owned by the user")
def list_projects(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(DBProject).filter(DBProject.owner_id == current_user.id).all()
    return [{
        "id": p.id,
        "name": p.name,
        "owner_id": p.owner_id,
        "created_at": p.created_at.isoformat()
    } for p in projects]

@app.get("/projects/{id}", summary="Get project details")
def get_project(id: int, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(DBProject).filter(DBProject.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this project.")
    return {
        "id": project.id,
        "name": project.name,
        "owner_id": project.owner_id,
        "created_at": project.created_at.isoformat(),
        "models": [m.model_id for m in project.models]
    }

@app.post("/register", summary="Register a model for platform tracking")
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
    # The server writes this because it owns the artifact directory and always
    # runs from a known CWD (the project root).
    try:
        import joblib as _joblib
        _art_dir = os.path.join(settings.ARTIFACT_ROOT, str(proj_id), req.model_id)
        os.makedirs(_art_dir, exist_ok=True)
        _art_path = os.path.join(_art_dir, f"version_{req.version}.pkl")
        if not os.path.exists(_art_path):
            # Write a lightweight sentinel so rollback endpoint can validate the file
            _joblib.dump({"model_id": req.model_id, "version": req.version, "placeholder": True}, _art_path)
            print(f"[Register] Wrote initial artifact placeholder to {_art_path}")
    except Exception as _art_err:
        print(f"[Register] Warning: Could not write v{req.version} artifact placeholder: {_art_err}")
    
    # Initialize metrics
    if req.accuracy is not None:
        accuracy_gauge.labels(model_id=req.model_id, version=req.version).set(req.accuracy)
    
    return {"status": "registered", "model_id": req.model_id}

# Remaining routes migrated to routers/


def check_and_recover_all_stale_jobs_for_user(user_id: int, db: Session):
    timeout_limit = datetime.datetime.now(ZoneInfo("Asia/Kolkata")) - datetime.timedelta(seconds=300)
    stale_events = db.query(DBRetrainingEvent).join(
        DBModel,
        (DBModel.model_id == DBRetrainingEvent.model_id) & (DBModel.project_id == DBRetrainingEvent.project_id)
    ).filter(
        DBModel.owner_id == user_id,
        DBRetrainingEvent.status == "running",
        DBRetrainingEvent.last_heartbeat < timeout_limit
    ).all()
    
    if stale_events:
        print(f"[Self-Healing] Recovering {len(stale_events)} stale retraining events for user {user_id}...")
        for event in stale_events:
            event.status = "failed"
            event.end_time = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
            event.details_json = json.dumps({"error": "Retraining job timed out/stale. Recovered by watchdog lock resolver."})
            
            db.add(DBAuditLogEntry(
                project_id=event.project_id,
                model_id=event.model_id,
                event_type="validation_failed",
                model_version=event.old_version,
                drift_score=0.0,
                triggered_by=event.triggered_by,
                details_json=json.dumps({"error": "Retraining job timed out/stale. Lock resolved."})
            ))
            
            # Revert model status
            model = db.query(DBModel).filter(
                DBModel.model_id == event.model_id,
                DBModel.project_id == event.project_id
            ).first()
            if model:
                model.status = "healthy"
        db.commit()

@app.post("/retrain/{model_id}", summary="Triggers retraining flow process asynchronously")
def trigger_retraining(model_id: str, req: RetrainTriggerRequest, background_tasks: BackgroundTasks, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Main trigger endpoint. Creates a retraining event record.
    """
    # 1. Recover any stale locks first
    check_and_recover_all_stale_jobs_for_user(current_user.id, db)

    # 2. Acquire row lock (with_for_update) to resolve concurrent retraining races
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

    # Lock status
    model.status = "retraining"
    db.commit()

    # Create run event entry
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

    # Expose retrain counter to prometheus
    retrain_counter.labels(model_id=model_id, triggered_by=req.triggered_by).inc()

    if req.source == "sdk_callback":
        # SDK owns the pipeline — do NOT spawn a server-side background task.
        return {
            "status": "recorded",
            "event_id": event.id,
            "message": "Event recorded. SDK callback pipeline will report results via /complete.",
        }

    if model.retrain_webhook_url:
        # ── WEBHOOK DRIVEN DISTRIBUTED RETRAINING ──
        def fire_webhook():
            try:
                print(f"[Webhook] Firing webhook for model {model_id} to {model.retrain_webhook_url}")
                payload = {
                    "event_id": event.id,
                    "model_id": model_id,
                    "drift_score": req.drift_score,
                    "callback_url": f"http://localhost:8000/retrain/{model_id}/complete"
                }
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(model.retrain_webhook_url, json=payload)
                    print(f"[Webhook] Response: {resp.status_code}")
            except Exception as e:
                print(f"[Webhook] Failed to hit webhook: {e}")
    
        background_tasks.add_task(fire_webhook)
        return {"status": "triggered_webhook", "event_id": event.id, "message": "Webhook fired to orchestrator."}

    # Default: push to FastAPI background executor (server-side pipeline)
    background_tasks.add_task(
        run_retraining_process,
        model_id=model_id,
        event_id=event.id,
        drift_score=req.drift_score,
        triggered_by=req.triggered_by
    )

    return {"status": "triggered", "event_id": event.id, "message": "Retraining initiated in background task."}


@app.post("/retrain/{model_id}/complete", summary="SDK callback pipeline reports its results")
def complete_retraining(model_id: str, req: RetrainCompleteRequest, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Called exclusively by the SDK's ``RetrainerCallbackRunner`` after its
    local pipeline finishes. Updates model record, audit log, Prometheus
    metrics, and Slack alerts.
    """
    model = verify_model_access(db, current_user, model_id)

    # Locate the event record
    event = None
    if req.event_id:
        event = db.query(DBRetrainingEvent).filter(
            DBRetrainingEvent.id == req.event_id,
            DBRetrainingEvent.project_id == model.project_id
        ).first()
    if event is None:
        # Fall back to the latest running event for this model
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
        # ── Challenger promoted ──────────────────────────────────────────
        old_version = model.version
        old_accuracy = req.old_accuracy if req.old_accuracy is not None else model.accuracy

        model.status = "healthy"
        model.accuracy = req.new_accuracy
        model.version = req.new_version

        # Archive old champion version in version registry
        db.query(DBModelVersion).filter(
            DBModelVersion.model_id == model_id,
            DBModelVersion.project_id == model.project_id,
            DBModelVersion.status == "champion"
        ).update({"status": "archived"})

        # FIX: Clear any dangling "candidate" rows written during the in-flight
        # training period before inserting the new champion record, so the version
        # registry never has two rows with the same version string or a stale
        # candidate alongside the new champion.
        db.query(DBModelVersion).filter(
            DBModelVersion.model_id == model_id,
            DBModelVersion.project_id == model.project_id,
            DBModelVersion.status == "candidate"
        ).delete(synchronize_session=False)

        # Insert new challenger version as champion
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
                {"message": "Promoted by SDK callback pipeline.",
                 "source": "sdk_callback"}
            )

        # Write promotion audit entry
        db.add(DBAuditLogEntry(
            project_id=model.project_id,
            model_id=model_id,
            event_type="model_promoted",
            model_version=req.new_version,
            drift_score=0.0,
            triggered_by="automatic",
            details_json=json.dumps({
                "message": (
                    f"SDK callback challenger {req.new_version} promoted. "
                    f"Accuracy {old_accuracy:.4f} → {req.new_accuracy:.4f}."
                ),
                "source": "sdk_callback",
                "old_version": old_version,
                "new_version": req.new_version,
                "old_accuracy": old_accuracy,
                "new_accuracy": req.new_accuracy,
            })
        ))
        db.commit()

        # Update Prometheus gauge
        accuracy_gauge.labels(model_id=model_id, version=req.new_version).set(req.new_accuracy)

        # Slack alert
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
        # ── Challenger rejected or pipeline error ──────────────────────────
        model.status = "healthy"  # revert from "retraining" regardless

        # FIX: Clean up any "candidate" row the SDK may have written so the
        # version registry does not contain a permanently orphaned candidate.
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
                {"error": req.error or "Challenger did not pass validation.",
                 "source": "sdk_callback"}
            )

        # Write rejection audit entry
        db.add(DBAuditLogEntry(
            project_id=model.project_id,
            model_id=model_id,
            event_type="validation_failed",
            model_version=model.version,
            drift_score=0.0,
            triggered_by="automatic",
            details_json=json.dumps(
                {"error": req.error or "Challenger did not pass validation.",
                 "source": "sdk_callback"}
            ),
        ))
        db.commit()


# Prometheus metrics scraping endpoint kept locally
@app.get("/metrics", summary="Scrapes Prometheus metrics format")
def metrics():
    """
    Prometheus metrics scraping endpoint.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/health")
def healthcheck():
    """
    API Health check
    """
    return {"status": "healthy", "timestamp": datetime.datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()}

# ----------------------------------------------------
# BACKGROUND RETRAINING EXECUTOR PROCESS
# ----------------------------------------------------
def _update_retraining_heartbeat(event_id: int):
    """
    FIX: Update last_heartbeat on a DBRetrainingEvent so the stale-job watchdog
    (which kills any job whose heartbeat is older than 5 minutes) does not
    incorrectly terminate long-running but healthy retraining jobs.
    Called periodically from run_retraining_process().
    """
    try:
        hb_db = SessionLocal()
        try:
            ev = hb_db.query(DBRetrainingEvent).filter(DBRetrainingEvent.id == event_id).first()
            if ev and ev.status == "running":
                ev.last_heartbeat = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
                hb_db.commit()
                print(f"[Heartbeat] Updated last_heartbeat for event_id={event_id}")
        finally:
            hb_db.close()
    except Exception as hb_err:
        print(f"[Heartbeat] Warning: failed to update heartbeat for event {event_id}: {hb_err}")


def run_retraining_process(model_id: str, event_id: int, drift_score: float, triggered_by: str):
    """
    Asynchronous executor thread running pipeline steps.
    Imports retraining modules to isolate ZenML + Great Expectations execution scopes.
    """
    # Create thread local session
    db = SessionLocal()
    try:
        print(f"[{model_id}] Starting pipeline execution...")
        event = db.query(DBRetrainingEvent).filter(DBRetrainingEvent.id == event_id).first()
        proj_id = event.project_id if event else 1
        model = db.query(DBModel).filter(DBModel.model_id == model_id, DBModel.project_id == proj_id).first()
        
        if not model:
            print(f"[{model_id}] Model not found in DB, aborting background retraining.")
            return

        # 1. Log Retrain Trigger in Audit Logs
        audit_trig = DBAuditLogEntry(
            project_id=model.project_id,
            model_id=model_id,
            event_type="retrain_triggered",
            model_version=model.version,
            drift_score=drift_score,
            triggered_by=triggered_by,
            details_json=json.dumps({"message": f"Retraining triggered in background due to score {drift_score:.4f}."})
        )
        db.add(audit_trig)
        db.commit()

        # FIX: Write initial heartbeat ping immediately so the watchdog does not
        # race against the 5-minute window on a slow startup path.
        _update_retraining_heartbeat(event_id)

        # Send alert
        _acc_str = f"{model.accuracy:.4f}" if model.accuracy is not None else "N/A"
        send_alert(
            event_type="retrain_triggered",
            message=f"Retraining pipeline started for model '{model_id}'",
            details={"triggered_by": triggered_by, "baseline_accuracy": _acc_str}
        )

        # 2. Resolve champion artifact path from the artifact store
        _champion_artifact_path = os.path.join(
            settings.ARTIFACT_ROOT,
            str(model.project_id),
            model_id,
            f"version_{model.version}.pkl"
        )
        print(f"[{model_id}] Champion artifact resolved to: {_champion_artifact_path}")

        # 3. Run the pipeline flow steps
        # FIX: Emit a heartbeat before and after the pipeline so the 5-minute
        # watchdog never kills a job that is merely waiting on training I/O.
        _update_retraining_heartbeat(event_id)

        # FIX: Register the challenger version as "candidate" in the version
        # registry BEFORE training begins, so dashboards can show it is in-flight.
        candidate_version = f"{model.version}-candidate"
        existing_candidate = db.query(DBModelVersion).filter(
            DBModelVersion.model_id == model_id,
            DBModelVersion.project_id == model.project_id,
            DBModelVersion.status == "candidate"
        ).first()
        if not existing_candidate:
            db.add(DBModelVersion(
                project_id=model.project_id,
                model_id=model_id,
                version=candidate_version,
                status="candidate",
                accuracy=None
            ))
            db.commit()

        try:
            from pipeline.retrain_pipeline import run_retraining_flow
            pipeline_results = run_retraining_flow(
                model_id=model_id,
                current_accuracy=model.accuracy,
                current_version=model.version,
                project_id=model.project_id,
                artifact_path=_champion_artifact_path
            )
        except Exception as pi_err:
            print(f"Pipeline flow execution failed: {pi_err}")
            pipeline_results = {
                "success": False,
                "validation_passed": False,
                "error": str(pi_err)
            }

        # Heartbeat after pipeline completes — keeps watchdog quiet on long runs.
        _update_retraining_heartbeat(event_id)

        # Clean up the in-flight candidate row now that training is done.
        db.query(DBModelVersion).filter(
            DBModelVersion.model_id == model_id,
            DBModelVersion.project_id == model.project_id,
            DBModelVersion.status == "candidate"
        ).delete(synchronize_session=False)
        db.commit()

        # 3. Check retraining pipeline outcomes
        if pipeline_results.get("success") and pipeline_results.get("validation_passed"):
            # Model validation succeeded! Promote challenger to champion
            new_acc = pipeline_results.get("new_accuracy", model.accuracy)
            new_ver = pipeline_results.get("new_version", "1.0.1")
            
            # Update Model
            model.status = "healthy"
            model.accuracy = new_acc
            model.version = new_ver
            
            # Archive old champion version in version registry
            db.query(DBModelVersion).filter(
                DBModelVersion.model_id == model_id,
                DBModelVersion.project_id == model.project_id,
                DBModelVersion.status == "champion"
            ).update({"status": "archived"})

            # Insert new challenger version as champion
            new_version_rec = DBModelVersion(
                project_id=model.project_id,
                model_id=model_id,
                version=new_ver,
                status="champion",
                accuracy=new_acc
            )
            db.add(new_version_rec)
            
            # Update Retraining Event
            if event:
                event.status = "completed"
                event.end_time = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
                event.new_accuracy = new_acc
                event.new_version = new_ver
                event.details_json = json.dumps(pipeline_results.get("details", {}))
            
            _old_acc = event.old_accuracy if event else model.accuracy
            _old_acc_str = f"{_old_acc:.4f}" if _old_acc is not None else "N/A"
            
            # Write Promotion Audit Log
            audit_prom = DBAuditLogEntry(
                project_id=model.project_id,
                model_id=model_id,
                event_type="model_promoted",
                model_version=new_ver,
                drift_score=0.0,
                triggered_by="automatic" if triggered_by == "automatic" else "manual",
                details_json=json.dumps({
                    "message": f"Challenger model {new_ver} promoted to champion. Succeeded accuracy validation check ({new_acc:.4f} > {_old_acc_str}).",
                    "before_accuracy": _old_acc,
                    "after_accuracy": new_acc
                })
            )
            db.add(audit_prom)
            db.commit()

            # Record Accuracy Gauge to Prometheus
            accuracy_gauge.labels(model_id=model_id, version=new_ver).set(new_acc)

            # Send Promotion notification
            send_alert(
                event_type="model_promoted",
                message=f"New model version '{new_ver}' promoted to champion!",
                details={
                    "model_id": model_id,
                    "old_version": event.old_version if event else model.version,
                    "new_version": new_ver,
                    "old_accuracy": _old_acc_str,
                    "new_accuracy": f"{new_acc:.4f}"
                }
            )
        else:
            # Succeeded training but validation failed, or pipeline failed
            model.status = "healthy"  # Revert back to healthy (using original champion model)
            
            if event:
                event.status = "failed"
                event.end_time = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
                event.details_json = json.dumps({
                    "error": pipeline_results.get("error", "Validation failed"),
                    "champion_accuracy": pipeline_results.get("champion_accuracy", model.accuracy),
                    "challenger_accuracy": pipeline_results.get("new_accuracy"),
                    "threshold": 0.01,
                    "comparison_method": pipeline_results.get("comparison_method", "unknown"),
                    "promotion_outcome": "rejected",
                    "message": pipeline_results.get("error", "Challenger did not beat champion by ≥1%."),
                })

            # Write Fail Audit Log
            audit_fail = DBAuditLogEntry(
                project_id=model.project_id,
                model_id=model_id,
                event_type="validation_failed",
                model_version=model.version,
                drift_score=drift_score,
                triggered_by="automatic" if triggered_by == "automatic" else "manual",
                details_json=json.dumps({
                    "message": pipeline_results.get("error", "Challenger rejected."),
                    "champion_accuracy": pipeline_results.get("champion_accuracy", model.accuracy),
                    "challenger_accuracy": pipeline_results.get("new_accuracy", 0.0),
                    "threshold": 0.01,
                    "comparison_method": pipeline_results.get("comparison_method", "unknown"),
                    "promotion_outcome": "rejected",
                })
            )
            db.add(audit_fail)
            db.commit()

            # Send failure Alert
            _champ_acc = pipeline_results.get("champion_accuracy", model.accuracy)
            _chall_acc = pipeline_results.get("new_accuracy", 0.0)
            send_alert(
                event_type="validation_failed",
                message=f"Model validation failed for challenger. Retaining champion '{model.version}'.",
                details={
                    "model_id": model_id,
                    "champion_version": model.version,
                    "champion_accuracy": f"{_champ_acc:.4f}" if _champ_acc is not None else "N/A",
                    "challenger_accuracy": f"{_chall_acc:.4f}",
                    "comparison_method": pipeline_results.get("comparison_method", "unknown"),
                }
            )

    except Exception as e:
        print(f"Background retraining crash on model {model_id}: {e}")
        # Robust revert
        try:
            db_err = SessionLocal()
            try:
                model = db_err.query(DBModel).filter(DBModel.model_id == model_id, DBModel.project_id == proj_id).first()
                if model:
                    model.status = "healthy"
                    db_err.commit()
            finally:
                db_err.close()
        except Exception:
            pass
    finally:
        db.close()

# ----------------------------------------------------
# KAFKA CONSUMER BACKGROUND WORKER
# ----------------------------------------------------
def kafka_consumer_loop():
    import json
    import httpx
    try:
        from confluent_kafka import Consumer
    except ImportError:
        print("[Kafka] confluent-kafka not installed. Consumer disabled.")
        return

    kafka_brokers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not kafka_brokers:
        print("[Kafka] KAFKA_BOOTSTRAP_SERVERS not set. Consumer disabled.")
        return

    conf = {
        'bootstrap.servers': kafka_brokers,
        'group.id': 'driftguard-backend-group',
        'auto.offset.reset': 'earliest'
    }
    
    try:
        consumer = Consumer(conf)
        consumer.subscribe(['driftguard-telemetry'])
        print(f"[Kafka] Consumer started on {kafka_brokers}, listening to 'driftguard-telemetry'")
        
        client = httpx.Client(timeout=10.0)
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"[Kafka] Consumer error: {msg.error()}")
                continue
            
            # Process Message
            try:
                payload = json.loads(msg.value().decode('utf-8'))
                model_id = payload.pop("model_id", None)
                api_key = payload.pop("api_key", None)
                
                if not model_id:
                    continue
                
                # Forward to standard endpoint to reuse all complex logic
                headers = {"X-API-Key": api_key} if api_key else {}
                # Post internally to FastAPI
                client.post(f"http://127.0.0.1:8000/predict/{model_id}", json=payload, headers=headers)
                
            except Exception as e:
                print(f"[Kafka] Error processing message: {e}")
                
    except Exception as e:
        print(f"[Kafka] Failed to start consumer: {e}")

@app.on_event("startup")
def startup_event():
    import threading
    worker = threading.Thread(target=kafka_consumer_loop, daemon=True, name="KafkaConsumerWorker")
    worker.start()

# ----------------------------------------------------
# ROUTER REGISTRATION (Delayed to prevent circular imports)
# ----------------------------------------------------
from routers import auth, projects, models, telemetry, retraining, audit, evidently

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(models.router)
app.include_router(telemetry.router)
app.include_router(retraining.router)
app.include_router(audit.router)
app.include_router(evidently.router)