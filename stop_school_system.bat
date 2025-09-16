@echo off
title School Management System - Stop Server
color 0C

echo.
echo ========================================
echo   🎓 School Management System - Stop Production
echo ========================================
echo.

echo 🔍 Checking for running Django processes...

:: Find and kill Django processes
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr "manage.py" >nul
if not errorlevel 1 (
    echo 🛑 Stopping Django server...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq *manage.py*" >nul 2>&1
    timeout /t 2 >nul
    echo ✅ Django server stopped!
) else (
    echo ℹ️  No Django server processes found.
)

:: Alternative method - kill by port
echo.
echo 🔍 Checking port 8000...
netstat -ano | findstr ":8000" >nul
if not errorlevel 1 (
    echo 🛑 Stopping processes on port 8000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    echo ✅ Port 8000 cleared!
) else (
    echo ℹ️  Port 8000 is free.
)

echo.
echo 🧹 Cleaning up production environment...
:: Clean up any remaining Python processes related to Django
wmic process where "name='python.exe' and commandline like '%%manage.py%%'" delete >nul 2>&1

:: Clear any temporary files
echo 🗑️ Clearing temporary files...
if exist "*.tmp" del /q *.tmp >nul 2>&1
if exist "temp\*" del /q temp\* >nul 2>&1

echo.
echo ✅ Production server stopped successfully!
echo.
echo 💡 To start production server again, run: start_school_system.bat
echo 🔧 To reconfigure production settings, run: setup_school_system.bat
echo.
pause