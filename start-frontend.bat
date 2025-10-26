@echo off
REM ===============================================
REM   Trading Platform - Start Frontend
REM ===============================================

echo ========================================
echo   Starting Frontend Server
echo ========================================
echo.

cd frontend

echo [1/3] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js not found!
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js version:
node --version
echo.

echo [2/3] Checking dependencies...
if not exist node_modules (
    echo ⚠️  Dependencies not installed!
    echo Installing dependencies... This may take a few minutes.
    call yarn install
    if errorlevel 1 (
        echo ⚠️  Yarn failed, trying npm...
        call npm install
    )
)
echo ✅ Dependencies ready
echo.

echo [3/3] Starting Frontend Development Server...
echo Frontend will run on: http://localhost:3000
echo Backend API: http://localhost:8001
echo.
echo The browser will open automatically
echo Press Ctrl+C to stop the server
echo ========================================
echo.

yarn start

pause
