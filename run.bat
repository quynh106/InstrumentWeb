@echo off
echo ========================================
echo InstrumentWeb - Starting Django Server
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo [1/2] Activating virtual environment... OK
echo.

REM Run server
echo [2/2] Starting Django server...
echo.
echo Server will run at: http://127.0.0.1:8000/
echo Admin Panel at: http://127.0.0.1:8000/adminpanel/
echo Django Admin at: http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
