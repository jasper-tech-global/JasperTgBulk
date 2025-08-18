@echo off
echo 🚀 Jasper TG BULK - Complete Project Setup
echo ===========================================
echo.

cd /d "%~dp0.."

echo 📁 Checking project structure...
if not exist "app" (
    echo ❌ Project structure not found. Please run this from the project root.
    pause
    exit /b 1
)

echo ✅ Project structure found

echo.
echo 🔧 Setting up virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.
echo 📦 Installing dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo 🗄️ Initializing database...
python scripts\init_db.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Database initialization failed
    pause
    exit /b 1
)
echo ✅ Database initialized

echo.
echo 🔑 Checking environment variables...
if not exist ".env" (
    echo Creating .env file...
    echo TELEGRAM_BOT_TOKEN=your_bot_token_here > .env
    echo SECRET_KEY=your_secret_key_here >> .env
    echo FERNET_KEY=your_fernet_key_here >> .env
    echo ✅ .env file created
    echo.
    echo ⚠️  IMPORTANT: Please update the .env file with your actual values:
    echo    - TELEGRAM_BOT_TOKEN: Your Telegram bot token
    echo    - SECRET_KEY: A random secret key for the admin panel
    echo    - FERNET_KEY: A random key for encrypting SMTP passwords
    echo.
) else (
    echo ✅ .env file already exists
)

echo.
echo 🎉 Project setup completed successfully!
echo.
echo 📋 Next steps:
echo    1. Update your .env file with actual values
echo    2. Run the admin panel: scripts\run_admin_full.bat
echo    3. Run the bot: scripts\run_bot_full.bat
echo.
echo 🔐 Default admin credentials:
echo    Username: admin
echo    Password: admin123
echo.
echo 🚀 You're ready to go!
echo.
pause
