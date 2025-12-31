@echo off
REM ============================================================================
REM Meowzon v3.0 GitHub Deployment Script (Windows)
REM ============================================================================
REM This script automates deployment to GitHub on Windows
REM
REM Prerequisites:
REM - Git installed and configured
REM - GitHub repository already exists
REM - You have push access to the repository
REM
REM Usage:
REM   deploy_to_github.bat
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo       /\_/\      
echo      ( o.o )     MEOWZON v3.0 
echo       ^> ^ ^<      GitHub Deployment
echo      /^|   ^|\     
echo     (_^|   ^|_)    
echo.

REM Configuration
set REPO_URL=https://github.com/Theworstever1992/meowzon-ocr-extractor.git
set BACKUP_BRANCH=backup-v2.0
set MAIN_BRANCH=main
set VERSION_TAG=v3.0.0

REM ============================================================================
REM Step 1: Check if in git repository
REM ============================================================================

echo [Step 1/10] Checking git repository...
if not exist ".git" (
    echo Error: Not in a git repository!
    echo.
    echo Please navigate to your repository folder first:
    echo   cd C:\path\to\meowzon-ocr-extractor
    echo.
    echo Or clone the repository if you don't have it locally:
    echo   git clone %REPO_URL%
    echo   cd meowzon-ocr-extractor
    pause
    exit /b 1
)
echo OK: Git repository detected
echo.

REM ============================================================================
REM Step 2: Check for uncommitted changes
REM ============================================================================

echo [Step 2/10] Checking for uncommitted changes...
git status --porcelain > temp_status.txt
set /p STATUS=<temp_status.txt
del temp_status.txt

if not "!STATUS!"=="" (
    echo Warning: You have uncommitted changes
    echo.
    git status --short
    echo.
    set /p CONTINUE="Do you want to continue? This will stash your changes. (Y/N): "
    if /i not "!CONTINUE!"=="Y" (
        echo Deployment cancelled
        pause
        exit /b 1
    )
    git stash save "Auto-stash before v3.0 deployment"
    echo OK: Changes stashed
) else (
    echo OK: Working directory clean
)
echo.

REM ============================================================================
REM Step 3: Fetch latest changes
REM ============================================================================

echo [Step 3/10] Fetching latest changes...
git fetch origin
echo OK: Fetched latest changes
echo.

REM ============================================================================
REM Step 4: Create backup branch
REM ============================================================================

echo [Step 4/10] Creating backup branch...

REM Check current branch
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set CURRENT_BRANCH=%%i

REM Switch to main if needed
if not "!CURRENT_BRANCH!"=="%MAIN_BRANCH%" (
    git checkout %MAIN_BRANCH%
)

REM Check if backup branch exists
git show-ref --verify --quiet refs/heads/%BACKUP_BRANCH% 2>nul
if !errorlevel! equ 0 (
    echo Warning: Backup branch '%BACKUP_BRANCH%' already exists
    set /p OVERWRITE="Overwrite it? (Y/N): "
    if /i "!OVERWRITE!"=="Y" (
        git branch -D %BACKUP_BRANCH%
        echo OK: Deleted old backup branch
    )
)

git checkout -b %BACKUP_BRANCH%
git push -f origin %BACKUP_BRANCH%
echo OK: Created and pushed backup branch: %BACKUP_BRANCH%

git checkout %MAIN_BRANCH%
echo.

REM ============================================================================
REM Step 5: Remove old files
REM ============================================================================

echo [Step 5/10] Cleaning up old files...

if exist "meowzon_ocr_extractor.py" (
    echo Found old meowzon_ocr_extractor.py
    set /p ARCHIVE="Move to archive? (Y/N): "
    if /i "!ARCHIVE!"=="Y" (
        if not exist "archive" mkdir archive
        git mv meowzon_ocr_extractor.py archive/
        echo OK: Moved old file to archive/
    ) else (
        git rm meowzon_ocr_extractor.py
        echo OK: Removed old file
    )
)

echo OK: Cleanup complete
echo.

REM ============================================================================
REM Step 6: Verify new files
REM ============================================================================

echo [Step 6/10] Verifying new files...

set MISSING=0
if not exist "main.py" (echo Missing: main.py & set MISSING=1)
if not exist "setup.py" (echo Missing: setup.py & set MISSING=1)
if not exist "requirements.txt" (echo Missing: requirements.txt & set MISSING=1)
if not exist "README.md" (echo Missing: README.md & set MISSING=1)
if not exist "meowzon\__init__.py" (echo Missing: meowzon\__init__.py & set MISSING=1)
if not exist "meowzon\config.py" (echo Missing: meowzon\config.py & set MISSING=1)
if not exist "meowzon\extractor.py" (echo Missing: meowzon\extractor.py & set MISSING=1)

if %MISSING% equ 1 (
    echo.
    echo Error: Missing required files!
    echo Please ensure all v3.0 files are in the repository directory.
    pause
    exit /b 1
)

echo OK: All required files present
echo.

REM ============================================================================
REM Step 7: Add files
REM ============================================================================

echo [Step 7/10] Adding new files to git...
git add .
echo OK: Added all files
echo.

REM ============================================================================
REM Step 8: Commit
REM ============================================================================

echo [Step 8/10] Creating commit...

git commit -m "🎉 Major Release: Meowzon v3.0 - Complete Production Rewrite" -m "" -m "✨ New Features:" -m "- Modular architecture with 11+ specialized modules" -m "- Multi-AI provider support (Ollama, OpenAI, Claude, Gemini)" -m "- Parallel processing for 2-4x speed improvement" -m "- Interactive review mode for manual corrections" -m "- Rich analytics with automatic visualizations" -m "- Multiple output formats (CSV, Excel, JSON, HTML)" -m "" -m "See CHANGELOG.md for complete details."

echo OK: Commit created
echo.

REM ============================================================================
REM Step 9: Create tag
REM ============================================================================

echo [Step 9/10] Creating version tag...

git rev-parse %VERSION_TAG% >nul 2>&1
if !errorlevel! equ 0 (
    echo Warning: Tag '%VERSION_TAG%' already exists
    set /p DELETE_TAG="Delete and recreate? (Y/N): "
    if /i "!DELETE_TAG!"=="Y" (
        git tag -d %VERSION_TAG%
        git push origin :refs/tags/%VERSION_TAG%
        echo OK: Deleted old tag
        git tag -a %VERSION_TAG% -m "Meowzon v3.0.0 - Production-Ready AI Hybrid OCR Extractor"
        echo OK: Tag created: %VERSION_TAG%
    )
) else (
    git tag -a %VERSION_TAG% -m "Meowzon v3.0.0 - Production-Ready AI Hybrid OCR Extractor"
    echo OK: Tag created: %VERSION_TAG%
)
echo.

REM ============================================================================
REM Step 10: Push to GitHub
REM ============================================================================

echo [Step 10/10] Pushing to GitHub...
echo.
echo This will push to: %REPO_URL%
set /p PUSH="Continue? (Y/N): "
if /i not "!PUSH!"=="Y" (
    echo Push cancelled
    echo.
    echo Your changes are committed locally but not pushed.
    echo You can push manually later with:
    echo   git push origin %MAIN_BRANCH%
    echo   git push origin %VERSION_TAG%
    pause
    exit /b 1
)

echo.
echo Pushing to GitHub...
echo.

echo Pushing %MAIN_BRANCH% branch...
git push origin %MAIN_BRANCH%

echo Confirming backup branch...
git push origin %BACKUP_BRANCH%

echo Pushing %VERSION_TAG% tag...
git push origin %VERSION_TAG%

REM ============================================================================
REM Success!
REM ============================================================================

echo.
echo ============================================================
echo                   SUCCESS!
echo ============================================================
echo.
echo Deployment Complete!
echo.
echo What was deployed:
echo    - Main branch: %MAIN_BRANCH%
echo    - Backup branch: %BACKUP_BRANCH% (with old code)
echo    - Version tag: %VERSION_TAG%
echo.
echo Next Steps:
echo.
echo 1. View your repository:
echo    https://github.com/Theworstever1992/meowzon-ocr-extractor
echo.
echo 2. Create a GitHub Release:
echo    https://github.com/Theworstever1992/meowzon-ocr-extractor/releases/new
echo.
echo 3. Test the deployment:
echo    git clone %REPO_URL%
echo    cd meowzon-ocr-extractor
echo    python test_installation.py
echo.
echo Meowzon v3.0 is now live! Happy extracting!
echo.
pause
