@echo off
REM Setup script for Montenegrian Legal CBR System

echo.
echo ================================
echo Legal CBR System - Quick Setup
echo ================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js not found!
    echo Please install Node.js from: https://nodejs.org/
    echo Then run this script again.
    pause
    exit /b 1
)

echo ✅ Node.js found
node --version

REM Install dependencies
echo.
echo Installing dependencies...
call npm install

REM Start the server
echo.
echo ✅ Setup complete!
echo.
echo 🚀 Starting web server...
echo 📱 Opening http://localhost:3000 in your browser...
echo.
echo Press Ctrl+C to stop the server
echo.

start http://localhost:3000
call npm start
