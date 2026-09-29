"""
DriftGuard Canary Deployment & Progressive Delivery Pipeline.
Orchestrates BentoML and Ray Serve routing weight shifts, monitors live canary performance,
and triggers automatic rollbacks if performance SLAs are breached.
"""
import time
import os
import logging
from typing import Dict, Any, Tuple

try:
    import httpx
except ImportError:
    httpx = None

try:
    import mlflow
except ImportError:
    mlflow = None
from driftguard.config import settings
from driftguard.alert import send_alert

logger = logging.getLogger("DriftGuard.DeployPipeline")

def deploy_canary_challenger(
    model_id: str,
    new_version: str,
    challenger_model: Any,
    error_threshold: float = 0.05,  # 5%
    latency_threshold_ms: float = 500.0,  # 500ms
    simulation: bool = True
) -> bool:
    """
    Deploys challenger model progressively using a canary strategy.

    Args:
        model_id: Model ID being promoted.
        new_version: New model version string.
        challenger_model: Trained model artifact object.
        error_threshold: Max allowed error rate (e.g. 0.05 for 5%).
        latency_threshold_ms: Max allowed p99 latency in ms.
        simulation: If True, accelerates weights shifts and runs in dry-run mode for tests.

    Returns:
        True if promoted successfully to 100%, False if rolled back.
    """
    logger.info(f"Initiating Canary Deployment for '{model_id}' version {new_version}...")

    # 1. Register new model in MLflow Registry as Staging
    client = None
    try:
        if mlflow is not None:
            mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
            client = mlflow.tracking.MlflowClient()
            # Ensure model is registered (in local tests we might mock this)
            logger.info(f"Registering version {new_version} in MLflow Model Registry...")
            try:
                client.transition_model_version_stage(
                    name=model_id,
                    version=new_version,
                    stage="Staging"
                )
                logger.info("Successfully transitioned model version to Staging.")
            except Exception as reg_err:
                logger.warning(f"Could not update MLflow Registry stage: {reg_err}. Proceeding with local configuration.")
    except Exception as e:
        logger.warning(f"MLflow service unreachable: {e}")

    # 2. Canary traffic progression steps: 10% -> 25% -> 50% -> 100%
    canary_splits = [0.10, 0.25, 0.50, 1.00]
    step_duration_sec = 1 if simulation else (settings.CANARY_STEP_MINUTES * 60)

    for split in canary_splits:
        logger.info(f"Shifting traffic split: Challenger receives {split*100:.0f}% traffic.")

        # Save split percentage to Redis (for cross-process router)
        try:
            import redis
            r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)), db=0, socket_connect_timeout=2.0)
            r.set(f"canary_split_{model_id}", str(split))
        except Exception as e:
            logger.error(f"FATAL: Failed to write canary split state to Redis for {model_id}: {e}")
            rollback_canary(model_id)
            return False

        # Trigger audit update and alerts
        send_alert(
            event_type="canary_split_updated",
            message=f"Model '{model_id}' canary split increased to {split*100:.0f}%",
            details={"model_id": model_id, "version": new_version, "weight": f"{split*100:.0f}%"}
        )

        # 3. Monitor performance window
        # In a real environment, we would poll Prometheus metrics here.
        # We will simulate telemetry evaluation.
        time.sleep(step_duration_sec)

        # Mock metric query (or real Prometheus query if enabled)
        error_rate, latency_p99 = get_live_telemetry(model_id, new_version)

        # 4. Check Rollback conditions
        if error_rate > error_threshold or latency_p99 > latency_threshold_ms:
            logger.error(f"Canary split SLA breach! Error Rate: {error_rate*100:.2f}% (Limit: {error_threshold*100:.1f}%), p99 Latency: {latency_p99:.1f}ms (Limit: {latency_threshold_ms}ms)")

            # TRIGGER ROLLBACK
            rollback_canary(model_id)
            return False

    # If all steps succeeded, promote version to Production
    logger.info(f"Canary deployment succeeded! Promoting '{model_id}' version {new_version} to full Production.")
    if client is not None:
        try:
            client.transition_model_version_stage(
                name=model_id,
                version=new_version,
                stage="Production"
            )
        except Exception:
            pass

    return True

def get_live_telemetry(model_id: str, model_version: str) -> Tuple[float, float]:
    """
    Fetches real-time telemetry metrics scraping from Prometheus.
    Strictly forbids silent fallback to simulation.
    """
    use_prometheus = os.getenv("USE_PROMETHEUS_CANARY")
    allow_simulation = os.getenv("ALLOW_SIMULATED_CANARY")

    # 1. Enforce explicit configuration
    if use_prometheus == "true":
        pass  # Proceed to query Prometheus
    elif use_prometheus == "false" and allow_simulation == "true":
        return simulate_live_telemetry()
    else:
        raise ValueError("Configuration error: USE_PROMETHEUS_CANARY is missing or false, and ALLOW_SIMULATED_CANARY is not explicitly enabled. Cannot safely proceed with canary validation in production.")

    if httpx is None:
        raise ImportError("httpx is required for querying Prometheus.")

    prom_url = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
    query_url = f"{prom_url}/api/v1/query"

    def execute_query(prom_query: str) -> float:
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(query_url, params={"query": prom_query})
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Prometheus HTTP failure: {e}")
        except ValueError as e:
            raise RuntimeError(f"Prometheus invalid JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Prometheus connection error: {e}")

        if data.get("status") != "success":
            raise ValueError(f"Prometheus API status not success: {data}")

        results = data.get("data", {}).get("result", [])
        if not results:
            raise ValueError(f"Missing metric/result for query: {prom_query}")

        try:
            val_str = results[0]["value"][1]
            return float(val_str)
        except (KeyError, IndexError, TypeError, ValueError):
            raise ValueError(f"Malformed Prometheus result for query {prom_query}: {results}")

    # Query Canary Error Rate (derived from actual prediction error metrics, specific to canary)
    # Using existing driftguard_prediction_errors_total semantic where error_rate = errors / requests
    # Using increase() over the validation window to isolate this step's errors from historical deployments
    window = settings.CANARY_STEP_MINUTES
    errors_query = f'sum(increase(driftguard_prediction_errors_total{{model_id="{model_id}", model_version="{model_version}", deployment_stage="canary"}}[{window}m]))'
    requests_query = f'sum(increase(driftguard_predictions_total{{model_id="{model_id}", model_version="{model_version}", deployment_stage="canary"}}[{window}m]))'

    canary_errors = 0.0
    try:
        canary_errors = execute_query(errors_query)
    except ValueError as e:
        if "Missing metric/result" not in str(e):
            raise

    try:
        canary_traffic_count = execute_query(requests_query)
    except ValueError as e:
        if "Missing metric/result" in str(e):
            raise ValueError(f"No traffic/request count found for canary model {model_id}. Canary cannot be evaluated safely.")
        raise

    if canary_traffic_count <= 0:
        raise ValueError(f"No traffic/request count found for canary model {model_id}. Canary cannot be evaluated safely.")

    error_rate = canary_errors / canary_traffic_count

    # Query Canary Latency
    # Using inference latency histogram to derive p99 latency for canary ONLY over the validation window
    window = settings.CANARY_STEP_MINUTES
    p99_query = f'histogram_quantile(0.99, sum by (le) (increase(driftguard_inference_latency_seconds_bucket{{model_id="{model_id}", model_version="{model_version}", deployment_stage="canary"}}[{window}m])))'

    try:
        p99_latency_ms = execute_query(p99_query) * 1000.0
    except ValueError as e:
        if "Missing metric/result" in str(e):
            raise ValueError(
                f"No latency telemetry found for canary model {model_id} "
                f"version {model_version}. Canary cannot be evaluated safely."
            )
        raise

    return error_rate, p99_latency_ms

def simulate_live_telemetry() -> Tuple[float, float]:
    """
    Simulates real-time telemetry metrics scraping.
    """
    # Guard: Allow simulating a canary failure or real telemetry scraping using env vars
    if os.getenv("DEMO_CANARY_FAIL", "false").lower() == "true":
        return 0.12, 600.0  # Fails SLA checks (12% error rate, 600ms latency)

    # Healthy canary split telemetry defaults
    return 0.012, 42.0

def rollback_canary(model_id: str):
    """
    Performs emergency rollbacks, reverting traffic routing completely to the previous champion.
    """
    logger.warning(f"ROLLBACK INITIATED for model '{model_id}'! Reverting 100% traffic to production champion.")
    try:
        import redis
        r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)), db=0, socket_connect_timeout=2.0)
        r.set(f"canary_split_{model_id}", "0.0")
    except Exception:
        pass

    # Send Emergency Notification
    send_alert(
        event_type="rollback",
        message=f"CRITICAL: Canary deployment rolled back for model '{model_id}' due to SLA breach!",
        details={"model_id": model_id, "action": "reverted_to_champion"}
    )
