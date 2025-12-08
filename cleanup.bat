@echo off
REM NodeFlow - Virtual Environment Cleanup Script
REM Removes unnecessary virtual environments while keeping project files

setlocal enabledelayedexpansion

echo.
echo ======================================
echo  NodeFlow - Cleanup Utility
echo ======================================
echo.

REM Check what venv directories exist
set venv_count=0
if exist ".\.venv" set /A venv_count+=1
if exist ".\venv" set /A venv_count+=1
if exist ".\env" set /A venv_count+=1

if %venv_count% equ 0 (
    echo No virtual environments found to clean.
    echo.
    pause
    exit /b 0
)

echo Found %venv_count% virtual environment(s) to clean:
echo.

if exist ".\.venv" (
    echo  1. .\.venv (Python 3.11 development environment)
    set "venv_path=.\.venv"
)

if exist ".\venv" (
    echo  2. .\venv
)

if exist ".\env" (
    echo  3. .\env
)

echo.
echo WARNING: This will DELETE virtual environments.
echo Project files will NOT be affected.
echo.
echo NOTE: Keep .venv if you plan to develop further
echo       Recreate with: python -m venv .venv
echo.
echo DO YOU WANT TO CONTINUE? (Y/N)
set /p response="Enter choice: "

if /i "%response%" neq "Y" (
    echo Cleanup cancelled.
    pause
    exit /b 0
)

echo.
echo Starting cleanup...
echo.

REM Remove virtual environments
if exist ".\.venv" (
    echo Removing .\.venv ...
    rmdir .\.venv /s /q >nul 2>&1
    if errorlevel 1 (
        echo  WARNING: Could not fully remove .\.venv
    ) else (
        echo  ✓ .\.venv removed
    )
)

if exist ".\venv" (
    echo Removing .\venv ...
    rmdir .\venv /s /q >nul 2>&1
    if errorlevel 1 (
        echo  WARNING: Could not fully remove .\venv
    ) else (
        echo  ✓ .\venv removed
    )
)

if exist ".\env" (
    echo Removing .\env ...
    rmdir .\env /s /q >nul 2>&1
    if errorlevel 1 (
        echo  WARNING: Could not fully remove .\env
    ) else (
        echo  ✓ .\env removed
    )
)

REM Remove Python cache files
echo.
echo Removing Python cache files...
for /r . %%D in (__pycache__) do (
    if exist "%%D" (
        rmdir "%%D" /s /q >nul 2>&1
    )
)
echo  ✓ Cache cleaned

REM Remove compiled Python files
for /r . %%F in (*.pyc) do (
    if exist "%%F" del /q "%%F" >nul 2>&1
)
echo  ✓ Compiled files cleaned

REM Remove pip cache (optional)
echo.
echo Cleaning pip cache...
python -m pip cache purge >nul 2>&1
if errorlevel 0 (
    echo  ✓ Pip cache cleaned
) else (
    echo  (Pip cache cleanup skipped)
)

echo.
echo ======================================
echo  Cleanup Complete!
echo ======================================
echo.
echo Space freed: ~500-1000 MB
echo.
echo To reinstall virtual environment:
echo   python -m venv .venv
echo   .\.venv\Scripts\Activate.ps1
echo   pip install -r backend/requirements.txt
echo.
pause
