@echo off
echo 🔧 DNS Configuration Helper - Jasper TG BULK
echo ===========================================
echo.

cd /d "%~dp0.."

echo 📁 Checking Python environment...
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found. Please run setup_project.bat first.
    pause
    exit /b 1
)

echo ✅ Virtual environment found
echo.

echo 🚀 Starting DNS Configuration Helper...
echo.

call .venv\Scripts\activate.bat
python scripts\setup_dns.py

echo.
echo 🎯 DNS Configuration Helper completed!
echo.
pause
