@echo off
chcp 65001 >nul
title School Management System - Smart Launcher
color 0B

echo.
echo +==============================================================+
echo ^|                                                              ^|
echo ^|    SCHOOL MANAGEMENT SYSTEM - SMART LAUNCHER                ^|
echo ^|                                                              ^|
echo ^|  * Auto Network Detection  * Mobile Hotspot Support        ^|
echo ^|  * Browser Auto-Launch     * Real-time Logs                ^|
echo ^|  * SSL Support             * One-Click Startup              ^|
echo ^|                                                              ^|
echo +==============================================================+
echo.

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

REM Run the Python startup script
echo [INFO] Starting School Management System...
python start_server.py

pause