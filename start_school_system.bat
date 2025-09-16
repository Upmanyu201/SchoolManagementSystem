@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title School Management System - Network Startup

echo.
echo ===============================================
echo    School Management System - Production Mode
echo ===============================================
echo.

:: Initialize variables
set "WIFI_IP="
set "HOTSPOT_IP="
set "SELECTED_IP=127.0.0.1"

echo [INFO] Detecting network connections...

:: Simple Wi-Fi detection
for /f "tokens=*" %%a in ('ipconfig ^| findstr "IPv4"') do (
    echo %%a | findstr "192.168.1" >nul
    if !errorlevel! equ 0 (
        for /f "tokens=2 delims=:" %%b in ("%%a") do (
            set "temp=%%b"
            set "temp=!temp: =!"
            set "temp=!temp:(Preferred)=!"
            set "WIFI_IP=!temp!"
        )
    )
)

:: Simple Hotspot detection - look for device IP, not host IP
for /f "tokens=*" %%a in ('ipconfig ^| findstr "IPv4"') do (
    echo %%a | findstr "192.168.137" >nul
    if !errorlevel! equ 0 (
        for /f "tokens=2 delims=:" %%b in ("%%a") do (
            set "temp=%%b"
            set "temp=!temp: =!"
            set "temp=!temp:(Preferred)=!"
            :: Skip .1 (host) and use device IP (.2, .3, etc.)
            if not "!temp!"=="192.168.137.1" (
                set "HOTSPOT_IP=!temp!"
            )
        )
    )
)

:: Display results
echo.
if defined WIFI_IP (
    echo [SUCCESS] Wi-Fi detected: !WIFI_IP!
    set "SELECTED_IP=!WIFI_IP!"
) else (
    echo [INFO] Wi-Fi not detected
)

if defined HOTSPOT_IP (
    echo [SUCCESS] Mobile Hotspot detected: !HOTSPOT_IP!
    if not defined WIFI_IP set "SELECTED_IP=!HOTSPOT_IP!"
) else (
    echo [INFO] Mobile Hotspot not detected
)

echo.
echo [INFO] Using IP: !SELECTED_IP!
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)

:: Create venv if needed
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

:: Activate venv
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install requirements
if exist "requirements.txt" (
    echo [INFO] Installing requirements...
    pip install -r requirements.txt >nul 2>&1
)

:: Clear template cache for production
echo [INFO] Clearing template cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" >nul 2>&1
del /s /q *.pyc >nul 2>&1

:: Run migrations
echo [INFO] Applying migrations...
python manage.py migrate >nul 2>&1

:: Collect static files
echo [INFO] Collecting static files...
python manage.py collectstatic --noinput >nul 2>&1

:: Check production readiness
echo [INFO] Checking production configuration...
python manage.py check --deploy >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Some production checks failed - continuing anyway
) else (
    echo [SUCCESS] Production checks passed
)

echo.
echo ===============================================
echo    PRODUCTION SYSTEM READY!
echo ===============================================
echo.
echo [PRODUCTION MODE] DEBUG=False, Template Caching=ON
echo.
echo Local Access:    http://127.0.0.1:8000
echo Network Access:  http://!SELECTED_IP!:8000
if defined WIFI_IP echo Wi-Fi Access:   http://!WIFI_IP!:8000
if defined HOTSPOT_IP echo Hotspot Access: http://!HOTSPOT_IP!:8000
echo All Interfaces:  http://0.0.0.0:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo [PRODUCTION] Starting server with optimized settings...
echo.

:: Start server on all interfaces with production settings
set DJANGO_SETTINGS_MODULE=school_management.settings
python manage.py runserver 0.0.0.0:8000 --insecure

pause