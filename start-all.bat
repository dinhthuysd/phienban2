@echo off
REM ===============================================
REM   Trading Platform - Start All Services
REM ===============================================

title Trading Platform - Launcher

color 0A
echo.
echo ========================================
echo   🚀 Trading Platform Launcher
echo ========================================
echo.
echo Starting all services...
echo.

REM Check if MongoDB is running
echo [1/3] Checking MongoDB...
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000); client.server_info()" 2>nul
if errorlevel 1 (
    echo ⚠️  MongoDB is not running!
    echo.
    echo Please start MongoDB:
    echo   1. Open Services (services.msc)
    echo   2. Find "MongoDB Server"
    echo   3. Click "Start"
    echo.
    echo Or run manually:
    echo   cd "C:\Program Files\MongoDB\Server\7.0\bin"
    echo   mongod --dbpath "C:\data\db"
    echo.
    pause
    exit /b 1
)
echo ✅ MongoDB is running
echo.

REM Start Backend
echo [2/3] Starting Backend Server...
start "Backend Server" cmd /k "cd backend && call venv\Scripts\activate && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
echo ✅ Backend starting on http://localhost:8001
echo.

REM Wait a bit for backend to initialize
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul
echo.

REM Start Frontend
echo [3/3] Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && yarn start"
echo ✅ Frontend starting on http://localhost:3000
echo.

echo ========================================
echo   ✅ All Services Started!
echo ========================================
echo.
echo 📊 Service URLs:
echo   • Frontend:  http://localhost:3000
echo   • Backend:   http://localhost:8001
echo   • API Docs:  http://localhost:8001/docs
echo   • MongoDB:   mongodb://localhost:27017
echo.
echo 🔑 Admin Login:
echo   • Email:     admin@trading.com
echo   • Password:  Admin@123456
echo.
echo ⚠️  Don't close this window!
echo Close the Backend and Frontend windows to stop services.
echo.
echo ========================================
pause
