import streamlit as st
import logging
import joblib
import os
import sys

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import FakeNewsClassifier
from summarizer import summarize_article
from utils import clean_text
from live_verifier import verify_news_online

# Page Config
st.set_page_config(
    page_title="Fake News Detector for Students",
    page_icon="🎓",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .result-card {
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid #e5e7eb;
    }
    .REAL {
        background-color: #ecfdf5;
        border-left: 5px solid #10b981;
    }
    .FAKE {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
    }
    .UNKNOWN {
        background-color: #fffbeb;
        border-left: 5px solid #f59e0b;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Load Model (Cached to prevent reloading on every interaction)
@st.cache_resource
def load_app_model():
    model = FakeNewsClassifier()
    try:
        model.load_model()
        logger.info("Model loaded successfully.")
        return model
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None

model = load_app_model()

# Header
st.title("🎓 Fake News Detector for Students")
st.write("Analyze articles, assess credibility, and get concise summaries.")

# Input
article_text = st.text_area("Paste the news article text here...", height=200)

if st.button("Analyze Article", type="primary"):
    if not article_text.strip():
        st.warning("Please enter some text to analyze.")
    elif not model:
        st.error("Model is not loaded. Please check logs.")
    else:
        with st.spinner("Analyzing... (checking ML patterns + live web search)"):
            try:
                # 1. Preprocess
                cleaned_text = clean_text(article_text)
                
                # 2. Predict
                prediction_result = model.predict(cleaned_text)
                
                # 3. Summarize (Skip if very short to save time)
                summary = "Summary unavailable."
                if len(article_text) > 300:
                    try:
                        summary = summarize_article(article_text)
                    except Exception as e:
                        logger.error(f"Summarization error: {e}")
                else:
                    summary = article_text

                # 4. Live Verification
                query = article_text.split('.')[0][:150]
                live_verification_result = verify_news_online(query)
                
                # --- LOGIC INTEGRATION FROM MAIN.PY ---
                # Override ML prediction if we have strong evidence from verification
                if live_verification_result["status"] == "VERIFIED_REAL":
                    prediction_result["prediction"] = "REAL"
                    prediction_result["confidence"] = 99.9
                    prediction_result["explanation"].insert(0, "Verified by major news outlets")
                
                elif live_verification_result["status"] == "UNVERIFIED":
                    pass 

                # Final Adjustment Logic
                final_prediction = prediction_result.get("prediction", "UNKNOWN")
                final_confidence = prediction_result.get("confidence", 0.0)
                
                status = live_verification_result["status"]
                sources_count = len(live_verification_result["sources"])
                
                if final_prediction == "FAKE":
                    if status == "ERROR":
                        final_prediction = "UNKNOWN"
                        final_confidence = 0.0
                        prediction_result["explanation"].insert(0, "Live verification failed (Connection/Limit)")
                    elif status in ["UNVERIFIED", "LIKELY_FAKE"] and sources_count == 0:
                         # Logic for Case 2 (0 results)
                         if prediction_result.get("prediction") == "REAL" and prediction_result.get("confidence", 0) > 70:
                             final_prediction = "REAL"
                             prediction_result["explanation"].insert(0, "Predicted Real by AI (Online verification inconclusive)")
                         else:
                             final_prediction = "UNKNOWN"
                             final_confidence = 0.0
                             prediction_result["explanation"].insert(0, "No online sources found to verify")
                
                elif status == "UNVERIFIED" and sources_count > 0:
                     if sources_count >= 3:
                         final_prediction = "REAL" 
                         final_confidence = 75.0
                         prediction_result["explanation"].insert(0, f"Widely reported online ({sources_count}+ sources)")
                     else:
                         final_prediction = "UNKNOWN"
                         final_confidence = 0.0
                         prediction_result["explanation"].insert(0, "Found online sources but disjoint from verified list")

                # --- DISPLAY RESULTS ---
                
                verdict_color = "green" if final_prediction == "REAL" else "red" if final_prediction == "FAKE" else "orange"
                
                st.markdown(f"""
                <div class="result-card {final_prediction}">
                    <h2 style="margin:0; color: {verdict_color};">Verdict: {final_prediction}</h2>
                    <p>Confidence Score: <strong>{final_confidence}%</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.progress(min(final_confidence / 100, 1.0))

                st.subheader("Summary")
                st.info(summary)

                st.subheader("Key Indicators")
                st.write(", ".join([f"#{word}" for word in prediction_result.get("explanation", [])]))

                if live_verification_result["status"] != "UNVERIFIED" or len(live_verification_result["sources"]) > 0:
                    st.subheader("Live Verification")
                    if live_verification_result["status"] == "VERIFIED_REAL":
                        st.success(f"✅ Verified by Reliable Sources: {live_verification_result['message']}")
                    elif len(live_verification_result["sources"]) > 0:
                         st.warning(f"⚠️ {live_verification_result['message']}")
                    else:
                        st.error(f"❌ {live_verification_result['message']}")

                    if live_verification_result["sources"]:
                        for source in live_verification_result["sources"][:3]:
                            st.markdown(f"- [{source['title']}]({source['url']}) ({source['domain']})")

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
                logger.error(f"Streamlit App Error: {e}")
