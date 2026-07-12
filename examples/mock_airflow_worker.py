import uvicorn
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import time
import httpx
import sys

app = FastAPI(title="Mock Airflow Webhook Server")

class WebhookPayload(BaseModel):
    event_id: int
    model_id: str
    drift_score: float
    callback_url: str

def simulate_heavy_gpu_training(payload: WebhookPayload):
    print(f"\n[Airflow Worker] Starting heavy GPU training job for {payload.model_id}...")
    print(f"[Airflow Worker] Event ID: {payload.event_id} | Drift Score: {payload.drift_score}")
    
    # Simulate time-consuming GPU job (5 seconds)
    for i in range(5):
        print(f"[Airflow Worker] Epoch {i+1}/5 - Loss: {0.5 / (i+1):.4f}...")
        time.sleep(1)
        
    print(f"[Airflow Worker] Training complete! Promoting new Challenger model...")
    
    # Send completion POST back to DriftGuard
    complete_payload = {
        "event_id": payload.event_id,
        "new_accuracy": 0.85, # 85% accuracy simulation
        "model_artifact_path": "s3://driftguard-artifacts/new_model.pkl",
        "training_metadata": {"epochs": 5, "final_loss": 0.1, "hardware": "AWS A100"}
    }
    
    print(f"[Airflow Worker] Pinging DriftGuard callback URL: {payload.callback_url}")
    try:
        # Include a dummy API key for testing if main.py enforces it (it does)
        # We will use the same test key used in nlp_real_example.py
        api_key = "dg-6e679a28560cb4e9487ef4bd04f7e806"
        headers = {"X-API-Key": api_key}
        
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(payload.callback_url, json=complete_payload, headers=headers)
            print(f"[Airflow Worker] DriftGuard Callback Response: {resp.status_code}")
    except Exception as e:
        print(f"[Airflow Worker] Failed to callback DriftGuard: {e}")

@app.post("/api/v1/dags/retrain_model/dagRuns")
def trigger_dag(payload: WebhookPayload, background_tasks: BackgroundTasks):
    print(f"\n=======================================================")
    print(f"[Airflow API] Received Webhook Trigger for model: {payload.model_id}")
    print(f"=======================================================")
    
    # Offload the heavy work to a background task so the webhook returns instantly (200 OK)
    background_tasks.add_task(simulate_heavy_gpu_training, payload)
    
    return {"status": "dag_triggered", "message": "Airflow DAG queued successfully."}

if __name__ == "__main__":
    print("Starting Mock Airflow Worker on port 8001...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
