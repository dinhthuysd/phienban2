@echo off
REM ===============================================
REM   Trading Platform - Setup Script
REM ===============================================

title Trading Platform - First Time Setup

color 0B
echo.
echo ========================================
echo   🛠️  Trading Platform Setup
echo ========================================
echo.
echo This script will set up your development environment
echo.
pause
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo Please install Python 3.11+ from: https://www.python.org/downloads/
    echo ⚠️  Don't forget to check "Add Python to PATH"
    pause
    exit /b 1
)
echo ✅ Python found:
python --version
echo.

REM Check Node.js
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found!
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js found:
node --version
echo.

REM Check MongoDB
echo [3/5] Checking MongoDB...
mongosh --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MongoDB Shell not found!
    echo Please install MongoDB from: https://www.mongodb.com/try/download/community
    echo You can continue without it, but database won't work
    pause
)
echo ✅ MongoDB Shell found:
mongosh --version
echo.

REM Setup Backend
echo [4/5] Setting up Backend...
cd backend

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

echo Activating virtual environment...
call venv\Scripts\activate
echo.

echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Backend dependencies installed
echo.

cd ..

REM Setup Frontend
echo [5/5] Setting up Frontend...
cd frontend

echo Installing Node.js dependencies...
echo This may take several minutes...
call yarn install
if errorlevel 1 (
    echo ⚠️  Yarn failed, trying npm...
    call npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✅ Frontend dependencies installed
echo.

cd ..

REM Create data directory for MongoDB (if doesn't exist)
if not exist "C:\data\db" (
    echo Creating MongoDB data directory...
    mkdir "C:\data\db" 2>nul
    if errorlevel 1 (
        echo ⚠️  Could not create C:\data\db - you may need admin rights
        echo You can create it manually or use a different path
    ) else (
        echo ✅ MongoDB data directory created
    )
)
echo.

REM Summary
echo ========================================
echo   ✅ Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Make sure MongoDB is running
echo   2. Run: start-all.bat
echo      OR
echo      Run separately:
echo      - start-backend.bat
echo      - start-frontend.bat
echo.
echo Admin credentials:
echo   Email:    admin@trading.com
echo   Password: Admin@123456
echo.
echo 📚 For detailed instructions, see:
echo    HƯỚNG_DẪN_CHẠY_TRÊN_WINDOWS.md
echo.
echo ========================================
pause
