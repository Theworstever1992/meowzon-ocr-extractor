@echo off
REM Meowzon OCR Extractor - Windows Installation Script
echo ========================================
echo Meowzon OCR Extractor - Installation
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

echo Installing dependencies...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install core dependencies
echo Installing core dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo IMPORTANT: You also need to install Tesseract OCR for Windows
echo.
echo Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo Recommended: tesseract-ocr-w64-setup-5.3.3.20231005.exe (or latest)
echo.
echo Install to default location: C:\Program Files\Tesseract-OCR
echo.
echo After installing Tesseract, you can run:
echo   run_meowzon.bat --help
echo.
echo Optional AI providers:
echo   - For Ollama (local AI): Download from https://ollama.com
echo   - For OpenAI: Set OPENAI_API_KEY environment variable
echo   - For Claude: Set ANTHROPIC_API_KEY environment variable
echo   - For Gemini: Set GOOGLE_API_KEY environment variable
echo.
pause
