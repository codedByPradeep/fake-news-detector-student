import logging
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import os


MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_pipeline.joblib")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FakeNewsClassifier:
    def __init__(self):
        self.pipeline = None
    
    def train(self, data_path):
        """
        Trains the model on the provided dataset.
        Compare Logistic Regression and Random Forest.
        Saves the best performing model pipeline.
        """
        logger.info(f"Loading data from {data_path}...")
        try:
            df = pd.read_csv(data_path)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return
            
        # Basic preprocessing assumes 'text' and 'label' columns exist
        if 'text' not in df.columns or 'label' not in df.columns:
            logger.error("Dataset must have 'text' and 'label' columns.")
            return

        X = df['text'].fillna('')
        y = df['label']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 1. Logistic Regression
        logger.info("Training Logistic Regression...")
        lr_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
            ('clf', LogisticRegression())
        ])
        lr_pipeline.fit(X_train, y_train)
        lr_pred = lr_pipeline.predict(X_test)
        lr_acc = accuracy_score(y_test, lr_pred)
        logger.info(f"Logistic Regression Accuracy: {lr_acc:.4f}")

        # 2. Random Forest
        logger.info("Training Random Forest...")
        rf_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
            ('clf', RandomForestClassifier(n_estimators=100))
        ])
        rf_pipeline.fit(X_train, y_train)
        rf_pred = rf_pipeline.predict(X_test)
        rf_acc = accuracy_score(y_test, rf_pred)
        logger.info(f"Random Forest Accuracy: {rf_acc:.4f}")

        # Select Best Model
        if rf_acc >= lr_acc:
            logger.info("Random Forest performed better or equal. Saving Random Forest model.")
            self.pipeline = rf_pipeline
        else:
            logger.info("Logistic Regression performed better. Saving Logistic Regression model.")
            self.pipeline = lr_pipeline
        
        # Save Model
        try:
            logger.info(f"Saving model to {MODEL_PATH}...")
            # Ensure dir exists if relative to script execution?
            # joblib handles this usually if dir exists
            joblib.dump(self.pipeline, MODEL_PATH)
            logger.info(f"Model saved successfully.")
        except Exception as e:
            logger.error(f"Error saving model: {e}")

    def load_model(self):
        """Loads the trained model from disk."""
        if os.path.exists(MODEL_PATH):
            self.pipeline = joblib.load(MODEL_PATH)
            logger.info("Model loaded successfully.")
        else:
            logger.warning(f"Model file not found at {MODEL_PATH}. Please train the model first.")

    def predict(self, text):
        """
        Predicts whether text is REAL or FAKE.
        Returns label, confidence, and explanation (top keywords).
        """
        if not self.pipeline:
            self.load_model()
            if not self.pipeline:
                return {"error": "Model not loaded"}

        # Prediction
        prediction = self.pipeline.predict([text])[0]
        proba_classes = self.pipeline.classes_
        proba_values = self.pipeline.predict_proba([text])[0]
        
        # Get max proba
        max_proba_idx = proba_values.argmax()
        confidence = proba_values[max_proba_idx]

        # Explainability (Feature Importance for simple models)
        # Getting feature names
        vectorizer = self.pipeline.named_steps['tfidf']
        feature_names = vectorizer.get_feature_names_out()
        
        explanation = []
        
        # Logic for feature importance extraction varies by model type
        try:
            input_vector = vectorizer.transform([text])
            # Generic approach: extract keywords present in text that are high in TF-IDF
            # This is a heuristic for "important words" if model interpretation is hard
            tfidf_scores = zip(feature_names, input_vector.toarray()[0])
            sorted_tfidf = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
            explanation = [word for word, score in sorted_tfidf[:5] if score > 0]
            
        except Exception as e:
            logger.error(f"Explainability error: {e}")
            explanation = ["Error extracting features"]

        return {
            "prediction": prediction,
            "confidence": round(confidence * 100, 2),
            "explanation": explanation
        }

if __name__ == "__main__":
    clf = FakeNewsClassifier()
    # Simple test if run directly
    clf.train("backend/data/fake_news.csv")
