@echo off
title School Management System - Setup
color 0A

echo.
echo ========================================
echo   🎓 School Management System Setup
echo ========================================
echo.

echo 📋 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.12+ first.
    pause
    exit /b 1
)
echo ✅ Python found!

echo.
echo 📦 Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created!
) else (
    echo ✅ Virtual environment already exists!
)

echo.
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo 📥 Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ Failed to install dependencies!
    pause
    exit /b 1
)
echo ✅ Dependencies installed!

echo.
echo 🗄️ Setting up database...
python manage.py migrate --verbosity=0
if errorlevel 1 (
    echo ❌ Database migration failed!
    pause
    exit /b 1
)
echo ✅ Database ready!

echo.
echo 📊 Collecting static files...
python manage.py collectstatic --noinput --verbosity=0
echo ✅ Static files collected!

echo.
echo 🎉 Setup completed successfully!
echo.
echo 💡 Next steps:
echo    1. Run 'start_school_system.bat' to start the server
echo    2. Access the system via the displayed URLs
echo.
pause