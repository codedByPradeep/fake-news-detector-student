@echo off
echo Starting Fake News Detector (Streamlit)...
cd backend
..\.venv\Scripts\activate && streamlit run streamlit_app.py
pause
