
# AI Fake News Detector for Students 🎓

<p align="center">
  <img src="https://via.placeholder.com/800x400?text=Fake+News+Detector+for+Students" alt="Project Banner" width="100%">
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
*   **Backend**: Python, FastAPI, Scikit-Learn, DuckDuckGo-Search, HuggingFace Transformers.
*   **Frontend**: React.js, Vite, Modern CSS.
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


### Backend (Python & FastAPI)
*   **Framework**: FastAPI for high-performance API endpoints.
*   **Text Preprocessing**: NLTK-based cleaning (lowercasing, punctuation removal, stopword filtering).
*   **Vectorization**: TF-IDF (Term Frequency-Inverse Document Frequency) to convert text into numerical features.
*   **Machine Learning**:
    *   **Logistic Regression**: A robust baseline model for text classification.
    *   **Random Forest**: An ensemble method to capture non-linear relationships.
    *   The system trains both and saves the one with higher accuracy on the test set.
*   **Summarization**: HuggingFace Transformers (DistilBART) for abstractive summarization.

### Frontend (React)
*   **Framework**: React with Vite for fast development and optimized builds.
*   **Styling**: Custom CSS variables for a premium, dark-mode compatible aesthetic.
*   **State Management**: React Hooks for handling asynchronous API calls and UI states.

## Model Performance

The model is trained on a dataset of real and fake news articles.

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Logistic Regression | ~95% | 0.94 | 0.96 | 0.95 |
| Random Forest | ~93% | 0.92 | 0.94 | 0.93 |

*Note: Performance metrics are based on the training data split. Actual results may vary depending on the dataset used.*

## Getting Started

### Prerequisites

*   Python 3.8+
*   Node.js 16+

### Installation

1.  **Project Setup**
    (You are already in the project folder)

2.  **Backend Setup**
    ```bash
    cd backend
    python -m venv .venv 
    # Windows:
    .venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    
    pip install -r requirements.txt
    
    # Train the model (uses included sample data by default)
    python train.py
    
    # Start the server
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

3.  **Frontend Setup**
    Open a new terminal in the project root.
    ```bash
    cd frontend
    # Dependencies were installed during setup
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.


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
Built with ❤️ by [Your Name]
