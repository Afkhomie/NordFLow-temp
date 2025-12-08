@echo off
REM Quick start script for NodeFlow Desktop Receiver with Virtual Devices

echo.
echo ============================================================
echo  NodeFlow Desktop Receiver
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Navigate to backend directory
cd /d "%~dp0backend"

REM Check if virtual devices are installed
echo Checking virtual devices...
echo.

REM Check OBS Virtual Camera
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s | find /i "OBS" >nul
if %errorlevel% neq 0 (
    echo ⚠ WARNING: OBS Virtual Camera not found
    echo   Your phone video won't be available in other apps
    echo   Install from: https://obsproject.com/forum/resources/obs-virtualcam.949/
    echo.
)

REM Check VB-Cable
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s | find /i "VB-CABLE" >nul
if %errorlevel% neq 0 (
    echo ⚠ WARNING: VB-Audio Virtual Cable not found
    echo   Your phone audio won't be available in other apps
    echo   Install from: https://vb-audio.com/Cable/
    echo.
)

echo.
echo ============================================================
echo  Starting NodeFlow Receiver...
echo ============================================================
echo.

REM Run the receiver GUI
python src\receiver_gui.py

pause
