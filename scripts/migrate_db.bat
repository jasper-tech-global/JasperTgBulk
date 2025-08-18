@echo off
echo Running Database Migration for Jasper TG BULK...
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
echo Running database migration...
python scripts\migrate_db.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Migration completed successfully!
    echo You can now run the admin panel.
) else (
    echo.
    echo ❌ Migration failed!
    echo Check the error messages above.
)

echo.
pause
