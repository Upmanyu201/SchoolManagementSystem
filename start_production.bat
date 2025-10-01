@echo off
chcp 65001 >nul
title School Management System - Production Mode
color 0C

echo ========================================
echo   PRODUCTION MODE STARTUP
echo ========================================
echo.

REM Set production environment variables
set PRODUCTION=true
set DEBUG=False
set DJANGO_SETTINGS_MODULE=school_management.settings

REM Call the main startup script with production flag
call start_server.bat --production

pause