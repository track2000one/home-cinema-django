@echo off
cd /d "%~dp0"

if not exist ".venv" (
  echo Virtual environment not found.
  echo Run start_server.bat first.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
python manage.py makemigrations movies
python manage.py migrate
python manage.py collectstatic --noinput

echo.
echo Database and static files were repaired successfully.
echo Restart start_server.bat.
echo.
pause
