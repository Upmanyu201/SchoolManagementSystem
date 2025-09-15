@echo off
title School Management System - Server
color 0B

echo.
echo ========================================
echo   🎓 School Management System Server
echo ========================================
echo.

echo 🔍 Detecting network interfaces...

:: Get Wi-Fi IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"Wireless LAN adapter Wi-Fi" /A:1 ^| findstr "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do set WIFI_IP=%%b
)

:: Get Mobile Hotspot IP (check multiple possible adapter names)
set HOTSPOT_IP=
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"Local Area Connection\*" /A:5 ^| findstr "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        if not defined HOTSPOT_IP set HOTSPOT_IP=%%b
    )
)

:: Clean up IPs (remove extra spaces)
if defined WIFI_IP set WIFI_IP=%WIFI_IP: =%
if defined HOTSPOT_IP set HOTSPOT_IP=%HOTSPOT_IP: =%

echo.
echo 📡 Network Status:
if defined WIFI_IP (
    echo    ✅ Wi-Fi: %WIFI_IP%
) else (
    echo    ❌ Wi-Fi: Not connected
)

if defined HOTSPOT_IP (
    echo    ✅ Mobile Hotspot: %HOTSPOT_IP%
) else (
    echo    ❌ Mobile Hotspot: Not active
)

echo.
echo 🔧 Activating virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found! Run setup_school_system.bat first.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat

echo.
echo 🚀 Starting Django development server...
echo.
echo 🌐 Access URLs:
echo    📱 Local: http://127.0.0.1:8000/

if defined WIFI_IP (
    echo    📶 Wi-Fi Network: http://%WIFI_IP%:8000/
)

if defined HOTSPOT_IP (
    echo    📡 Mobile Hotspot: http://%HOTSPOT_IP%:8000/
)

echo.
echo 💡 Tips:
echo    • Use Wi-Fi URL for devices on same network
echo    • Use Hotspot URL when sharing internet via mobile hotspot
echo    • Press Ctrl+C to stop the server
echo.
echo ⏳ Server starting...

:: Start server on all interfaces
python manage.py runserver 0.0.0.0:8000