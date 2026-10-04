# DriftGuard Customer Product Flow Audit

## 1. Executive Summary

DriftGuard is currently in an **early transition phase** between an internal infrastructure orchestration engine and a commercial, customer-hosted software product. While the core "engine" (drift detection, telemetry ingestion, versioning, and rollback) is mathematically proven and robustly implemented in the backend, the customer deployment architecture and product boundaries are misaligned. 

Currently, the Docker deployment forces heavy infrastructure (Kafka, Zookeeper, MLflow) to run by default, while hiding the actual customer product (Dashboard, Grafana) behind a `--profile full` flag. The dashboard is functional but missing critical project management, artifact downloading, and API key management interfaces. Security is underdeveloped for a multi-tenant environment (missing RBAC, plaintext API key display risks). 

Overall Readiness: **PARTIALLY IMPLEMENTED (Prototype Phase)**. The foundation is solid, but the customer onboarding and deployment experience needs significant refactoring before commercial release.

## 2. Intended Customer Journey

| Step | Status | Notes |
| :--- | :--- | :--- |
| Purchase / obtain DriftGuard | UNCLEAR | No licensing or purchasing mechanism exists. |
| Deploy Docker stack | BROKEN | The current `docker-compose.prod.yml` starts Kafka/MLflow by default, but hides the Dashboard behind a `--profile full` flag. |
| Access dashboard | IMPLEMENTED + NOT VERIFIED | Requires `--profile full` to start. Port 3000 exposed. |
| Signup | IMPLEMENTED + VERIFIED | Functional via `/users/register`. |
| API key | IMPLEMENTED + VERIFIED | Generated and displayed upon signup. |
| Install SDK | IMPLEMENTED + VERIFIED | Python package structure exists (`driftguard/`). |
| Instrument model | IMPLEMENTED + VERIFIED | `dg.wrap()` mechanism works. |
| Register model | IMPLEMENTED + VERIFIED | Handled transparently by SDK on first use. |
| Run model & telemetry | IMPLEMENTED + VERIFIED | SDK successfully intercepts `predict()` and logs telemetry. |
| Drift detection | IMPLEMENTED + VERIFIED | Local SDK detection mechanism is proven. |
| Dashboard | PARTIALLY IMPLEMENTED | Shows metrics and drift, but lacks projects and artifact access. |
| Prometheus/Grafana | PARTIALLY IMPLEMENTED | Running in stack, but zero integration with DriftGuard UI. |
| Retraining | IMPLEMENTED + VERIFIED | Background tasks and webhooks work. |
| Artifact storage | PARTIALLY IMPLEMENTED | `ArtifactStore` supports Local and S3, but UI is completely missing. |
| Version management | IMPLEMENTED + VERIFIED | Dashboard and backend correctly handle champion/challenger tracking. |
| Rollback | IMPLEMENTED + VERIFIED | Working via Dashboard and API. |
| Cloud integrations | IMPLEMENTED + NOT VERIFIED | S3 `boto3` code exists but was not explicitly tested in the validation run. |

## 3. Customer Deployment Architecture

The current `docker-compose.prod.yml` defines the following:

| Service | Purpose | Must Run? | Current Config | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **driftguard-postgres** | Core metadata store | YES | Default | 5432 exposed. `pgdata` volume exists. |
| **driftguard-redis** | Feature store / Cache | YES | Default | 6379 exposed. |
| **driftguard-api** | Core Control Plane | YES | Default | 8000 exposed. |
| **driftguard-prometheus**| Telemetry TSDB | YES | Default | 9090 exposed. |
| **driftguard-dashboard** | Customer UI | YES | `profile: ["full"]` | **GAP:** Should be default. Port 3000. |
| **driftguard-grafana** | Advanced Observability | YES | `profile: ["full"]` | **GAP:** Should be default. Port 3001. |
| **driftguard-mlflow** | Experiment tracking | NO | Default | **GAP:** Should be optional/external. |
| **driftguard-zookeeper**| Kafka dependency | NO | Default | **GAP:** Should be optional/removed. |
| **driftguard-kafka** | Telemetry ingestion | NO | Default | **GAP:** Should be optional/removed. |
| **driftguard-prefect** | Pipeline orchestrator | NO | `profile: ["full"]` | Should remain optional. |

**Required Action:** Refactor `docker-compose.prod.yml` so that `postgres`, `redis`, `api`, `prometheus`, `grafana`, and `dashboard` start by default. Kafka, Zookeeper, MLflow, and Prefect should be moved to a `--profile full` or removed.

## 4. Dashboard Audit

| Feature | Status | Evidence / Missing Pieces | Required Action |
| :--- | :--- | :--- | :--- |
| Signup & Login | IMPLEMENTED | `/login` route works, uses `/users/register`. | None |
| API Key Retrieval | PARTIALLY IMPLEMENTED | Keys generated at signup. | Add "Settings" page to view/rotate keys. |
| Project Creation | MISSING | Backend supports projects, UI has no concept of them. | Build project selector/creator UI. |
| Model Creation | IMPLEMENTED | Auto-registered via SDK. | None |
| Model Details | IMPLEMENTED | `/models/[id].js` provides rich views. | None |
| Drift / Telemetry | IMPLEMENTED | `DriftChart.js` works. | None |
| Retraining State | IMPLEMENTED | `RetrainingHistory.js` works. | Add a "Force Retrain" manual button. |
| Rollback | IMPLEMENTED | Functional in `ModelVersions.js`. | None |
| Artifact Info | MISSING | No visibility into S3/Local `.pkl` files. | Add artifact download buttons and metadata view. |

## 5. SDK Customer Integration

The Python SDK (`driftguard`) acts as the bridge.
- **Initialization:** `dg = DriftGuard(model_id="...", api_url="...", api_key="...")`. 
- **Wrapping:** `model = dg.wrap(model)`.
- **Telemetry:** Automatically captured during `predict()`.
- **Retraining:** Driven by `RetrainerCallbackRunner`.
**Conclusion:** The SDK is realistically usable without understanding DriftGuard internals. It cleanly isolates the customer's model code from the MLOps infrastructure.

## 6. Model Lifecycle

`SDK init -> POST /register -> version 1.0.0 -> predict() -> telemetry logged -> drift detected -> POST /retrain -> challenger trained -> validation -> POST /retrain/.../complete -> version 1.0.1 -> Artifact saved -> Rollback (optional)`.

**Lifecycle Gaps:** The transition from Retraining to Artifact saving happens transparently, but the customer has no way to manually intervene or download the produced artifact from the dashboard before deciding to promote.

## 7. Artifact Management

- **Location:** Managed by `ArtifactStore` (`driftguard/artifact_store.py`).
- **Local FS:** Default (`ARTIFACT_ROOT=./artifacts`).
- **S3:** Implemented via `boto3` (`S3ArtifactStore`) using `s3://` URI prefix.
- **Persistence:** Survived container restarts in local mode during testing.
- **Versioning:** Strictly tied to `model_id` and `version` string.
- **Rollback:** `POST /rollback` successfully pulls the correct old artifact.
- **Customer S3:** Supported if they pass standard AWS environment variables to the API container (`AWS_ACCESS_KEY_ID`, etc.).

**Critical Gap:** Artifacts are completely invisible to the customer on the dashboard. They cannot be downloaded or inspected.

## 8. PostgreSQL / Persistence

Tables: `dg_users`, `dg_projects`, `dg_models`, `dg_model_versions`, `dg_retraining_events`, `dg_audit_logs`, `dg_predictions`.
- State survives container restart (via `pgdata` volume).
- Database is the sole source of truth for the Control Plane.

## 9. Observability

- **Prometheus:** Running. Scrapes `/metrics` from API. Exposes standard metrics (`driftguard_drift_score`, `driftguard_model_accuracy`, etc.). 
- **Grafana:** Provisioned in Compose, but completely disjointed from the DriftGuard Dashboard. 
- **Customer Visibility:** The customer sees drift in the custom Next.js UI, but must manually navigate to port 3001 to see Grafana. There is no SSO or iFrame integration.

## 10. Retraining / Workflow Integration

- **Internal Callback:** SDK supports local retraining (`RetrainerCallbackRunner`).
- **Webhooks:** The dashboard includes `WebhookConfig.js`. If set, DriftGuard POSTs to the webhook (e.g., Airflow/Prefect) upon drift.
- **Airflow/Prefect Specifics:** No deep integration. It's just a generic HTTP POST webhook. The external orchestrator is responsible for calling `/complete`.

## 11. AWS / Cloud Integration

- **S3 Storage:** IMPLEMENTED (via `boto3` in `ArtifactStore`).
- **IAM Roles:** IMPLEMENTED + NOT VERIFIED. `boto3` defaults to environment variables or IAM roles if running on EC2/ECS.
- **CloudWatch/EC2:** NOT IMPLEMENTED (DriftGuard doesn't manage infrastructure).

## 12. Security / Multi-Tenancy

- **API Keys:** Plaintext keys are never stored in DB (hashed via SHA256). Good practice.
- **Multi-tenancy:** `verify_model_access` correctly checks `owner_id`. However, the lack of a Project UI means everyone dumps into a default project.
- **RBAC:** MISSING. All registered users are effectively admins of their own models.
- **Secrets:** Dashboard API URL and Postgres credentials are hardcoded or passed insecurely in Compose.

## 13. Installation / Onboarding

**Missing Setup Documentation:**
A new customer cannot easily determine how to start the "Self-hosted monitoring mode". They would run `docker compose up -d` and realize the dashboard isn't running because it requires `--profile full`. They wouldn't know how to configure `s3://` artifact storage without digging into Python source code.

## 14. Docker Distribution

**Not Ready for Docker Hub.**
- The `docker-compose.prod.yml` uses `build: context: ..` for the API, MLflow, Prefect, and Evidently. This means it requires the source code to run. 
- To distribute to customers, we must publish pre-built images (e.g., `yugenjr/driftguard-api:latest`) and the customer's compose file should only reference images, not `build:` contexts.

## 15. Customer Cost / Operational Burden

- **REQUIRED:** API, PostgreSQL, Dashboard.
- **OPTIONAL (but recommended):** Prometheus, Grafana, Redis.
- **CAN BE REMOVED (High Burden):** Kafka, Zookeeper. (Using an HTTP `/telemetry` endpoint backed by Postgres/Redis is sufficient for 95% of users. Kafka forces massive memory overhead).
- **SHOULD NOT BE EXPOSED:** MLflow, Prefect. If the customer wants them, they should BYO (Bring Your Own) orchestrator via webhooks.

## 16. Exact Gap Matrix

| Capability | Status | What's Missing | Priority | Required Action |
| :--- | :--- | :--- | :--- | :--- |
| **Docker Compose Profiles** | BROKEN | Dashboard is hidden. Kafka is default. Requires source code. | P0 | Rewrite `docker-compose.yml` to use published images. Make Dashboard default. Remove Kafka. |
| **Artifact Dashboard UI** | MISSING | No way to see or download `.pkl` files. | P0 | Build `GET /artifacts` endpoint and "Download" buttons on Dashboard. |
| **Project Management UI** | MISSING | Backend supports projects, UI does not. | P1 | Add Project dropdown to Sidebar and Fleet pages. |
| **API Key Settings UI** | MISSING | Keys only visible once at signup. | P1 | Build Settings page to rotate keys. |
| **Manual Retrain UI** | MISSING | Can't force a retrain from the UI. | P2 | Add "Force Retrain" button to Model Details. |
| **Observability Deep-Links**| MISSING | Grafana exists but is disjointed. | P2 | Add "View in Grafana" links to Dashboard. |

## 17. Execution Validation Plan

- **S3 Artifact Validation:** Configure `.env` with real AWS credentials and `ARTIFACT_ROOT=s3://my-bucket/`. Run the `validate_retraining_workflow.py` script to prove S3 persistence works.
- **Multi-Tenant Validation:** Create User A and User B. Ensure User A cannot fetch User B's models via API.

## 18. Final Product Flow

**CURRENTLY POSSIBLE:**
Local SDK inference -> API Telemetry -> Postgres Metadata -> Dashboard Views.

**REQUIRED BEFORE COMMERCIAL RELEASE:**
`docker compose up -d` (pre-built images without Kafka) -> Dashboard (Project selection) -> API Key UI -> SDK Inference -> Dashboard (with Artifact downloading).

## 19. Do Not Build Yet

- **Do NOT build an internal Airflow/Prefect orchestrator.** Let the customer use Webhooks to connect their existing orchestrators.
- **Do NOT build a hosted/SaaS control plane.** Focus entirely on the self-hosted Docker deployment first.
- **Do NOT add Kafka/Zookeeper back into the default stack.** It's unnecessary operational overhead for a typical customer.
