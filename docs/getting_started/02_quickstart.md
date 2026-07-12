# Quickstart Guide

This guide will show you how to wrap your existing machine learning model with DriftGuard. DriftGuard acts as an invisible interceptor, analyzing incoming data for statistical drift without slowing down your predictions.

## Writing the Code

Here is a complete, copy-pasteable example of integrating DriftGuard into a standard FastAPI application.

```python
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.linear_model import LogisticRegression
from driftguard.tracker import DriftGuard

# ---------------------------------------------------------
# 1. Simulate an Existing Model
# ---------------------------------------------------------
# In reality, you would load this from a .pkl file
X_train = np.random.rand(100, 3)
y_train = np.random.randint(0, 2, 100)
model = LogisticRegression().fit(X_train, y_train)

# ---------------------------------------------------------
# 2. Initialize DriftGuard
# ---------------------------------------------------------
dg = DriftGuard(
    model_id="fraud-detector-v1",
    api_url="http://127.0.0.1:8000",
    api_key="dg-your-secret-key-from-dashboard", # Replace this!
    project_id=1,
    drift_threshold=0.30,
    expected_features=["transaction_amount", "location_score", "velocity"]
)

# Optional: Tell DriftGuard what the original training data looked like
# so it has a baseline to compare new data against.
dg.set_validation_data(X_train, y_train)

# Wrap your model!
wrapped_model = dg.wrap(model)

# ---------------------------------------------------------
# 3. Create your API endpoint
# ---------------------------------------------------------
app = FastAPI()

class Transaction(BaseModel):
    features: list[float]

@app.post("/predict")
def predict_fraud(transaction: Transaction):
    # Make a prediction using the WRAPPED model.
    # DriftGuard automatically intercepts this, calculates the drift score,
    # and POSTs the telemetry to your dashboard asynchronously!
    prediction = wrapped_model.predict([transaction.features])
    
    return {"fraud_probability": int(prediction[0])}
```

## How it works

When a user sends a POST request to `/predict`:
1. The `wrapped_model.predict()` function is called.
2. DriftGuard calculates the statistical variance of `transaction.features` compared to your original training data.
3. DriftGuard executes a non-blocking HTTP POST request to your API Gateway to log the telemetry.
4. Your application instantly returns the `prediction` to the user with zero added latency.

### What's Next?
Now that your code is written, let's learn how to manually trigger drift and [watch the dashboard spike in real-time](03_running_and_checking.md).
