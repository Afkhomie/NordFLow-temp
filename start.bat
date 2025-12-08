@echo off
REM NodeFlow - Windows Startup Script
REM This script starts the server and desktop receiver GUI

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"

echo.
echo ======================================
echo   NodeFlow - Desktop Media Streaming
echo   Setup & Launch Script
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org
    echo Then try running this script again.
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo        Python version: %PYTHON_VERSION%

REM Check if we're in the right directory
if not exist "%BACKEND_DIR%\src\run_dev.py" (
    echo [ERROR] Could not find backend files
    echo.
    echo This script must be run from the NodeFlow directory.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo [2/5] Installing Python dependencies...
cd /d "%BACKEND_DIR%"
python -m pip install -q --upgrade pip 2>nul
python -m pip install -q -r requirements.txt

if errorlevel 1 (
    echo [WARNING] Failed to install some dependencies
    echo           Continuing anyway...
)

echo [3/5] Verifying critical packages...
python -c "import aiohttp; import PyQt6; import websocket" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Critical packages missing
    echo.
    echo Please run: pip install aiohttp PyQt6 websocket-client
    echo.
    pause
    exit /b 1
)
echo        Core packages verified ✓

echo [4/5] Generating SSL certificates (if needed)...
if not exist "%BACKEND_DIR%\src\server.crt" (
    echo        Generating self-signed certificate...
    python src\generate_cert.py >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Could not auto-generate certificates
        echo           SSL may not work properly
    ) else (
        echo        Certificate generated ✓
    )
) else (
    echo        Using existing certificates ✓
)

echo [5/5] Starting services...
echo.
echo ======================================
echo   ✓ System Ready - Starting Services
echo ======================================
echo.

REM Determine local IP
for /f "tokens=4 delim=." %%i in ('route print ^| find "0.0.0.0" ^| findstr /r "192\. 10\. 172\."') do (
    for /f "tokens=1-4" %%a in ('getmacaddress.exe 2^>nul') do (
        set "LOCAL_IP=192.168.1.82"
    )
)

if not defined LOCAL_IP set "LOCAL_IP=192.168.1.82"

echo [Server] Backend HTTPS server starting...
echo          Access from phone: https://%LOCAL_IP%:5000
echo.
echo [Desktop] Receiver GUI starting...
echo           Watch for incoming video here
echo.
echo [Phone] Instructions:
echo         1. Open https://%LOCAL_IP%:5000 in your browser
echo         2. Accept the SSL certificate warning
echo         3. Press "Start Camera" to stream video
echo         4. Press "Start Microphone" to stream audio
echo.
echo [Info] Keep this window open. Close it to stop both services.
echo.

REM Start the server in background (minimized)
start "NodeFlow Server" /MIN cmd /c "cd /d "%BACKEND_DIR%\src" && python -u run_dev.py"

REM Wait for server to initialize
timeout /t 3 /nobreak

REM Start the receiver GUI
start "NodeFlow Receiver" cmd /c "cd /d "%BACKEND_DIR%\src" && python receiver.py"

echo.
echo ======================================
echo   ✓ NodeFlow is running
echo ======================================
echo.
echo Open your phone browser to: https://%LOCAL_IP%:5000
echo.
pause
echo Services started. You can now:
echo 1. Open your phone browser to: https://192.168.1.82:5000
echo 2. Use the desktop receiver to view streams
echo.
echo Press any key to continue...
pause >nul

exit /b 0
