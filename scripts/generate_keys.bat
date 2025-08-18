@echo off
echo 🔑 Generating secure keys for Jasper TG BULK...
echo.

cd /d "%~dp0.."

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo Running key generation...
python scripts\generate_keys.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Keys generated successfully!
    echo Check your .env file for the new keys.
) else (
    echo.
    echo ❌ Key generation failed!
    echo Check the error messages above.
)

echo.
pause
