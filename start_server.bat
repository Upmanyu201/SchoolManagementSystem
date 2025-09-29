@echo off
chcp 65001 >nul
title School Management System - Smart Launcher
color 0B

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo [INFO] Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if manage.py exists
if not exist "manage.py" (
    echo [ERROR] manage.py not found! Please run from Django project root.
    pause
    exit /b 1
)

REM Install required packages if not present
echo [INFO] Checking dependencies...
python -c "import psutil" 2>nul || (
    echo [INFO] Installing psutil...
    pip install psutil
)

REM Check license status
echo [INFO] Checking application status...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings'); import django; django.setup(); from demo.services import LicenseService; status = LicenseService.get_demo_status(); print('Licensed Version' if status.is_licensed else f'Demo: {status.days_remaining} days' if status.is_active else 'Activation Required')" 2>nul

REM Run the Python startup script
echo [INFO] Starting School Management System...
python start_server.py

pause