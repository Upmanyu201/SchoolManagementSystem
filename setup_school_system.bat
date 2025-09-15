@echo off
chcp 65001 >nul
title School Management System - Setup
color 0A

echo.
echo ========================================
echo   🎓 School Management System Setup
echo ========================================
echo.

echo 📡 Detecting network interfaces...
call :detect_network

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
if defined HOTSPOT_IP (
    echo 📡 Mobile Hotspot detected: http://%HOTSPOT_IP%:8000/
)
if defined WIFI_IP (
    echo 📶 Wi-Fi Network: http://%WIFI_IP%:8000/
)
echo.
pause

:detect_network
setlocal enabledelayedexpansion
set WIFI_IP=
set HOTSPOT_IP=
set HOTSPOT_ACTIVE=false

:: Check for active mobile hotspot service
sc query "icssvc" 2>nul | findstr "RUNNING" >nul 2>&1
if not errorlevel 1 set HOTSPOT_ACTIVE=true

:: Check netsh for mobile hotspot status
netsh wlan show hostednetwork 2>nul | findstr "Started" >nul 2>&1
if not errorlevel 1 set HOTSPOT_ACTIVE=true

:: Detect IP addresses
for /f "tokens=2 delims=:" %%a in ('ipconfig 2^>nul ^| findstr /i "IPv4"') do (
    set "ip=%%a"
    set "ip=!ip: =!"
    
    :: Standard Wi-Fi ranges
    echo !ip! | findstr "^192\.168\.1\." >nul && set WIFI_IP=!ip!
    echo !ip! | findstr "^192\.168\.0\." >nul && set WIFI_IP=!ip!
    echo !ip! | findstr "^10\.0\.0\." >nul && set WIFI_IP=!ip!
    
    :: Mobile hotspot ranges
    echo !ip! | findstr "^192\.168\.137\." >nul && set HOTSPOT_IP=!ip!
    echo !ip! | findstr "^192\.168\.43\." >nul && set HOTSPOT_IP=!ip!
    echo !ip! | findstr "^192\.168\.42\." >nul && set HOTSPOT_IP=!ip!
    echo !ip! | findstr "^172\.20\.10\." >nul && set HOTSPOT_IP=!ip!
)

echo.
echo 📡 Network Status:
if defined WIFI_IP (
    echo    ✅ Wi-Fi: Connected (!WIFI_IP!)
) else (
    echo    ❌ Wi-Fi: Not connected
)

if defined HOTSPOT_IP (
    echo    ✅ Mobile Hotspot: Active (!HOTSPOT_IP!)
) else (
    if "!HOTSPOT_ACTIVE!"=="true" (
        echo    ⚠️ Mobile Hotspot: Service running but no IP detected
    ) else (
        echo    ❌ Mobile Hotspot: Not active
    )
)
endlocal & set WIFI_IP=%WIFI_IP% & set HOTSPOT_IP=%HOTSPOT_IP%
goto :eof