@echo off
title Sharky TikTok Automation Suite - by SharkySolvers
color 0A

echo.
echo  ================================================
echo   Sharky TikTok Automation Suite - SharkySolvers
echo  ================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)

:: Install dependencies if needed
if not exist "venv" (
    echo  [*] Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo  [*] Installing dependencies...
    pip install -r scripts\requirements.txt --quiet
) else (
    call venv\Scripts\activate.bat
)

echo  [*] Launching suite...
echo.
python main.py

pause
