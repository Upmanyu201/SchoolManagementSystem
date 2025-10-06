@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title School Management System - Master Setup

:: Colors disabled for CMD compatibility
set "GREEN="
set "RED="
set "YELLOW="
set "BLUE="
set "CYAN="
set "RESET="

echo %CYAN%
echo ================================================================
echo                                                                
echo   SCHOOL MANAGEMENT SYSTEM - MASTER SETUP                    
echo   Windows Automated Deployment                               
echo                                                                
echo ================================================================
echo %RESET%

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo %RED%[ERROR] This script requires administrator privileges%RESET%
    echo %YELLOW%[INFO] Right-click and select "Run as administrator"%RESET%
    pause
    exit /b 1
)

echo %GREEN%[OK] Running with administrator privileges%RESET%

:: Set script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Main menu
:MAIN_MENU
cls
echo %CYAN%
echo ================================================================
echo                     SETUP OPTIONS                             
echo ================================================================
echo %RESET%
echo %GREEN%1.%RESET% [SETUP] Complete Fresh Installation (Recommended)
echo %GREEN%2.%RESET% [PYTHON] Install Python Only
echo %GREEN%3.%RESET% [VENV] Setup Virtual Environment
echo %GREEN%4.%RESET% [DATABASE] Database Setup (Clean)
echo %GREEN%5.%RESET% [MIGRATE] Reset Migrations
echo %GREEN%6.%RESET% [SERVER] Start Development Server
echo %GREEN%7.%RESET% [TEST] Run System Tests
echo %GREEN%8.%RESET% [FIX] Fix Common Issues
echo %GREEN%9.%RESET% [HEALTH] System Health Check
echo %GREEN%0.%RESET% [EXIT] Exit
echo.

set /p choice="[INPUT] Select option (0-9): "

if "%choice%"=="1" goto COMPLETE_SETUP
if "%choice%"=="2" goto PYTHON_SETUP
if "%choice%"=="3" goto VENV_SETUP
if "%choice%"=="4" goto DB_SETUP
if "%choice%"=="5" goto RESET_MIGRATIONS
if "%choice%"=="6" goto START_SERVER
if "%choice%"=="7" goto RUN_TESTS
if "%choice%"=="8" goto FIX_ISSUES
if "%choice%"=="9" goto HEALTH_CHECK
if "%choice%"=="0" goto EXIT
goto MAIN_MENU

:COMPLETE_SETUP
echo %CYAN%[SETUP] Starting Complete Fresh Installation...%RESET%
call python check_system.py
if %errorlevel% neq 0 (
    echo %RED%[ERROR] System check failed%RESET%
    pause
    goto MAIN_MENU
)

call python install_python.py
call python setup_environment.py
call python install_psutil.py
call python database_setup.py
call python run_tests.py
echo %GREEN%[OK] Complete setup finished!%RESET%
pause
goto MAIN_MENU

:PYTHON_SETUP
echo %CYAN%[PYTHON] Installing Python...%RESET%
call python install_python.py
pause
goto MAIN_MENU

:VENV_SETUP
echo %CYAN%[VENV] Setting up Virtual Environment...%RESET%
call python setup_environment.py
pause
goto MAIN_MENU

:DB_SETUP
echo %CYAN%[DATABASE] Setting up Database...%RESET%
call python database_setup.py
pause
goto MAIN_MENU

:RESET_MIGRATIONS
echo %CYAN%[MIGRATE] Resetting Migrations...%RESET%
call python reset_migrations.py
pause
goto MAIN_MENU

:START_SERVER
echo %CYAN%[SERVER] Starting Development Server...%RESET%
call python start_server.py
pause
goto MAIN_MENU

:RUN_TESTS
echo %CYAN%[TEST] Running System Tests...%RESET%
call python run_tests.py
pause
goto MAIN_MENU

:FIX_ISSUES
echo %CYAN%[FIX] Fixing Common Issues...%RESET%
call python fix_common_issues.py
pause
goto MAIN_MENU

:HEALTH_CHECK
echo %CYAN%[HEALTH] Running System Health Check...%RESET%
call python system_health.py
pause
goto MAIN_MENU

:EXIT
echo %GREEN%[EXIT] Thank you for using School Management System!%RESET%
exit /b 0