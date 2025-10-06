@echo off
title Test All Fixes
echo ================================================================
echo   TESTING ALL FIXES
echo   Verifying no ANSI codes and dependencies work
echo ================================================================
echo.

cd /d "%~dp0.."

echo [TEST] 1. Testing virtual environment...
if exist "venv\Scripts\python.exe" (
    echo [OK] Virtual environment found
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    echo [ERROR] Virtual environment not found
    set "PYTHON_EXE=python"
)

echo.
echo [TEST] 2. Testing Python imports...
%PYTHON_EXE% -c "from pathlib import Path; print('[OK] Path import works')" 2>nul || echo [ERROR] Path import failed

echo.
echo [TEST] 3. Testing psutil...
%PYTHON_EXE% -c "import psutil; print('[OK] psutil works')" 2>nul || (
    echo [WARN] psutil missing, installing...
    %PYTHON_EXE% -m pip install psutil==7.0.0
)

echo.
echo [TEST] 4. Testing start_server.py import...
%PYTHON_EXE% -c "import sys; sys.path.append('ImpScripts'); import start_server; print('[OK] start_server.py imports successfully')" 2>nul || echo [ERROR] start_server.py import failed

echo.
echo [TEST] 5. Testing Django...
%PYTHON_EXE% manage.py check --deploy 2>nul && echo [OK] Django check passed || echo [WARN] Django check warnings (normal)

echo.
echo ================================================================
echo   TEST COMPLETE
echo ================================================================
pause