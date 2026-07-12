# Installation Guide

Welcome to DriftGuard! DriftGuard is composed of two parts: the **Platform** (Dashboard + API) and the **Python SDK**. You need to install both.

## 1. Deploy the Platform (Docker Hub)

The easiest way to get the dashboard and backend running is by pulling our pre-built, optimized production images directly from Docker Hub.

1. Clone the repository to get the docker-compose file:
```bash
git clone https://github.com/Yugenjr/DriftGuard-AI-Sdk.git
cd DriftGuard-AI-Sdk/infra
```

2. Start the platform using the production configuration:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

This single command boots up:
- The Obsidian Dashboard (Next.js)
- The Core API Gateway (FastAPI)
- PostgreSQL, Redis, Kafka, and Zookeeper

Your dashboard is now live at **http://localhost:3000**! 

> [!TIP]
> Navigate to the dashboard and click **Create Project** to generate your first Secret API Key. You will need this key for the next step.

## 2. Install the Python SDK

The DriftGuard Python SDK is extremely lightweight and is installed directly into your machine learning or inference environment.

```bash
pip install driftguard-ai-sdk
```

The SDK uses `httpx` to asynchronously stream telemetry to your platform without adding any latency to your model's predictions.

### What's Next?
Now that the platform is running and the SDK is installed, head over to the [Quickstart Guide](02_quickstart.md) to write your first line of code!
