@echo off

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found! Please install Python 3.6+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Run the launcher
python main.py
pause
