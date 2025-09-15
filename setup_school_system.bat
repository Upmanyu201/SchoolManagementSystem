@echo off
title School Management System - First Time Setup
color 0B
echo.
echo ========================================
echo    🎓 School Management System Setup
echo ========================================
echo.

echo 🔧 Setting up School Management System for first time...
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.12+ first.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Create virtual environment
if not exist "%~dp0venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call "%~dp0venv\Scripts\activate.bat"

REM Install requirements
echo 📥 Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install requirements!
    pause
    exit /b 1
)

echo ✅ Python packages installed

REM Run migrations
echo 📊 Setting up database...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ❌ Database migration failed!
    pause
    exit /b 1
)

echo ✅ Database setup complete

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo ⚠️  Static files collection failed (non-critical)
)

REM Create superuser prompt
echo.
echo 👤 Creating admin user...
echo Please create an admin account for the system:
python manage.py createsuperuser

REM Create necessary directories
if not exist "%~dp0logs" mkdir logs
if not exist "%~dp0media" mkdir media
if not exist "%~dp0backups" mkdir backups

echo.
echo ✅ Setup completed successfully!
echo.
echo 📋 What's been set up:
echo - ✅ Virtual environment created
echo - ✅ Python packages installed  
echo - ✅ Database initialized
echo - ✅ Static files collected
echo - ✅ Admin user created
echo - ✅ Required directories created
echo.
echo 🚀 Next steps:
echo 1. Run 'start_school_system.bat' to start the application
echo 2. Access the system at http://localhost:8000
echo 3. Login with your admin credentials
echo 4. Configure school settings in the admin panel
echo.
echo 💡 Optional enhancements:
echo - Install Redis for background tasks (Celery)
echo - Set up HTTPS certificates for secure access
echo - Configure SMS settings for notifications
echo.
pause