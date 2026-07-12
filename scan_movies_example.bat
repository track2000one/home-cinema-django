@echo off
cd /d "%~dp0"

if not exist ".venv" (
  echo Virtual environment not found.
  echo Run start_server.bat first.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat

echo Edit the movie folder path below before running this file.
python manage.py scan_movies "E:\Movies" --recursive

pause
