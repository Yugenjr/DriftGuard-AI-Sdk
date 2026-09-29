import joblib
from sklearn.ensemble import GradientBoostingClassifier
import sys

class PerfectChallenger(GradientBoostingClassifier):
    pass

sys.modules['__main__'].PerfectChallenger = PerfectChallenger
model = joblib.load(r'C:\Users\Yugendra\Downloads\DriftGuard\artifacts\5\demo-champion-1784952941\version_1.0.3.pkl')
model.__class__ = GradientBoostingClassifier
joblib.dump(model, r'C:\Users\Yugendra\Downloads\DriftGuard\artifacts\5\demo-champion-1784952941\version_1.0.3.pkl')
print('Fixed pickle file!')
