@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title School Management System - Quick Start

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
echo   SCHOOL MANAGEMENT SYSTEM - QUICK START                     
echo   One-Click Launch                                           
echo                                                                
echo ================================================================
echo %RESET%

:: Change to project root directory
cd /d "%~dp0.."

:: Check if virtual environment exists
if exist "venv\Scripts\python.exe" (
    echo %GREEN%[OK] Virtual environment found%RESET%
    set "PYTHON_EXE=venv\Scripts\python.exe"
    
    :: Check if psutil is installed
    %PYTHON_EXE% -c "import psutil" >nul 2>&1
    if %errorlevel% neq 0 (
        echo %YELLOW%[WARN] psutil not found, installing...%RESET%
        %PYTHON_EXE% ImpScripts\install_psutil.py
        if %errorlevel% neq 0 (
            echo %RED%[ERROR] Failed to install psutil%RESET%
        )
    )
) else (
    echo %YELLOW%[WARN] Virtual environment not found, using system Python%RESET%
    set "PYTHON_EXE=python"
)

:: Check if database exists
if exist "db.sqlite3" (
    echo %GREEN%[OK] Database found%RESET%
) else (
    echo %YELLOW%[WARN] Database not found, will create it%RESET%
    echo %CYAN%[INFO] Creating database...%RESET%
    %PYTHON_EXE% manage.py migrate
    if %errorlevel% neq 0 (
        echo %RED%[ERROR] Database creation failed%RESET%
        pause
        exit /b 1
    )
    echo %GREEN%[OK] Database created successfully%RESET%
)

:: Start the server
echo %CYAN%[INFO] Starting School Management System...%RESET%
echo %GREEN%[URL] Server will be available at: http://127.0.0.1:8000/%RESET%
echo %YELLOW%[TIP] Press Ctrl+C to stop the server%RESET%
echo.

%PYTHON_EXE% ImpScripts\start_server.py

pause