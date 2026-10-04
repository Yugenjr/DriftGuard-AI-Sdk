# DriftGuard Production Validation: End-to-End Readiness Matrix

## Production Readiness Audit

| Component | Current Implementation | Works Locally? | Production-ready? | Missing Pieces | Required Change | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FastAPI Backend** | Fully implemented in `main.py` and `routers/` | Yes | Yes | None | None | IMPLEMENTED |
| **DriftGuard SDK** | Fully implemented in `driftguard/` | Yes | Yes | None | None | IMPLEMENTED |
| **Kafka Producer** | `confluent_kafka` logic inside SDK | Yes | Yes | None | None | IMPLEMENTED |
| **Kafka Consumer** | Threaded loop in `main.py` (`kafka_consumer_loop`) | Yes | Yes | None | None | IMPLEMENTED |
| **PostgreSQL** | SQLAlchemy ORM configured. SQLite fallback exists. | Yes | Yes | None | Ensure `DATABASE_URL` connects to real PG | IMPLEMENTED |
| **Redis** | Present in compose, used for Feast feature store | Simulated/Local | No | Real caching/Feature Store link | Configure Feast to use Redis | PARTIALLY IMPLEMENTED |
| **MLflow** | Built into pipeline scripts, UI runs in compose | Yes | Yes | AWS S3 Backend | Configure `MLFLOW_TRACKING_URI` and Artifact Root to S3 | PARTIALLY IMPLEMENTED |
| **Prefect** | Missing from active workflow | No | No | Workflow definitions | Convert `retrain_pipeline.py` to Prefect tasks (Optional for this phase) | MISSING |
| **Prometheus** | Metric collectors defined, `generate_latest` in `main.py` | Yes | Yes | Real telemetry feed for Canary | Wire real Canary logic to Prometheus | PARTIALLY IMPLEMENTED |
| **Grafana** | `infra/grafana` folder exists | Yes | Yes | Dashboards | Configure dashboards to read new metrics | IMPLEMENTED |
| **Evidently** | Integrated in monitoring/ | Yes | Yes | None | None | IMPLEMENTED |
| **Artifact Storage** | Hardcoded to local `ARTIFACT_ROOT` in `config.py` | Yes | No | S3 Abstraction | Create `ArtifactStore` abstraction for S3 / Local | PARTIALLY IMPLEMENTED |
| **Model Registration** | API routes exist | Yes | Yes | None | None | IMPLEMENTED |
| **Drift Detection** | Core engine works | Yes | Yes | Real data stream | Route real user traffic through SDK | IMPLEMENTED |
| **Retraining** | SDK triggers callback or webhook | Yes | Yes | Real data loader | Connect retraining callback to real S3 dataset | IMPLEMENTED |
| **Champion/Challenger**| Math logic is sound in `validation.py` | Yes | Yes | None | None | IMPLEMENTED |
| **Model Versioning** | DB logic exists | Yes | Yes | None | None | IMPLEMENTED |
| **Canary Deployment** | Defined in `deploy_pipeline.py` | Simulated | No | Real Prometheus metrics | Replace `simulate_live_telemetry()` with Prometheus queries | SIMULATED |
| **Rollback** | API route exists and works | Yes | Yes | None | Fix ArtifactStore to pull from S3 | IMPLEMENTED |
| **Docker Compose** | `docker-compose.prod.yml` exists | Yes | Yes | S3 creds, MLflow integration | Create isolated `.env.prod` | IMPLEMENTED |

## Phase 0: Plan & Architecture

**WHAT ALREADY EXISTS:**
- Complete core backend, SDK, database versioning, rollback, and mathematical champion/challenger logic.
- Production `docker-compose.prod.yml` provisioning Postgres, Kafka, Zookeeper, and MLflow.
- Kafka producer/consumer code inside the SDK and FastAPI respectively.
- Prometheus `Counter`, `Gauge`, and `/metrics` exports.

**WHAT IS MISSING:**
- `ArtifactStore` interface to handle both `s3://` and `./artifacts/`.
- S3 bucket for model artifacts and MLflow default artifact root.
- A **Real ML Model** Server (`live_demo/app.py`) taking real HTTP traffic.
- Real Canary routing logic backed by actual Prometheus metrics instead of `simulate_live_telemetry()`.
- Isolated `.env.prod` to ensure local development remains untouched.

**WHAT WE ARE CHANGING:**
1. Creating `live_demo/app.py` for real HTTP inference.
2. Building an `ArtifactStore` class to push `.pkl` files to S3.
3. Removing `simulate_live_telemetry()` and querying the real Prometheus endpoint.
4. Setting up `.env.prod` to run `docker-compose -p driftguard-prod -f infra/docker-compose.prod.yml up`.

**WHY IT IS NEEDED:**
To prove the end-to-end autonomous lifecycle in a cloud-native architecture without using mocks, ensuring we don't break local fallback logic.

**HOW WE WILL VERIFY IT:**
We will spin up the isolated prod stack, hit the live model with real data, trigger real drift, watch Kafka transport it, observe MLflow log the real training run, see S3 store the new model, and watch the canary use real Prometheus metrics to promote it.

## Prefect Production Dependency Validation (2026-10-04)

- **Root Cause:** Prefect 2.19.0 requires `pendulum <3.0`. On Python 3.11, installing `pendulum==2.1.2` triggers source builds which fail or exhaust memory on resource-constrained EC2 hosts.
- **Python Version Selected for Prefect:** 3.10 (provides pre-built wheels for `pendulum==2.1.2`).
- **Prefect Version:** 2.19.0 (pinned explicitly).
- **Pendulum Version:** 2.1.2 (pinned explicitly).
- **Successful Import Verification:** Pending (Requires execution on EC2 host, local Docker daemon unavailable).
- **Successful Container Startup:** Pending (Requires execution on EC2 host).
- **Healthcheck Result:** Pending (Requires execution on EC2 host).
- **Production Validation Test Result:** Pending (Executed local `pytest tests/` successfully, but full docker test requires EC2).
- **Date/Time of Validation:** 2026-10-04.
- **Limitations that remain:** Local Docker daemon was unavailable. Final verification of the Prefect container startup and healthcheck must be performed directly on the target EC2 instance.
