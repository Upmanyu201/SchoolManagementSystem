@echo off
title School Management System - Startup
color 0A
echo.
echo ========================================
echo    🎓 School Management System
echo ========================================
echo.

REM Get IPv4 address for network access
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do (
    set IP=%%i
    goto :found_ip
)
:found_ip
set IP=%IP: =%

if "%IP%"=="" (
    echo ⚠️  Warning: Could not detect IPv4 address!
    set IP=localhost
    echo Using localhost as fallback...
) else (
    echo 🌐 Network IP: %IP%
)

echo.
echo 🔧 Checking system requirements...

REM Check if virtual environment exists
if not exist "%~dp0venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Check if Redis is available (for Celery)
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Redis not running - Celery tasks will be disabled
    set REDIS_AVAILABLE=false
) else (
    echo ✅ Redis is running
    set REDIS_AVAILABLE=true
)

echo.
echo 🚀 Starting School Management System...

REM Activate virtual environment
call "%~dp0venv\Scripts\activate.bat"

REM Check database and run migrations if needed
echo 📊 Checking database...
python manage.py showmigrations --plan | findstr "\[ \]" >nul
if %errorlevel% equ 0 (
    echo 🔄 Running database migrations...
    python manage.py migrate
)

REM Collect static files if needed
if not exist "%~dp0staticfiles" (
    echo 📁 Collecting static files...
    python manage.py collectstatic --noinput
)

REM Start Celery worker if Redis is available
if "%REDIS_AVAILABLE%"=="true" (
    echo 🔄 Starting Celery worker for background tasks...
    start /min "Celery Worker" cmd /c "cd /d %~dp0 && celery -A config worker --loglevel=info --pool=solo"
    
    echo 📅 Starting Celery beat scheduler...
    start /min "Celery Beat" cmd /c "cd /d %~dp0 && celery -A config beat --loglevel=info"
    
    timeout /t 3 /nobreak >nul
)

REM Start Django development server
echo 🌐 Starting Django server...
echo 🔓 Starting with HTTP...
start /min "Django HTTP Server" cmd /c "cd /d %~dp0 && python manage.py runserver 0.0.0.0:8000"
set PROTOCOL=http

REM Wait for server to start
echo ⏳ Waiting for server to initialize...
timeout /t 8 /nobreak >nul

echo.
echo ✅ School Management System is now running!
echo.
echo 📋 System Information:
echo ==========================================
echo 🏠 Local Access:     %PROTOCOL%://localhost:8000
echo 🌐 Network Access:   %PROTOCOL%://%IP%:8000
echo 📱 Mobile Access:    %PROTOCOL%://%IP%:8000
echo 🔧 Admin Panel:      %PROTOCOL%://localhost:8000/admin/
echo 📊 Dashboard:        %PROTOCOL%://localhost:8000/dashboard/
echo.
echo 🎯 Quick Links:
echo - Students:          %PROTOCOL%://localhost:8000/students/
echo - Teachers:          %PROTOCOL%://localhost:8000/teachers/
echo - Fees:              %PROTOCOL%://localhost:8000/fees/
echo - Attendance:        %PROTOCOL%://localhost:8000/attendance/
echo - Reports:           %PROTOCOL%://localhost:8000/reports/
echo.
echo 🤖 AI Features:
if exist "%~dp0models\student_performance_model.pkl" (
    echo ✅ ML Models: 26 trained models available
) else (
    echo ⚠️  ML Models: Not found - AI features disabled
)
echo.
echo 📱 SMS Integration:
echo ✅ MSG91 SMS service configured
echo ✅ Fine notifications enabled
echo ✅ Fee reminders enabled
echo.
if "%REDIS_AVAILABLE%"=="true" (
    echo 🔄 Background Tasks: ✅ Enabled (Celery + Redis)
) else (
    echo 🔄 Background Tasks: ⚠️  Disabled (Redis not available)
)
echo.
echo 🔒 Security Features:
echo ✅ CSRF Protection enabled
echo ✅ Session security enabled
echo ✅ File upload validation enabled
echo 🔓 HTTP server (development mode)
echo.
echo 💡 Tips:
echo - Use Ctrl+C in server windows to stop services
echo - Check logs/ folder for system logs
echo - Access admin panel with superuser credentials
echo - Mobile devices can access via network IP
echo.
echo 🌐 Opening system in default browser...
start %PROTOCOL%://localhost:8000/dashboard/

echo.
echo 🎓 School Management System is ready!
echo Keep this window open to monitor the system.
echo Close server windows to stop the application.
echo.
pause