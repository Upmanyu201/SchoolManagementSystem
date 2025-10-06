@echo off
chcp 65001 >nul
title School Management System - Production Mode
color 0C

echo ========================================
echo   PRODUCTION MODE STARTUP
echo ========================================
echo.

:: Change to project root directory
cd /d "%~dp0.."

:: Set production environment variables
set PRODUCTION=true
set DEBUG=False
set DJANGO_SETTINGS_MODULE=config.settings

:: Call the main startup script with production flag
call ImpScripts\start_server.bat --production

pause