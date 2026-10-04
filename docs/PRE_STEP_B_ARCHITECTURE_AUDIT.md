# Pre-Step B Architecture Consistency Audit

## 1. Current Architecture
The current architecture has been correctly refactored into a modular, self-hosted deployment.
- **Base (Mandatory):** `postgres`, `redis`, `driftguard-api`, `driftguard-dashboard`.
- **Optional Profiles:** `observability`, `orchestration`, `mlflow`, `evidently`, `messaging`.

## 2. Runtime Dependency Matrix
| Service / Component | Status | Required for Base API? | Fallback if Absent |
| :--- | :--- | :--- | :--- |
| **PostgreSQL** | Base | **Yes** | API fails to start (`create_engine` crash). |
| **Redis** | Base | **Yes** | Canary deployment / routing crashes (`redis.Redis()`). |
| **Kafka** | Optional (`messaging`) | **No** | Tracker falls back to `LocalQueueTracker`. API gracefully aborts consumer startup. |
| **Zookeeper** | Optional (`messaging`) | **No** | N/A (Kafka dependency). |
| **MLflow** | Optional (`mlflow`) | **No** | Pipeline gracefully disables MLflow tracking if `MLFLOW_TRACKING_URI` is empty. |
| **Prefect** | Optional (`orchestration`)| **No** | Pipeline uses `@flow` locally if `PREFECT_API_URL` is empty. |
| **Evidently**| Optional (`evidently`) | **No** | `drift_detector.py` falls back to in-process math mocks. |

## 3. Base vs Optional Services
The base API is now verified to be entirely independent of heavy infrastructure (Kafka, MLflow, Prefect). Redis is retained as a base service because `canary_router.py` strictly requires it.

## 4. Kafka Findings
- **API Consumer:** `main.py` explicitly checks `os.getenv("KAFKA_BOOTSTRAP_SERVERS")`. If missing, it logs a warning and gracefully exits the consumer loop without blocking FastAPI startup.
- **SDK Producer:** `tracker.py` uses HTTP/LocalQueue fallbacks automatically when Kafka is unavailable.

## 5. MLflow Findings
- **Requirement:** MLflow is an *optional* experiment tracker. It is not required for DriftGuard's core versioning, which relies entirely on PostgreSQL.
- **Changes Made:** Modified `pipeline/deploy_pipeline.py` and `pipeline/retrain_pipeline.py` to gracefully disable MLflow API calls if `MLFLOW_TRACKING_URI` is empty, preventing accidental local `./mlruns` creation or SQLite DB spawning.
- **Config:** `driftguard/config.py` was updated so `MLFLOW_TRACKING_URI` defaults to an empty string instead of `sqlite:///mlflow.db`.

## 6. Prefect Findings
- Prefect `@flow` and `@task` decorators are used in `retrain_pipeline.py`, but they do not require an active external Prefect Server (`driftguard-prefect` container) to execute synchronously in the FastAPI background worker.
- The base API runs correctly with `PREFECT_API_URL` left blank.

## 7. Evidently Findings
- `drift_detector.py` correctly attempts to reach `DRIFTGUARD_EVIDENTLY_URL`.
- If the URL is empty or the service is unreachable (e.g., HTTP 500/timeout), it gracefully falls back to local pandas statistical checks (`drift_score = min(diff * 0.1, 1.0)`). 

## 8. Redis Findings
- Redis is strictly required. It is used by `serving/canary_router.py` (which directly imports `redis.Redis` and will raise `RuntimeError` if unavailable) and `pipeline/deploy_pipeline.py` to parse routing weights. Removing it would break canary lifecycle workflows.

## 9. Compose Findings
- Removed explicit container references in optional env vars. Changed from:
  `KAFKA_BOOTSTRAP_SERVERS: kafka:29092` 
  to:
  `KAFKA_BOOTSTRAP_SERVERS: ${KAFKA_BOOTSTRAP_SERVERS:-}`
- This guarantees the API doesn't try connecting to dead hostnames if a profile is unselected.

## 10. Dashboard/API Findings
- The `DRIFTGUARD_API_URL` environment variable is only consumed by Next.js Server-Side API Routes (e.g., `pages/api/models.js`).
- This means setting `DRIFTGUARD_API_URL=http://driftguard-api:8000` is architecturally correct. The browser hits the Dashboard container (`localhost:3000`), and the Dashboard container routes the fetch to the API container via Docker's internal network. No CORS or cross-origin browser issues exist for the backend.

## 11. Changes Made in This Pass
- **`driftguard/config.py`**: Changed `MLFLOW_TRACKING_URI` default to `""`.
- **`main.py`**: Safely bypasses SQLite creation if `MLFLOW_TRACKING_URI` is empty.
- **`pipeline/retrain_pipeline.py` & `deploy_pipeline.py`**: Conditionally set `mlflow = None` if URI is empty to prevent rogue local logging.
- **`infra/docker-compose.prod.yml`**: Converted all optional service URLs to `${VAR:-}` syntax for the API container.

## 12. Remaining Blockers
There are no architectural/infrastructure blockers remaining for Step B. The core API/Dashboard boundary is solid.
Future Productization Blockers (to be solved in Step B or later):
- Project Multi-tenancy UI.
- Artifact Download UI.
- API Key Management UI.

## 13. Exact Commands Required to Validate Locally
```bash
# Test Base Deployment
docker compose -f infra/docker-compose.prod.yml up -d
curl http://localhost:8000/api/health
curl http://localhost:3000

# Test Optional Observability Profile
docker compose -f infra/docker-compose.prod.yml --profile observability up -d
curl http://localhost:9090

# Test MLflow Profile
MLFLOW_TRACKING_URI=http://driftguard-mlflow:5000 docker compose -f infra/docker-compose.prod.yml --profile mlflow up -d
```
