# DriftGuard Documentation Portal

Welcome to the documentation repository for the **DriftGuard MLOps Platform**. 

DriftGuard provides real-time model logging, telemetry streaming, statistical concept drift detection, and automated closed-loop retraining and rollback recovery.

---

## Documentation Index

Explore the platform's features, architecture, and use cases through these detailed guides:

### 🚀 Getting Started (Start Here)
If you are new to DriftGuard, follow this journey to get your first self-healing model running in under 10 minutes.
1. [**01. Installation Guide**](getting_started/01_installation.md): Deploying the Docker Hub images and installing the PyPI SDK.
2. [**02. Quickstart Tutorial**](getting_started/02_quickstart.md): Writing your first lines of code to wrap a FastAPI model.
3. [**03. Running & Checking**](getting_started/03_running_and_checking.md): Simulating drift locally and watching the dashboard spike.

### ⚙️ Core Concepts (The Engine)
Deep dives into the math and architecture powering the platform.
1. [**The Interceptor Lifecycle**](core_concepts/the_interceptor.md): Step-by-step lifecycle of a single prediction payload.
2. [**System Architecture & Security**](core_concepts/architecture.md): Detailed system components, multi-tenant security partitioning, and database entity relationships.
3. [**SDK & Telemetry Queue**](core_concepts/sdk_telemetry.md): Deep-dive into model wrapping, asynchronous queuing buffers, and worker threads.
4. [**Concept Drift Detection**](core_concepts/drift_detection.md): Mathematical walkthrough of the ADWIN algorithm and variance scoring.

### 📈 Advanced Workflows
For production MLOps engineers deploying automated CI/CD loops.
1. [**Retraining & Rollback Lifecycles**](advanced/retraining_rollback.md): Webhooks, Apache Airflow integration, and Champion/Challenger validation.
2. [**Application Use-Cases**](advanced/usecases.md): Real-world scenarios like Credit Fraud detection and SaaS multi-tenancy.
3. [**Full System Workflow Dump**](advanced/FULL_SYSTEM_WORKFLOW.md): Comprehensive, unedited workflow logs and internal architecture dumps.
