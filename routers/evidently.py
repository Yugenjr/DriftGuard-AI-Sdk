import numpy as np
from fastapi import APIRouter, HTTPException
from main import EvidentlyCalculateRequest

router = APIRouter(prefix="/evidently", tags=["Evidently Calculations"])

@router.post("/calculate", summary="Isolated Evidently calculations REST endpoint")
def calculate_evidently_drift_endpoint(req: EvidentlyCalculateRequest):
    """
    Computes statistical data drift using local evidently packages.
    Runs inside the isolated Evidently service container.
    """
    try:
        import pandas as pd
        ref_df = pd.DataFrame(req.reference_data)
        cur_df = pd.DataFrame(req.current_data)
        
        from driftguard.drift_detector import EVIDENTLY_AVAILABLE
        if not EVIDENTLY_AVAILABLE:
            raise HTTPException(status_code=500, detail="Evidently library not installed inside this container.")
            
        from driftguard.drift_detector import Report, DataDriftPreset, TargetDriftPreset
        metrics = [DataDriftPreset()]
        if req.target_column and req.target_column in ref_df.columns:
            metrics.append(TargetDriftPreset())
            
        report = Report(metrics=metrics)
        report.run(reference_data=ref_df, current_data=cur_df)
        result = report.as_dict()
        
        drift_metrics = {}
        overall_drift_detected = False
        drift_data = result["metrics"][0]["result"]
        for feature, detail in drift_data["drift_by_columns"].items():
            drift_score = detail["drift_score"]
            drift_detected = detail["drift_detected"]
            if drift_detected:
                overall_drift_detected = True
            drift_metrics[feature] = {
                "drift_score": float(drift_score),
                "drift_detected": bool(drift_detected),
                "metric_name": detail["test_name"]
            }
            
        scores = [v["drift_score"] for v in drift_metrics.values()]
        overall_drift_score = float(np.mean(scores)) if scores else 0.0
        
        return {
            "drift_detected": overall_drift_detected,
            "metrics": drift_metrics,
            "overall_drift_score": overall_drift_score
        }
    except Exception as e:
        # Clean response message detailing calculations error while hiding traceback details
        raise HTTPException(status_code=500, detail=f"Evidently calculation error: {str(e)}")
