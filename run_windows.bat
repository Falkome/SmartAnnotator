@echo off
REM Smart Annotator - Windows Launcher
REM Double-click this file to run on Windows

title Smart Annotator

echo.
echo ====================================================
echo Smart Annotator - Starting...
echo ====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo.
    echo Install Python 3.8+ from python.org
    echo Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Run universal launcher
python run.py

REM Keep window open on error
if errorlevel 1 (
    echo.
    echo Application exited with errors
    pause
)

