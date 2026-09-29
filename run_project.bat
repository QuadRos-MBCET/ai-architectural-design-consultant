@echo off
echo =======================================================
echo   Starting Prompt-Based 2D Floor Plan Generator
echo   (FastAPI Backend + React Vite Frontend)
echo =======================================================
echo.
echo Starting Backend (FastAPI)...
start cmd /k "uvicorn backend.main:app --reload --port 8000"

echo Starting Frontend (React/Vite)...
start cmd /k "cd frontend && npm run dev"

echo.
echo =======================================================
echo Servers are now starting!
echo Backend API: http://localhost:8000
echo React Studio UI: http://localhost:5173
echo =======================================================
pause
