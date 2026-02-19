
# AI Fake News Detector for Students 🎓


<p align="center">
  <img src="assets/banner.svg" alt="Fake News Detector for Students" width="100%">
</p>

## Problem Statement 🎯
Misinformation spreads quickly through online news and social media, making it hard for students to differentiate between reliable and fake information. There is a need for an AI solution that can analyze articles, assess credibility, and provide concise, trustworthy summaries to prevent the spread of false information.

## Solution Overview 💡
This project addresses the problem by providing a simple, user-friendly tool that combines **Natural Language Processing (NLP)** for linguistic analysis with **Real-Time Web Verification** to fact-check claims against reliable sources instantly.

### Core Capabilities:
1.  **Analyze Articles**: Uses ML models to detect patterns in writing style (e.g., sensationalism, hate speech).
2.  **Assess Credibility (Real-Time)**: Unlike static models, this tool checks *live news* using DuckDuckGo to verify if major outlets are reporting the same story.
3.  **Concise Summaries**: Generates short, easy-to-read summaries using AI, perfect for students researching topics.

---

## Key Features

*   **⚡ Real-Time Fact Checking**: Automatically searches the web to verify claims against trusted sources (BBC, Reuters, Times of India, etc.).
*   **🤖 Smart AI Analysis**: Trained on thousands of news articles to spot fake news purely from text patterns.
*   **📝 Auto-Summarization**: Get the gist of long articles in seconds.
*   **✅ Trust Scores**: Provides a clear "Real", "Fake", or "Video/Clickbait" verdict with a confidence percentage.
*   **🔍 Explainability**: Highlights *why* an article might be fake (e.g., specific keywords or lack of sources).

## Technical Architecture


### Technologies Used:
*   **Application / UI**: Streamlit (Python-based Web App).
*   **Engine**: Python, Scikit-Learn, DuckDuckGo-Search, HuggingFace Transformers.
*   **AI Models**: Logistic Regression, Random Forest (Comparison Ensemble).

## How it Works (Real-World Application)

1.  **Input**: A student pastes a news headline or article.
2.  **Processing**:
    *   **Step 1:** The text is cleaned and analyzed by the ML model for fake/real patterns.
    *   **Step 2:** The system simultaneously searches the web for live verification.
3.  **Output**:
    *   **Verdict**: "REAL" if verified by reliable sources, or matched by AI pattern.
    *   **Evidence**: Links to trusted news sites if found.
    *   **Summary**: A 2-3 sentence summary of the content.

---

## Live Demo 🚀
The project is live! You can access it here:
**[Fake News Detector for Students](https://fake-news-detector-student-gbxesl5vnqbbparsxpdssf.streamlit.app/)**

## Getting Started (Local Run)

### Prerequisites
*   Python 3.8+

### Installation

1.  **Setup Virtual Environment**
    ```bash
    cd backend
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App**
    ```bash
    streamlit run streamlit_app.py
    ```
    The application will open automatically in your browser.

    *(Alternatively, just run the `start_app.bat` file if on Windows)*


## Usage

1.  Open the web application in your browser.
2.  Paste the text of a news article into the input box.
3.  Click **Analyze Article**.
4.  View the verdict (REAL/FAKE), confidence score, summary, and key indicators.

## Dataset

This project is designed to work with the [Kaggle Fake News Dataset](https://www.kaggle.com/c/fake-news/data).
To use the full dataset:
1.  Download `train.csv` from Kaggle.
2.  Place it in `backend/data/`.
3.  Update `backend/train.py` or just rename the file to `fake_news.csv` (keeping column headers consistent).
4.  Run `python backend/train.py` to retrain the model.

## Future Improvements

*   **Deep Learning Integration**: Implement LSTM or BERT-based classifiers for higher accuracy on subtle misinformation.
*   **URL Scraping**: Add functionality to fetch and parse article content directly from a URL.
*   **User Feedback**: Allow users to flag incorrect classifications to improve the model over time.
*   **Browser Extension**: Create a chrome extension to analyze news directly on websites.

---
Built with ❤️ by Pradeep Patwal
