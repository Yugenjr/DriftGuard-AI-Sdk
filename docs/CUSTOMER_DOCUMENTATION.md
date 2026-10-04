# DriftGuard Platform: Customer Quickstart & Golden Path

Welcome to DriftGuard. DriftGuard is a self-hosted control plane for Machine Learning observability, automated drift detection, and continuous retraining. 
This guide walks you through the entire lifecycle of a model on DriftGuard from first launch to self-healing rollback.

## 1. Starting DriftGuard

DriftGuard is designed to be hosted in your own infrastructure. Start the base stack with Docker Compose:

```bash
docker compose -f infra/docker-compose.prod.yml up -d
```
*This starts the DriftGuard Dashboard, API Gateway, PostgreSQL, and Redis.*

## 2. Opening the Dashboard
Open your browser and navigate to `http://localhost:3000`. You will be automatically redirected to the login page.

## 3. Creating an Account
Click **Sign Up** on the login screen.
Enter your name and email. 
Upon successful registration, your first **API Key** will be generated and shown to you. **Copy it immediately** — you will need it for the SDK!

## 4. Creating a Project
1. In the sidebar, open the Project Selector dropdown.
2. Click **+ New Project**.
3. Name your project (e.g., `Fraud Detection`).
4. Select the new project from the dropdown. All models registered will now be scoped to this project.

## 5. Managing Your API Key
If you missed copying your API Key during signup:
1. Navigate to **System Settings** in the sidebar.
2. Scroll to the **Danger Zone** and click **Rotate Key**. 
3. Copy the newly generated key. *(Warning: This invalidates your old key).*

## 6. Installing the SDK
In your ML model's Python environment, install DriftGuard:

```bash
pip install -e .
```

## 7. Configuring the SDK
Configure your `DriftGuardClient` (or Tracker) in your Python code:

```python
import driftguard as dg

tracker = dg.DriftGuardTracker(
    model_id="fraud-model-prod",
    project_id=1,           # Found in your dashboard
    api_key="dg-...",       # Your API key
    drift_threshold=0.20
)
```

## 8. Registering a Model
When you initialize the `DriftGuardTracker` and call `tracker.register()`, DriftGuard creates the model in the Dashboard under your active project and creates a placeholder `v1.0.0` artifact.

## 9. Viewing Telemetry
As your model makes predictions, log them:
```python
tracker.predict(features, model_prediction)
```
In the Dashboard, navigate to **Model Metrics** -> your model. You will see real-time drift scores plotted on the chart.

## 10. Understanding Drift
If the drift score crosses your `drift_threshold` (e.g., 0.20), the system transitions the model state to `degraded`.

## 11. Understanding Retraining
Upon degradation, if a retrain callback is registered:
```python
@dg.retrainer(model_id="fraud-model-prod")
def my_retraining_logic():
    # Fetch new data, train model, return it
    return new_model
```
DriftGuard automatically executes this in the background, validating the new challenger model against the degraded champion.

## 12. Viewing Versions
In the Dashboard, scroll to the **Model Version Registry**. You will see:
- `v1.0.0` (Archived, if a new version was promoted)
- `v1.0.1` (Champion, if the challenger succeeded)

## 13. Downloading Artifacts
In the Model Version Registry table, click the **.pkl** download button next to any version to download the actual model binary from your DriftGuard artifact storage (Local or S3).

## 14. Rolling Back
If `v1.0.1` performs poorly in production, click the **Rollback** button next to `v1.0.0`. DriftGuard will immediately restore `v1.0.0` as the active champion and record an audit log event.

## 15. Optional Integrations
You can enable heavier integrations by restarting Docker Compose with profiles:
- **MLflow**: `docker compose -f infra/docker-compose.prod.yml --profile mlflow up -d`
- **Observability**: `docker compose -f infra/docker-compose.prod.yml --profile observability up -d`
