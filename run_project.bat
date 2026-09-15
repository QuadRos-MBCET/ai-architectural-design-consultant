@echo off
echo =======================================================
echo   Starting AI Architectural Design Consultant Servers
echo =======================================================
echo.
echo Starting Backend (FastAPI)...
start cmd /k "cd backend && uvicorn main:app --reload"

echo Starting Frontend (React/Vite)...
start cmd /k "cd frontend && npm run dev"

echo.
echo =======================================================
echo Servers are now running in separate permanent windows!
echo You can safely present your project without interruptions.
echo =======================================================
pause
