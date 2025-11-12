@echo off
REM Startup script for AI Conversation Assistant (Windows)
REM This script starts both the backend and frontend services

echo Starting AI Conversation Assistant...
echo.

REM Check if backend virtual environment exists
if not exist "backend\venv\" (
    echo Backend virtual environment not found!
    echo Please run setup first:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Node modules not found!
    echo Please run: npm install
    exit /b 1
)

REM Check if .env exists
if not exist "backend\.env" (
    echo Backend .env file not found!
    echo Please create backend\.env from backend\.env.example
    exit /b 1
)

echo All dependencies found
echo.

echo Starting Backend (FastAPI)...
cd backend
call venv\Scripts\activate
start "Backend - FastAPI" cmd /k uvicorn app.main:app --reload --port 8000
cd ..

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo Starting Frontend (Vite)...
start "Frontend - Vite" cmd /k npm run dev

echo.
echo Application started!
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Close the terminal windows to stop the services.
