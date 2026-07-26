"""
DriftGuard Demo Test — Champion vs Challenger Pipeline
=======================================================
Phase 1 : 50% data with medium drift  → model starts degrading
Phase 2 : 100% data with heavy drift  → drift threshold breached,
           retraining fires, challenger beats champion and gets promoted.
"""
import time
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from driftguard import DriftGuard

# ──────────────────────────────────────────────
# 0.  Config
# ──────────────────────────────────────────────
API_URL    = "http://localhost:8000"
API_KEY    = "dg-b78ddaa2f14565939175e68896671883"
MODEL_ID   = f"demo-champion-{int(time.time())}"
PROJECT_ID = 5   # created via POST /projects

print("=" * 60)
print(f"  DriftGuard Demo")
print(f"  Model ID : {MODEL_ID}")
print("=" * 60)

# ──────────────────────────────────────────────
# 1.  Generate dataset
# ──────────────────────────────────────────────
X, y = make_classification(
    n_samples=1500,
    n_features=8,
    n_informative=6,
    n_redundant=2,
    random_state=42
)

# Hold-out split: 80% train, 20% validation
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ──────────────────────────────────────────────
# 2.  Train champion model
# ──────────────────────────────────────────────
print("\n[Step 1] Training champion model...")
champion = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
champion.fit(X_train, y_train)
champ_acc = champion.score(X_val, y_val)
print(f"         Champion baseline accuracy: {champ_acc:.4f}")

# ──────────────────────────────────────────────
# 3.  Initialize DriftGuard
# ──────────────────────────────────────────────
dg = DriftGuard(
    model_id=MODEL_ID,
    api_url=API_URL,
    api_key=API_KEY,
    project_id=PROJECT_ID,
    drift_threshold=0.15,       # medium threshold -> easier to breach
    auto_retrain=True,
    accuracy=round(champ_acc, 4),
    version="1.0.0"
)

# Register champion and validation set for challenger comparison
dg.set_champion(champion)
dg.set_validation_data(X_val, y_val)

# Register retraining callback
@dg.retrainer
def retrain():
    """Train a better challenger on clean data with more trees."""
    print("\n  [Retrainer] Training challenger model (GradientBoosting)...")
    # GradientBoosting typically outperforms RandomForest on structured data
    challenger = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    challenger.fit(X_train, y_train)
    chall_acc = challenger.score(X_val, y_val)
    print(f"  [Retrainer] Challenger accuracy: {chall_acc:.4f}")
    return challenger

# Wrap champion
wrapped = dg.wrap(champion)

# ──────────────────────────────────────────────
# 4.  Phase 1 - 50% data with MEDIUM drift
# ──────────────────────────────────────────────
print("\n[Phase 1] Sending 50% data with MEDIUM drift (2x scale shift)...")
half = len(X) // 2

# First quarter: clean traffic
print("         -> Clean traffic (25%)...")
for row in X[:half // 2]:
    wrapped.predict([row])

# Second quarter: medium drift (scale 2x, offset 3)
print("         -> Medium-drift traffic (25%)...")
X_medium_drift = (X[half // 2 : half] * 2.0) + 3.0
for row in X_medium_drift:
    wrapped.predict([row])

print(f"         Phase 1 complete - {half} predictions sent.")
print(f"         Telemetry queued : {dg.telemetry_queued}")
print(f"         Telemetry sent   : {dg.telemetry_sent}")

# Brief pause so telemetry flushes
time.sleep(3)

# ──────────────────────────────────────────────
# 5.  Phase 2 - 100% data with HEAVY drift
#     -> pushes drift score above threshold
#     -> retraining fires, challenger beats champion
# ──────────────────────────────────────────────
print("\n[Phase 2] Sending 100% data with HEAVY drift (8x scale shift)...")
print("         This should breach the drift threshold and trigger retraining.")

X_heavy_drift = (X * 8.0) + 50.0
for i, row in enumerate(X_heavy_drift):
    wrapped.predict([row])
    if (i + 1) % 300 == 0:
        print(f"         -> {i+1}/{len(X)} predictions sent...")

print(f"\n         Phase 2 complete - {len(X)} predictions sent.")
print(f"         Telemetry queued : {dg.telemetry_queued}")
print(f"         Telemetry sent   : {dg.telemetry_sent}")
print(f"         Telemetry failed : {dg.telemetry_failed}")

# Allow background retraining thread to finish
print("\n[Step 5] Waiting for retraining pipeline to complete...")
time.sleep(10)

# ──────────────────────────────────────────────
# 6.  Summary
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("  DONE")
print(f"  Model ID  : {MODEL_ID}")
print(f"  API URL   : {API_URL}/models/{MODEL_ID}")
print(f"  Dashboard : http://localhost:3000")
print("=" * 60)
