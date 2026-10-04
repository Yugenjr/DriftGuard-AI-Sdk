# DriftGuard Self-Hosted Deployment Validation

## Deployment Overview
**Command:** 
```bash
docker compose -f infra/docker-compose.prod.yml up -d
```

**Running Services (Base Profile):**
- `driftguard-postgres` (PostgreSQL 15)
- `driftguard-redis` (Redis 7)
- `driftguard-api` (FastAPI Control Plane)
- `driftguard-dashboard` (Next.js UI)

**Optional Profiles Supported:**
- `--profile observability`: Starts Prometheus and Grafana.
- `--profile messaging`: Starts Kafka and Zookeeper.
- `--profile orchestration`: Starts Prefect.
- `--profile mlflow`: Starts MLflow.
- `--profile evidently`: Starts Evidently Statistical Service.

## Health Checks & Dependencies
- `postgres`: Checked via `pg_isready` before API/MLflow/Prefect start.
- `redis`: Checked via `redis-cli ping` before API starts.
- `api`: Checked via `curl /api/health` before Dashboard starts.
- `dashboard`: Checked via `curl localhost:3000`.

## Persistent Volumes
1. `pgdata`: Ensures all model metadata, users, versions, and audit logs survive container restart.
2. `prometheus-data`: (Optional) Preserves historical TSDB metrics.
3. `grafana-data`: (Optional) Preserves dashboard configurations.

## Network Architecture & Exposed Ports
- **Publicly Exposed (Host Bound):**
  - Dashboard: `3000`
  - API: `8000`
  - PostgreSQL: `5432` (Only if required for external inspection, could be removed for tighter security).
  - Redis: `6379`
- **Internal Only:** None currently explicitly defined via a custom Docker network (relies on default Compose network isolation).

## E2E Validation Result
**Status:** UNVERIFIED (Environment Issue)
**Reason:** The host running the validation agent did not have an active Docker Daemon (`error: failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`). 
**Next Steps:** The E2E tests (`validation/validate_retraining_workflow.py`) must be executed manually on a host with an active Docker engine to confirm the new Base Profile supports the full orchestration lifecycle.

## Known Limitations (For Phase B)
1. **Artifact Dashboard Missing:** The UI does not expose `.pkl` artifacts for download.
2. **Project Isolation:** The backend API supports project IDs, but the Dashboard does not have a Project Selector.
3. **API Key Rotation:** No settings UI exists to rotate API keys; they are generated once on `/register`.
4. **Local Build Context:** The `docker-compose.prod.yml` still relies on a local `build: context: ..` block for `driftguard-api` and `driftguard-dashboard`. True Docker Hub readiness requires a CI/CD pipeline to publish these images and removing the `build` blocks entirely.
