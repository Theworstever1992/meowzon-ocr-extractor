@echo off
REM Meowzon OCR Extractor - Windows Launcher
REM This batch file makes it easier to run Meowzon on Windows

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found. Please run this script from the Meowzon directory.
    pause
    exit /b 1
)

REM Run the main script with all arguments passed through
python main.py %*

REM Pause if run by double-clicking (not from command line)
if "%1"=="" (
    echo.
    echo To process screenshots:
    echo   run_meowzon.bat -i ./screenshots -o orders.csv
    echo.
    echo For help:
    echo   run_meowzon.bat --help
    echo.
    pause
)
