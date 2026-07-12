@echo off
cd /d "%~dp0"

if not exist ".venv" (
  echo لم يتم العثور على البيئة الافتراضية.
  echo شغّل start_server.bat أولاً.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install whitenoise
python manage.py collectstatic --noinput

echo.
echo تم إصلاح ملفات التصميم الثابتة.
echo أغلق الخادم القديم ثم شغّل start_server.bat من جديد.
echo.
pause
