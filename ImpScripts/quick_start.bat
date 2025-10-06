@echo off
:: 🚀 Quick Start Script - One-Click School Management System Launch
:: For users who just want to run the system quickly

setlocal enabledelayedexpansion
title School Management System - Quick Start

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
echo ║  🚀 SCHOOL MANAGEMENT SYSTEM - QUICK START                  ║
echo ║  ⚡ One-Click Launch                                        ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo %RESET%

:: Check if virtual environment exists
if exist "venv\Scripts\python.exe" (
    echo %GREEN%✅ Virtual environment found%RESET%
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    echo %YELLOW%⚠️  Virtual environment not found, using system Python%RESET%
    set "PYTHON_EXE=python"
)

:: Check if database exists
if exist "db.sqlite3" (
    echo %GREEN%✅ Database found%RESET%
) else (
    echo %YELLOW%⚠️  Database not found, will create it%RESET%
    echo %CYAN%🔧 Creating database...%RESET%
    %PYTHON_EXE% manage.py migrate
    if %errorlevel% neq 0 (
        echo %RED%❌ Database creation failed%RESET%
        pause
        exit /b 1
    )
    echo %GREEN%✅ Database created successfully%RESET%
)

:: Start the server
echo %CYAN%🚀 Starting School Management System...%RESET%
echo %GREEN%📍 Server will be available at: http://127.0.0.1:8000/%RESET%
echo %YELLOW%💡 Press Ctrl+C to stop the server%RESET%
echo.

%PYTHON_EXE% start_server.py

pause