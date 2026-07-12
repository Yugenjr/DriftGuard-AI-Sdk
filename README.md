<div align="center">
  <h1>🛡️ DriftGuard AI</h1>
  <p><strong>Self-Healing MLOps & Autonomous Retraining Platform</strong></p>
  
  [![PyPI version](https://badge.fury.io/py/driftguard-ai-sdk.svg)](https://badge.fury.io/py/driftguard-ai-sdk)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

<br />

DriftGuard is a production-grade observability platform that detects **data drift**, **concept drift**, and **model degradation** in real-time, automatically triggering CI/CD retraining loops (like Apache Airflow) to heal your AI pipelines with zero human intervention.

## 🌟 Features

- **Real-Time Telemetry:** Asynchronous, non-blocking telemetry logging that adds zero latency to your inference APIs.
- **Enterprise Dashboard:** A stunning, Vercel-inspired observability dashboard to monitor your entire fleet of models in real-time.
- **Self-Healing Webhooks:** Automatically fire POST payloads to your orchestrator (Airflow, Kubeflow, SageMaker) when SLA thresholds are breached.
- **Multi-Tenant Security:** Securely isolate telemetry data by project using hashed API keys.

---

## 🚀 Quickstart: Bring Your Own Server

You can run the entire DriftGuard platform on your own infrastructure for free using Docker.

### 1. Start the Platform
Clone this repository and spin up the backend and frontend simultaneously using our highly optimized, pre-built Docker Hub images:
```bash
git clone https://github.com/Yugenjr/DriftGuard-AI-Sdk.git
cd DriftGuard-AI-Sdk/infra
docker-compose -f docker-compose.prod.yml up -d
```
Your dashboard is now live at **http://localhost:3000**! Go create your first API key.

### 2. Install the SDK
Install the lightweight Python SDK into your inference environment:
```bash
pip install driftguard-ai-sdk
```

### 3. Wrap your Model
Import the SDK and initialize it in your FastAPI/Flask app:

```python
from fastapi import FastAPI
from driftguard import DriftGuard

# 1. Initialize DriftGuard
dg = DriftGuard(
    model_id="fraud-detector-v1",
    api_key="dg-your-secret-key",
    drift_threshold=0.15,
    expected_features=["amount", "location_score", "velocity"]
)

app = FastAPI()

@app.post("/predict")
def predict(features: list[float]):
    prediction = model.predict([features])
    
    # 2. Log telemetry asynchronously (Non-blocking)
    dg.log_prediction(
        features=features,
        prediction=prediction
    )
    
    return {"fraud_probability": prediction}
```

---

## 🏗 Architecture

```text
                     +---------------------------------------+
                     |          Client Application           |
                     +-------------------+-------------------+
                                         |
                                (Predict Telemetry)
                                         v
                     +-------------------+-------------------+
                     |          DriftGuard SDK               |
                     |  - Wrapper pattern intercept          |
                     |  - River ADWIN concept drift checks   |
                     +-------------------+-------------------+
                                         |
                                 (HTTP Telemetry)
                                         v
                     +-------------------+-------------------+
                     |       DriftGuard FastAPI Core API     | <---+ NextJS Dashboard (:3000)
                     |       - /register, /predict, /drift   | <---+ Grafana (:3001)
                     |       - Prom metrics /metrics (:8000) |
                     +-------------------+-------------------+
                                         |
                        (SLA Drift Breach Trigger)
                                         v
                     +-------------------+-------------------+
                     |      Prefect Orchestration Server     |
                     |      - drift_detection_flow (:4200)   |
                     +-------------------+-------------------+
                                         |
                                 (Runs steps)
                                         v
                     +-------------------+-------------------+
                     |      ZenML Step Training Pipelines    |
                     |  - Step 1: Great Expectations Validate|
                     |  - Step 2: Feast Feature Store Check  |
                     |  - Step 3: Train & Track (MLflow/W&B) |
                     |  - Step 4: Validate (>1% boost check) |
                     |  - Step 5: Canary Progressive Deploy  |
                     |  - Step 6: Immutable JSON Ledger & PDF|
                     +-------------------+-------------------+
                                         |
                            (Progressive Split Promotes)
                                         v
                     +-------------------+-------------------+
                     |       BentoML & Ray Serve Fleet       |
                     |       - canary_router: 10%->100%      |
                     |       - SLA Monitoring & Rollbacks    |
                     +---------------------------------------+
```

DriftGuard is composed of three main components:
1. **The Python SDK (`driftguard/`)**: A lightweight client that intercepts inferences and streams telemetry.
2. **The FastAPI Engine (`main.py`)**: A high-concurrency event processor backed by PostgreSQL for state management.
3. **The Obsidian Dashboard (`dashboard/`)**: A Next.js (React) front-end providing a breathtaking developer experience.

## 🤝 Contributing
We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to set up your local development environment.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
