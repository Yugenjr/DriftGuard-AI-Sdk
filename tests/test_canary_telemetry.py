import os
import pytest
from unittest.mock import patch, MagicMock
from pipeline.deploy_pipeline import get_live_telemetry

def test_simulation_only_when_explicitly_allowed():
    # Production configuration missing USE_PROMETHEUS_CANARY and ALLOW_SIMULATED_CANARY
    with patch.dict(os.environ, {"USE_PROMETHEUS_CANARY": "", "ALLOW_SIMULATED_CANARY": ""}):
        with pytest.raises(ValueError, match="Configuration error.*Cannot safely proceed with canary validation in production"):
            get_live_telemetry("model1", "1.0.5")

    # Simulation allowed explicitly
    with patch.dict(os.environ, {"USE_PROMETHEUS_CANARY": "false", "ALLOW_SIMULATED_CANARY": "true"}):
        with patch("pipeline.deploy_pipeline.simulate_live_telemetry", return_value=(0.012, 42.0)):
            error_rate, latency = get_live_telemetry("model1", "1.0.5")
            assert error_rate == 0.012
            assert latency == 42.0

def test_successful_prometheus_query():
    with patch.dict(os.environ, {"USE_PROMETHEUS_CANARY": "true", "PROMETHEUS_URL": "http://prometheus:9090"}):
        # Mock httpx client
        def mock_get(url, params):
            query = params["query"]
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()

            if "driftguard_prediction_errors_total" in query and "increase" in query and "canary" in query and 'model_version="1.0.5"' in query:
                # 5 canary errors
                mock_resp.json.return_value = {"status": "success", "data": {"result": [{"value": [1234, "5.0"]}]}}
            elif "driftguard_predictions_total" in query and "increase" in query and "canary" in query and 'model_version="1.0.5"' in query:
                # 100 canary requests
                mock_resp.json.return_value = {"status": "success", "data": {"result": [{"value": [1234, "100.0"]}]}}
            elif "driftguard_inference_latency_seconds_bucket" in query and "histogram_quantile" in query and "canary" in query and 'model_version="1.0.5"' in query:
                # p99 latency 0.05 seconds for canary
                mock_resp.json.return_value = {"status": "success", "data": {"result": [{"value": [1234, "0.05"]}]}}
            return mock_resp

        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.side_effect = mock_get

        with patch("httpx.Client", return_value=mock_client):
            error_rate, latency_p99 = get_live_telemetry("model1", "1.0.5")
            # 5 errors / 100 reqs = 0.05
            assert error_rate == pytest.approx(0.05)
            # 0.05 seconds = 50.0 ms
            assert latency_p99 == pytest.approx(50.0)

def test_prometheus_http_failure():
    with patch.dict(os.environ, {"USE_PROMETHEUS_CANARY": "true"}):
        import httpx
        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.side_effect = httpx.HTTPError("Connection failed")

        with patch("httpx.Client", return_value=mock_client):
            with pytest.raises(RuntimeError, match="Prometheus HTTP failure"):
                get_live_telemetry("model1", "1.0.5")

def test_zero_traffic_count_raises_error():
    with patch.dict(os.environ, {"USE_PROMETHEUS_CANARY": "true"}):
        def mock_get(url, params):
            query = params["query"]
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()

            if "driftguard_prediction_errors_total" in query and "increase" in query:
                mock_resp.json.return_value = {"status": "success", "data": {"result": [{"value": [1234, "0.0"]}]}}
            elif "driftguard_predictions_total" in query and "increase" in query:
                # 0 traffic count for canary!
                mock_resp.json.return_value = {"status": "success", "data": {"result": [{"value": [1234, "0"]}]}}
            elif "driftguard_inference_latency_seconds_bucket" in query and "histogram_quantile" in query:
                mock_resp.json.return_value = {"status": "success", "data": {"result": [{"value": [1234, "0.0"]}]}}
            return mock_resp

        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.side_effect = mock_get

        with patch("httpx.Client", return_value=mock_client):
            with pytest.raises(ValueError, match="No traffic/request count found"):
                get_live_telemetry("model1", "1.0.5")

def test_missing_latency_raises_error():
    with patch.dict(os.environ, {"USE_PROMETHEUS_CANARY": "true"}):
        def mock_get(url, params):
            query = params["query"]
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()

            if "driftguard_prediction_errors_total" in query and "increase" in query:
                mock_resp.json.return_value = {"status": "success", "data": {"result": [{"value": [1234, "0.0"]}]}}
            elif "driftguard_predictions_total" in query and "increase" in query:
                mock_resp.json.return_value = {"status": "success", "data": {"result": [{"value": [1234, "10.0"]}]}}
            elif "driftguard_inference_latency_seconds_bucket" in query and "histogram_quantile" in query:
                # Missing latency!
                mock_resp.json.return_value = {"status": "success", "data": {"result": []}}
            return mock_resp

        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.side_effect = mock_get

        with patch("httpx.Client", return_value=mock_client):
            with pytest.raises(ValueError, match="No latency telemetry found for canary model"):
                get_live_telemetry("model1", "1.0.5")

def test_redis_write_failure_aborts_deployment():
    import sys
    from pipeline.deploy_pipeline import deploy_canary_challenger
    # Simulate Redis connection failure without relying on the real module being installed
    mock_redis_module = MagicMock()
    mock_redis_class = MagicMock()
    mock_redis_class.return_value.set.side_effect = Exception("Redis Down")
    mock_redis_module.Redis = mock_redis_class
    sys.modules["redis"] = mock_redis_module

    # We need to mock rollback_canary to ensure it's called
    with patch("pipeline.deploy_pipeline.rollback_canary") as mock_rollback:
        # deploy_pipeline should return False immediately
        result = deploy_canary_challenger("model1", "1.0.5", None)
        assert result is False
        mock_rollback.assert_called_once_with("model1")

def test_redis_read_failure_aborts_routing():
    import sys
    from serving.canary_router import get_canary_split_weight

    mock_redis_module = MagicMock()
    mock_redis_class = MagicMock()
    mock_redis_class.return_value.get.side_effect = Exception("Redis Down")
    mock_redis_module.Redis = mock_redis_class
    sys.modules["redis"] = mock_redis_module

    with patch.dict(os.environ, {"ALLOW_SIMULATED_CANARY": "false"}):
        # The routing should fail-closed and raise RuntimeError, not fallback silently
        with pytest.raises(RuntimeError, match="Canary routing failed: Redis state unavailable"):
            get_canary_split_weight("model1")
