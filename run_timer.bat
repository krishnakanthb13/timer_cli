@echo off
setlocal
title Timer CLI Launcher

echo [INFO] Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python to run this application.
    pause
    exit /b 1
)

echo [INFO] Python found.
echo [INFO] Launching Timer CLI...

:: Navigate to script directory to ensure relative paths work
cd /d "%~dp0"

:: Run the application
python -m src.main

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error code %errorlevel%.
    pause
)

endlocal
