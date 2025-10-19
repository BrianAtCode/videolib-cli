@echo off
title VideoLib - Enhanced with 'q' interrupt

echo VideoLib - Video Processing Tool (Enhanced with 'q' interrupt)
echo =============================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found! Please install Python 3.6+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo -> Features:
echo    • Real-time FFmpeg monitoring
echo    • Press 'q' during operations to cancel and return to menu
echo    • Cross-platform keyboard interrupt support
echo    • Graceful process termination
echo.
echo -> Launching enhanced CLI...
REM Run the launcher
python main.py
pause
