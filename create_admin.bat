@echo off
cd /d "%~dp0"

if not exist ".venv" (
  echo Virtual environment not found.
  echo Run start_server.bat first.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
python manage.py createsuperuser
pause
