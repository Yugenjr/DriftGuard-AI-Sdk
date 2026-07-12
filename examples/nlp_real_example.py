import time
import numpy as np
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from driftguard.tracker import DriftGuard

def main():
    print("1. Downloading Real Text Dataset (20 Newsgroups)...")
    # Get a couple of categories
    categories = ['sci.space', 'rec.autos']
    train_data = fetch_20newsgroups(subset='train', categories=categories, remove=('headers', 'footers', 'quotes'))
    
    # 2. Train a real text feature extractor and model (Initial Champion)
    print("2. Training TfidfVectorizer and Naive Bayes Model on Text (Partial Data)...")
    vectorizer = TfidfVectorizer(max_features=25) 
    
    # Let's train the FIRST model on only 50% of the data so it has a lower accuracy
    half_idx = len(train_data.data) // 2
    X_train_vec_half = vectorizer.fit_transform(train_data.data[:half_idx]).toarray()
    X_train_vec_full = vectorizer.transform(train_data.data).toarray() # For validation
    
    model = MultinomialNB()
    model.fit(X_train_vec_half, train_data.target[:half_idx])
    
    # Create a custom model class that takes raw text, just like a real LLM would!
    class TextPredictor:
        def __init__(self, clf):
            self.clf = clf
            
        def predict(self, texts_or_vecs):
            # If DriftGuard's validation framework passes pre-vectorized arrays, use them directly
            if isinstance(texts_or_vecs, np.ndarray) and np.issubdtype(texts_or_vecs.dtype, np.number):
                return self.clf.predict(texts_or_vecs)
                
            # Otherwise, vectorize the raw text strings!
            vecs = vectorizer.transform(texts_or_vecs).toarray()
            return self.clf.predict(vecs)
            
    my_nlp_model = TextPredictor(model)
    
    # 3. Initialize DriftGuard
    print("\n3. Initializing DriftGuard for 'zen-nlp-model'...")
    dg = DriftGuard(
        model_id="zen-nlp-model", # Zen mode testing
        api_url="http://localhost:8000",
        drift_threshold=0.15,
        auto_retrain=True 
    )
    
    # Set the baseline validation data using the FULL dataset so evaluation is accurate
    dg.set_validation_data(X_train_vec_full, train_data.target)
    
    # Manually register our initial model as the Champion!
    dg.set_champion(my_nlp_model)
    
    # 4. Define our custom NLP Retraining Pipeline using the @dg.retrainer decorator!
    # When drift is detected, the SDK executes THIS function locally instead of pinging the backend pipeline.
    @dg.retrainer
    def my_custom_nlp_retrainer():
        print("\n>>> 🚨 [DriftGuard SDK] DRIFT DETECTED! Intercepting event and running custom @dg.retrainer locally!")
        print(">>> 🚨 [DriftGuard SDK] Fetching 100% of the text data and training a BETTER MultinomialNB model...")
        
        # Train on FULL data so it gets a higher accuracy!
        new_clf = MultinomialNB()
        new_clf.fit(X_train_vec_full, train_data.target)
        
        # [NEW] Update the validation data to the NEW dataset that we just trained on!
        # This tells DriftGuard: "This new dataset is the new baseline normal!"
        # (In a real app, this would be your freshly pulled production data)
        dg.set_validation_data(X_train_vec_full, train_data.target)

        
        print(">>> 🚨 [DriftGuard SDK] Training complete! Submitting Challenger model to validation arena...")
        return TextPredictor(new_clf)

    # 5. Wrap the model WITH the vectorizer acting as the feature extractor!
    # The feature_extractor must take raw text and return a numpy array
    def extract_features(raw_text_list):
        return vectorizer.transform(raw_text_list).toarray()

    wrapped_model = dg.wrap(my_nlp_model, feature_extractor=extract_features)
    
    # 5. Simulate Production Traffic (Normal Text)
    print("\n[Phase 1] Sending normal English text (Space & Autos)...")
    normal_texts = [
        "The new NASA spacecraft will launch tomorrow into orbit.",
        "I need to change the oil and tires on my car.",
        "The engine has a V8 cylinder design.",
        "Telescopes are observing the moon and planets."
    ]
    
    for i in range(10): # Loop to generate enough predictions
        preds = wrapped_model.predict(normal_texts)
        time.sleep(0.2)
        
    print("Normal text processed successfully!")
    time.sleep(2)
    
    # 6. Simulate Concept Drift (Completely different domain / random text)
    print("\n[Phase 2] Sending Drifting Text (Cooking / Medical / Gibberish)...")
    drifting_texts = [
        "Bake the cake in the oven for 45 minutes with flour and sugar.",
        "The patient needs antibiotics and a blood test immediately.",
        "XYZ abc qwerty random strings blah blah.",
        "Boil the water, add salt, and cook the pasta."
    ]
    
    for i in range(25): # Loop to heavily skew the distribution and trigger drift
        preds = wrapped_model.predict(drifting_texts)
        time.sleep(0.2)
        
    print("\nTest Finished! The text feature extractor converted the strings into mathematical arrays on the fly!")
    print("Go check 'real-nlp-model-v1' on your dashboard to see the drift spike!")
    time.sleep(3) # Wait for daemon threads

if __name__ == "__main__":
    main()
