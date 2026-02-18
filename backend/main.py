import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import joblib
import pandas as pd
import numpy as np
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add current directory to path so we can import modules if running inside backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import FakeNewsClassifier
from summarizer import summarize_article
from utils import clean_text
from live_verifier import verify_news_online

app = FastAPI(title="Fake News Detector API", 
              description="A machine learning API to detect fake news and provide summaries.",
              version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
model = FakeNewsClassifier()

class ArticleRequest(BaseModel):
    text: str
    
class AnalyzeResponse(BaseModel):
    result: str
    confidence: float
    summary: str
    explanation: list
    message: str
    live_verification: dict

@app.on_event("startup")
async def load_model():
    """Load the model on startup."""
    try:
        model.load_model()
        logger.info("Model loaded successfully on startup.")
    except Exception as e:
        logger.error(f"Failed to load model on startup: {e}")
        # Try to train if model is missing (for first run convenience)
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_pipeline.joblib")
        if not os.path.exists(model_path):
             logger.warning("Model not found. Please train first.")

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_article(request: ArticleRequest):
    """
    Analyze the given text for fake news probability.
    Returns prediction, confidence score, summary, and explainability.
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    logger.info(f"Received analysis request (Length: {len(request.text)} chars)")

    # 1. Preprocess
    cleaned_text = clean_text(request.text)
    
    # 2. Predict
    try:
        prediction_result = model.predict(cleaned_text)
        logger.info(f"Prediction: {prediction_result['prediction']} ({prediction_result['confidence']}%)")
    except Exception as e:
         # Fallback if model fails or isn't loaded
         logger.error(f"Prediction error: {e}")
         prediction_result = {"prediction": "UNKNOWN", "confidence": 0.0, "explanation": []}


    # 3. Summarize
    try:
        summary = summarize_article(request.text)
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        summary = "Summary unavailable due to error."
        
    # 4. Live Verification
    live_verification_result = {"status": "UNVERIFIED", "sources": [], "message": "Verification skipped"}
    try:
        # Use first 150 chars or first sentence as query for speed/relevance
        query = request.text.split('.')[0]
        if len(query) > 150:
             query = query[:150]
        
        live_verification_result = verify_news_online(query)
        

        # Override ML prediction if we have strong evidence from verification
        # If reliable sources confirm it, it's REAL.
        if live_verification_result["status"] == "VERIFIED_REAL":
            prediction_result["prediction"] = "REAL"
            prediction_result["confidence"] = 99.9  # High confidence if verified by major outlets
            prediction_result["explanation"].insert(0, "Verified by major news outlets")
        
        # If UNVERIFIED (found no reliable sources), do NOT default to FAKE.
        # Check if the ML model predicted FAKE with low confidence or based on limited data.
        # If ML says FAKE but high confidence, keep it.
        # But if ML is just guessing (which it might be for new topics), we should tone it down.
        elif live_verification_result["status"] == "UNVERIFIED":
             # If ML said FAKE but we couldn't verify it online either way, 
             # let's be cautious. If the ML confidence is suspicious (e.g. very high for short text),
             # it might be overfitting on keywords.
             pass 

    except Exception as e:
        logger.error(f"Live verification error: {e}")


    # Final Adjustment Logic
    # Differentiating "Unverified" from "Fake"
    final_prediction = prediction_result.get("prediction", "UNKNOWN")
    final_confidence = prediction_result.get("confidence", 0.0)
    
    # CRITICAL FIX: If Online Verification FAILED (Error) or found NOTHING (0 sources),
    # we CANNOT trust the ML model's "FAKE" prediction blindly. 
    # The ML model is trained on old data and might label "Joe Biden" or "Pandemic" as Fake due to bias.
    # If we can't verify it online, we must return UNKNOWN.
    
    if final_prediction == "FAKE":
        status = live_verification_result["status"]
        sources_count = len(live_verification_result["sources"])
        
        # Case 1: Search Verification Error (Rate limit, simplified scraper block, etc.)
        if status == "ERROR":
             final_prediction = "UNKNOWN"
             final_confidence = 0.0
             prediction_result["explanation"].insert(0, "Live verification failed (Connection/Limit)")
             




        # Case 2: Search ran but found ZERO results (Rare topic or very new)
        elif status in ["UNVERIFIED", "LIKELY_FAKE"] and sources_count == 0:
             # Logic Change: If query is very specific (e.g., date included), scraper might miss exact match.
             # BUT if it's a major historical event (like WHO Pandemic), it SHOULD be found.
             # If not found, it implies the specific phrasing is unique (often a sign of fake news or strict query).
             # Let's try to be smart: if the query has a date, maybe try a looser search? 
             # For now, we stick to UNKNOWN to avoid False Positives.
             # However, user wants it to be REAL if it is REAL.
             # Constraint: We are limited by the free scraper's ability to find old news.
             # Let's fallback to the ML Model's prediction if confidence is high, but label as "Unverified Online".
             
             # If model says REAL (high confidence) -> Keep REAL (but warn unverified)
             if prediction_result.get("prediction") == "REAL" and prediction_result.get("confidence", 0) > 70:
                 final_prediction = "REAL"
                 # Keep original confidence
                 prediction_result["explanation"].insert(0, "Predicted Real by AI (Online verification inconclusive)")
             else:
                 final_prediction = "UNKNOWN"
                 final_confidence = 0.0
                 prediction_result["explanation"].insert(0, "No online sources found to verify")
        

        # Case 3: Found results but not unreliable
        # Upgrade "Found online sources but disjoint" to "Likely REAL" if there are MANY search results (e.g., > 4)
        # because big real news gets covered by everyone, not just the "Reliable List".
        # This handles the "Joe Biden" case where it hits many random news sites but maybe misses our specific list.
        elif status == "UNVERIFIED" and sources_count > 0:
             if sources_count >= 3:
                 # If we found 3+ sources discussing it, it's very likely a real event, even if sources aren't in our curated list.
                 # "Joe Biden signs act" -> Covered by 1000s of sites.
                 final_prediction = "REAL" 
                 final_confidence = 75.0 # Moderate confidence
                 prediction_result["explanation"].insert(0, f"Widely reported online ({sources_count}+ sources)")
             else:
                 # Only 1-2 obscure sources -> Keep UNKNOWN
                 final_prediction = "UNKNOWN"
                 final_confidence = 0.0
                 prediction_result["explanation"].insert(0, "Found online sources but disjoint from verified list")

    return AnalyzeResponse(
        result=final_prediction,
        confidence=final_confidence,
        summary=summary,
        explanation=prediction_result.get("explanation", []),
        live_verification=live_verification_result,
        message="Analysis complete."
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Fake News Detector API. Visit /docs for Swagger UI."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
