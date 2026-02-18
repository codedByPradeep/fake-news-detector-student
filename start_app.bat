@echo off
echo Starting Fake News Detector for Students...

start "Backend Server" cmd /k "cd backend && ..\.venv\Scripts\activate && uvicorn main:app --reload"
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo Servers started! 
echo Frontend: http://localhost:5173
echo Backend: http://localhost:8000
pause
