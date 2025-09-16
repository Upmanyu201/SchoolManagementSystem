@echo off
echo ========================================
echo School Management System - Production
echo ========================================

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run production deployment script
echo Running production deployment...
python deploy_production.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Production deployment successful!
    echo ========================================
    echo.
    echo Starting production server...
    echo Server will be available at: http://localhost:8000
    echo Press Ctrl+C to stop the server
    echo.
    
    REM Start the production server
    python manage.py runserver 0.0.0.0:8000
) else (
    echo.
    echo ========================================
    echo Production deployment failed!
    echo ========================================
    echo Please check the errors above and try again.
    pause
)