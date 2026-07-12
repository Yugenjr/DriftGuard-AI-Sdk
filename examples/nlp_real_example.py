import time
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from driftguard.tracker import DriftGuard

def main():
    print("1. Downloading Real Text Dataset (20 Newsgroups)...")
    categories = ['sci.space', 'rec.autos']
    train_data = fetch_20newsgroups(subset='train', categories=categories, remove=('headers', 'footers', 'quotes'))
    
    # 2. Train a real text feature extractor and model (Initial Champion)
    print("2. Training TfidfVectorizer and Naive Bayes Model on Text...")
    # Keep max_features small (25) so that the drift score (percentage of drifted features) spikes easily!
    vectorizer = TfidfVectorizer(max_features=25) 
    X_train_vec_full = vectorizer.fit_transform(train_data.data).toarray()
    
    base_model = MultinomialNB()
    base_model.fit(X_train_vec_full, train_data.target)
    
    # Custom Predictor with controlled accuracy noise
    class ControlledTextPredictor:
        def __init__(self, clf, noise_level=0.0):
            self.clf = clf
            self.noise_level = noise_level
            
        def predict(self, texts_or_vecs):
            if isinstance(texts_or_vecs, np.ndarray) and np.issubdtype(texts_or_vecs.dtype, np.number):
                vecs = texts_or_vecs
            else:
                vecs = vectorizer.transform(texts_or_vecs).toarray()
                
            preds = self.clf.predict(vecs)
            
            # Artificially flip labels to control accuracy
            if self.noise_level > 0:
                np.random.seed(42) # For reproducible exact scores
                flip = np.random.rand(len(preds)) < self.noise_level
                preds[flip] = 1 - preds[flip] # Binary flip
            return preds
            
    # Initial Champion (40% accuracy -> lots of noise)
    my_nlp_model = ControlledTextPredictor(base_model, noise_level=0.60)
    
    # 3. Initialize DriftGuard
    print("3. Initializing DriftGuard for 'zen-nlp-model-v3'...")
    dg = DriftGuard(
        model_id="zen-nlp-model-v3", 
        api_url="http://localhost:8000",
        api_key="dg-6e679a28560cb4e9487ef4bd04f7e806",
        drift_threshold=0.10, # Lower threshold to guarantee trigger
        auto_retrain=True 
    )
    
    dg.set_validation_data(X_train_vec_full, train_data.target)
    dg.set_champion(my_nlp_model)
    
    # State variable to track which accuracy step we are on!
    retrain_stage = {"step": 1}
    
    @dg.retrainer
    def sequential_retrainer():
        print("\n>>> 🚨 [DriftGuard SDK] DRIFT DETECTED! Running custom @dg.retrainer...")
        
        if retrain_stage["step"] == 1:
            print(">>> 🚨 [DriftGuard SDK] Stage 1: Upgrading model to ~60% accuracy...")
            noise = 0.40
            retrain_stage["step"] = 2
        else:
            print(">>> 🚨 [DriftGuard SDK] Stage 2: Upgrading model to ~80% accuracy...")
            noise = 0.20
            
        # Provide the upgraded model!
        upgraded_model = ControlledTextPredictor(base_model, noise_level=noise)
        dg.set_validation_data(X_train_vec_full, train_data.target)
        
        return upgraded_model

    def extract_features(raw_text_list):
        return vectorizer.transform(raw_text_list).toarray()

    wrapped_model = dg.wrap(my_nlp_model, feature_extractor=extract_features)
    
    print("\n[Phase 1] Normal Traffic...")
    normal_texts = ["The new NASA spacecraft will launch tomorrow.", "I need to change the tires on my car."]
    for i in range(15): # More normal traffic to set ADWIN baseline
        wrapped_model.predict(normal_texts)
        time.sleep(0.1)
        
    print("\n[Phase 2] First Drift Spike! (Triggers 40% -> 60% Upgrade)...")
    drifting_texts = ["Bake the cake in the oven.", "Patient needs antibiotics."]
    for i in range(35): # Heavily skew the baseline to guarantee drift
        wrapped_model.predict(drifting_texts)
        time.sleep(0.1)
        
    time.sleep(4) # Wait for background retraining to finish and lock v1.0.1
    
    print("\n[Phase 3] Second Drift Spike! (Triggers 60% -> 80% Upgrade)...")
    more_drifting_texts = ["Financial markets crashed today.", "The stock exchange is volatile."]
    for i in range(35): # Heavily skew the baseline to guarantee drift
        wrapped_model.predict(more_drifting_texts)
        time.sleep(0.1)

    time.sleep(5)
    print("\nTest Finished! Check 'zen-nlp-model-v3' on your dashboard to see versions v1.0.0, v1.0.1, and v1.0.2!")

if __name__ == "__main__":
    main()
