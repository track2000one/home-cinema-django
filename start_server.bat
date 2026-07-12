@echo off
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed or is not available in PATH.
  echo Install Python 3.11 or newer and enable "Add Python to PATH".
  pause
  exit /b 1
)

if not exist ".venv" (
  python -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py makemigrations movies
python manage.py migrate
python manage.py collectstatic --noinput

echo.
echo Local address:
echo http://127.0.0.1:8000
echo.
echo Network address:
echo http://YOUR-PC-IP:8000
echo.
echo Run create_admin.bat once to create an administrator account.
echo.

waitress-serve --listen=0.0.0.0:8000 home_cinema.wsgi:application
pause
