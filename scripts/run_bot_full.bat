@echo off
setlocal
cd /d %~dp0\..
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
)
call .venv\Scripts\activate.bat
if not exist .venv\Lib\site-packages\aiogram (
  python -m pip install -U pip --quiet
  pip install -r requirements.txt --quiet --no-input
)
if not exist .env (
  if exist ENV_SAMPLE copy ENV_SAMPLE .env >nul
)
powershell -NoProfile -Command "if(-not (Test-Path 'data')){ New-Item -ItemType Directory -Path 'data' | Out-Null }"
powershell -NoProfile -Command "$p='.env';$t='TELEGRAM_BOT_TOKEN=7899691936:AAHsE7r-F5wVVSZ9OL4CD8nwjRJov49Ie10';$c=(Get-Content $p -Raw -ErrorAction SilentlyContinue); if(-not $c){$c=''}; if($c -match '(?m)^TELEGRAM_BOT_TOKEN='){ $c=[regex]::Replace($c,'(?m)^TELEGRAM_BOT_TOKEN=.*',$t) } else { if($c.Length -gt 0 -and -not $c.EndsWith([Environment]::NewLine)){ $c+=[Environment]::NewLine }; $c+=$t+[Environment]::NewLine }; Set-Content -Path $p -Value $c -Encoding UTF8"
python scripts\init_keys.py
echo Initializing database...
python scripts\init_db.py
echo Starting Telegram Bot...
python main_bot.py
endlocal



