@echo off
REM ===============================================
REM   Trading Platform - Start Backend
REM ===============================================

echo ========================================
echo   Starting Backend Server
echo ========================================
echo.

cd backend

echo [1/3] Activating Python Virtual Environment...
if exist venv\Scripts\activate (
    call venv\Scripts\activate
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)
echo.

echo [2/3] Checking MongoDB connection...
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000); client.server_info(); print('✅ MongoDB connected')" 2>nul
if errorlevel 1 (
    echo ⚠️  MongoDB not running!
    echo Please start MongoDB service first.
    echo.
    pause
    exit /b 1
)
echo.

echo [3/3] Starting Backend Server...
echo Backend will run on: http://localhost:8001
echo API Documentation: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

pause
