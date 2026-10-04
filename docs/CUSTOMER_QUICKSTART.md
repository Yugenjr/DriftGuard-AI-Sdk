# DriftGuard Customer Quickstart

Welcome to DriftGuard. This guide will help you install and configure your self-hosted DriftGuard control plane.

## 1. Prerequisites
- Docker and Docker Compose installed on your host machine.
- Minimum 4GB RAM available for the base profile.

## 2. Obtain DriftGuard
For now, DriftGuard is distributed via a `docker-compose.prod.yml` configuration.
1. Clone the DriftGuard repository or download the `infra/docker-compose.prod.yml` file.
2. Navigate to the `infra` directory:
```bash
cd driftguard/infra
```

## 3. Create Configuration (.env)
Create a `.env` file in the same directory as your `docker-compose.prod.yml` to set your secure credentials.
```env
# Database Credentials
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_secure_db_password
POSTGRES_DB=driftguard

# API and Dashboard Config
DRIFTGUARD_API_URL=http://localhost:8000
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Advanced Observability (Optional)
GF_SECURITY_ADMIN_PASSWORD=your_secure_grafana_password
```

## 4. Start the Minimal Stack
DriftGuard is designed to be modular. Start the base control plane (Dashboard, API, PostgreSQL, Redis) with:
```bash
docker compose -f docker-compose.prod.yml up -d
```
*(This will start the mandatory services. Kafka, Prefect, Grafana, and MLflow will NOT start unless requested).*

## 5. Open the Dashboard
Navigate to [http://localhost:3000](http://localhost:3000) in your browser.
You should see the DriftGuard Fleet Overview.

## 6. Create Account & Get API Key
1. Click **Sign Up**.
2. Enter your email and name.
3. Upon registration, you will be given an **API Key**. 
   > **IMPORTANT:** Copy this key immediately. It is only shown once and is hashed in the database.

## 7. Instrument Your Model (DriftGuard SDK)
Install the SDK in your Python environment where your model runs:
```bash
pip install driftguard
```
Initialize the SDK and wrap your model:
```python
from driftguard import DriftGuard

dg = DriftGuard(
    model_id="my-fraud-detector",
    api_url="http://localhost:8000",
    api_key="your_api_key_here"
)

# Wrap your existing model
tracked_model = dg.wrap(my_scikit_model)

# Run inference normally
predictions = tracked_model.predict(X_new)
```

## 8. View Telemetry
Return to the Dashboard at [http://localhost:3000](http://localhost:3000). Your model `my-fraud-detector` will automatically appear in the Fleet Overview, complete with drift charts and version history!

## Advanced / Optional Profiles
If you need extended observability or MLflow tracking, start the stack with profiles:
```bash
# Add Prometheus & Grafana
docker compose -f docker-compose.prod.yml --profile observability up -d

# Add MLflow & Prefect
docker compose -f docker-compose.prod.yml --profile orchestration --profile mlflow up -d
```
