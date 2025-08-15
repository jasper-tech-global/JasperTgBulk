@echo off
setlocal
cd /d %~dp0\..
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
)
call .venv\Scripts\activate.bat
if not exist .venv\Lib\site-packages\fastapi (
  python -m pip install -U pip --quiet
  pip install -r requirements.txt --quiet --no-input
)
if not exist data mkdir data
echo Starting Admin Server...
python -m uvicorn app.admin.app:app --host 0.0.0.0 --port 8000 --reload
endlocal



