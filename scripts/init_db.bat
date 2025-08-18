@echo off
echo 🚀 Initializing Jasper TG BULK Database...
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
echo Running database initialization...
python scripts\init_db.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🎉 Database initialization completed successfully!
    echo You can now run the admin panel with clean logs.
    echo.
    echo Default admin credentials:
    echo   Username: admin
    echo   Password: admin123
) else (
    echo.
    echo ❌ Database initialization failed!
    echo Check the error messages above.
)

echo.
pause
