# Running and Checking

Now that your DriftGuard platform is running and your FastApi model is wrapped, it's time to see DriftGuard in action!

## 1. Start your API
Assuming you saved the code from the [Quickstart Guide](02_quickstart.md) as `app.py`, start your FastAPI server:

```bash
uvicorn app:app --reload --port 8080
```

## 2. Simulate Normal Traffic (Healthy State)
Let's send some normal, expected data to your model. Open a new terminal and run this `curl` command a few times:

```bash
curl -X POST "http://localhost:8080/predict" \
     -H "Content-Type: application/json" \
     -d '{"features": [0.5, 0.4, 0.6]}'
```

**Check the Dashboard:**
1. Open your browser to **http://localhost:3000**
2. Click on your `fraud-detector-v1` model card.
3. You should see a green **HEALTHY** badge. The Drift Score chart will show a very low variance (e.g., `0.02`), indicating that the incoming data matches the training data.

## 3. Simulate Data Drift (SLA Breach)
Now, let's pretend a new type of fraud has emerged, or an upstream data pipeline broke, causing the features to change drastically.

Send heavily skewed data:
```bash
curl -X POST "http://localhost:8080/predict" \
     -H "Content-Type: application/json" \
     -d '{"features": [9.9, -5.2, 14.8]}'
```
Run this command 5-10 times rapidly to simulate a flood of bad data.

**Check the Dashboard:**
1. Watch the dashboard in real-time.
2. The ADWIN statistical engine will detect the sudden shift in variance.
3. The Drift Score chart will spike dramatically (e.g., `0.45`).
4. Once the score crosses your `drift_threshold` (e.g., `0.30`), the badge will instantly turn amber and read **DRIFTING (SLA BREACH)**.

## 4. The Automated Response
If you configured a Webhook URL in your dashboard settings, DriftGuard just fired a POST request to your orchestration tool (like Apache Airflow or GitHub Actions) telling it to begin retraining the model!

You can view this automated response by checking the **Audit Log** tab on your dashboard, which will show an `Automated Retraining Triggered` event.

---
Congratulations! You have successfully deployed a self-healing AI pipeline. To learn how to connect DriftGuard to Airflow for automated retraining, read the [Retraining & Rollback Guide](../advanced/retraining_rollback.md).
