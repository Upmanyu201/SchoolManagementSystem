@echo off
title School Management System - Shutdown
color 0C
echo.
echo ========================================
echo    🛑 Stopping School Management System
echo ========================================
echo.

echo 🔄 Stopping Django server...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Django*" >nul 2>&1

echo 🔄 Stopping Celery worker...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Celery Worker*" >nul 2>&1

echo 🔄 Stopping Celery beat scheduler...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Celery Beat*" >nul 2>&1

echo 🔄 Cleaning up processes...
timeout /t 2 /nobreak >nul

echo.
echo ✅ School Management System stopped successfully!
echo.
echo 📋 System Status:
echo - Django Server: Stopped
echo - Celery Worker: Stopped  
echo - Celery Beat: Stopped
echo.
echo 💡 All services have been terminated.
echo You can now safely close this window.
echo.
pause