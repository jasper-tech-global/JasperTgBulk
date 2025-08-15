@echo off
setlocal
cd /d %~dp0\..
if not exist .venv\Scripts\python.exe (
  echo Virtual environment not found. Please run run_bot_full.bat first.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
echo Testing connection to Telegram API...
python scripts\test_connection.py
endlocal
