@echo off
:: 🎓 School Management System - Master Setup Script
:: Automates complete Windows deployment with error handling

setlocal enabledelayedexpansion
title School Management System - Master Setup

:: Colors for output
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "RESET=[0m"

echo %CYAN%
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║  🎓 SCHOOL MANAGEMENT SYSTEM - MASTER SETUP                 ║
echo ║  🚀 Windows Automated Deployment                            ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo %RESET%

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo %RED%❌ This script requires administrator privileges%RESET%
    echo %YELLOW%💡 Right-click and select "Run as administrator"%RESET%
    pause
    exit /b 1
)

echo %GREEN%✅ Running with administrator privileges%RESET%

:: Set script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Main menu
:MAIN_MENU
cls
echo %CYAN%
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    SETUP OPTIONS                             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo %RESET%
echo %GREEN%1.%RESET% 🔧 Complete Fresh Installation (Recommended)
echo %GREEN%2.%RESET% 🐍 Install Python Only
echo %GREEN%3.%RESET% 📦 Setup Virtual Environment
echo %GREEN%4.%RESET% 🗄️  Database Setup (Clean)
echo %GREEN%5.%RESET% 🔄 Reset Migrations
echo %GREEN%6.%RESET% 🚀 Start Development Server
echo %GREEN%7.%RESET% 🧪 Run System Tests
echo %GREEN%8.%RESET% 🛠️  Fix Common Issues
echo %GREEN%9.%RESET% 📊 System Health Check
echo %GREEN%0.%RESET% ❌ Exit
echo.

set /p choice="🎯 Select option (0-9): "

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
echo %CYAN%🚀 Starting Complete Fresh Installation...%RESET%
call python check_system.py
if %errorlevel% neq 0 (
    echo %RED%❌ System check failed%RESET%
    pause
    goto MAIN_MENU
)

call python install_python.py
call python setup_environment.py
call python database_setup.py
call python install_dependencies.py
call python run_tests.py
echo %GREEN%✅ Complete setup finished!%RESET%
pause
goto MAIN_MENU

:PYTHON_SETUP
echo %CYAN%🐍 Installing Python...%RESET%
call python install_python.py
pause
goto MAIN_MENU

:VENV_SETUP
echo %CYAN%📦 Setting up Virtual Environment...%RESET%
call python setup_environment.py
pause
goto MAIN_MENU

:DB_SETUP
echo %CYAN%🗄️ Setting up Database...%RESET%
call python database_setup.py
pause
goto MAIN_MENU

:RESET_MIGRATIONS
echo %CYAN%🔄 Resetting Migrations...%RESET%
call python reset_migrations.py
pause
goto MAIN_MENU

:START_SERVER
echo %CYAN%🚀 Starting Development Server...%RESET%
call python start_server.py
pause
goto MAIN_MENU

:RUN_TESTS
echo %CYAN%🧪 Running System Tests...%RESET%
call python run_tests.py
pause
goto MAIN_MENU

:FIX_ISSUES
echo %CYAN%🛠️ Fixing Common Issues...%RESET%
call python fix_common_issues.py
pause
goto MAIN_MENU

:HEALTH_CHECK
echo %CYAN%📊 Running System Health Check...%RESET%
call python system_health.py
pause
goto MAIN_MENU

:EXIT
echo %GREEN%👋 Thank you for using School Management System!%RESET%
exit /b 0