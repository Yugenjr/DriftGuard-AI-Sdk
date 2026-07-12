Here is the exact step-by-step journey of what happens the moment an external user interacts with a model protected by DriftGuard!

1. The Invisible Interceptor
When a developer sets up DriftGuard, they wrap their model like this: wrapped_model = dg.wrap(my_model). From that moment on, DriftGuard acts as an invisible shield sitting directly in front of the model. When an external user interacts with your app (e.g. typing a prompt into a chatbot, or uploading an image), that data hits the DriftGuard wrapper first.

2. The ADWIN Mathematical Engine
As the user's data passes through the wrapper, DriftGuard doesn't just pass it to the model. It instantly runs the data through a mathematical algorithm called ADWIN (Adaptive Windowing). ADWIN is a highly optimized stream-processing algorithm. It calculates the statistical mean and variance of the incoming data in real-time, and mathematically compares it to the original data the model was trained on.

It asks one simple question: "Does the math of this new data look like the math of the old data?"

3. The Drift Score Calculation
ADWIN spits out a Drift Score (between 0.0 and 1.0).

If the external user is sending normal data, the score stays low (e.g., 0.02).
If the external user starts sending completely new concepts (like Spanish text instead of English, or pictures of cats instead of dogs), the mathematical distribution changes rapidly, and ADWIN spikes the score (e.g., 0.45).
4. What DriftGuard Does When It Detects Drift
The moment that Drift Score breaches your safety limit (e.g., drift_threshold = 0.15), DriftGuard instantly executes a 3-step action plan:

Fire the Retraining Signal: It immediately intercepts the execution flow and triggers your @dg.retrainer callback pipeline to start training a new model on fresh data to fix the problem.
Asynchronous Telemetry: Without slowing down the external user's request, DriftGuard uses a background thread to quietly POST the drift score, the user's raw data, and the model's prediction directly to your DriftGuard API backend.
Dashboard & Alerting: The API saves the telemetry to the database. Your dashboard instantly plots a massive spike on the live chart, logs an AUTOMATIC Retraining Event in the Audit Ledger, and (if hooked up) can fire off a Slack alert or Prometheus metric to wake up your MLOps engineers!