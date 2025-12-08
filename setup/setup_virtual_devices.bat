@echo off
REM Virtual Devices Automated Setup for NodeFlow
REM This script installs OBS Virtual Camera and VB-Audio Virtual Cable

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo  NodeFlow Virtual Devices Setup
echo ============================================================
echo.
echo This script will install:
echo   - OBS Virtual Camera (for video streaming)
echo   - VB-Audio Virtual Cable (for audio streaming)
echo.
echo Prerequisites:
echo   - Administrator rights
echo   - Internet connection (to download installers if needed)
echo   - Windows 10/11
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo.
    echo To run as Administrator:
    echo   1. Right-click this file
    echo   2. Select "Run as administrator"
    pause
    exit /b 1
)

echo [Step 1/3] Checking for OBS Virtual Camera...
REM Check if OBS Virtual Camera is already installed
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s | find /i "OBS" >nul
if %errorlevel% equ 0 (
    echo   ✓ OBS Virtual Camera appears to be installed
) else (
    echo   ⚠ OBS Virtual Camera not found
    echo.
    echo   Download from: https://obsproject.com/forum/resources/obs-virtualcam.949/
    echo   Then run the installer: OBS-*.exe
    echo.
    pause
)

echo.
echo [Step 2/3] Checking for VB-Audio Virtual Cable...
REM Check if VB-Cable is installed
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s | find /i "VB-CABLE" >nul
if %errorlevel% equ 0 (
    echo   ✓ VB-Audio Virtual Cable appears to be installed
) else (
    echo   ⚠ VB-Audio Virtual Cable not found
    echo.
    echo   Download from: https://vb-audio.com/Cable/
    echo   Then run: VBCABLE_Setup_x64.exe (for 64-bit Windows)
    echo.
    echo   NOTE: You may need to restart Windows after installation
    pause
)

echo.
echo [Step 3/3] Verifying Python packages...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo   Installing required Python packages...
cd /d "%~dp0backend"
pip install pyvirtualcam -q --no-warn-script-location 2>nul
pip install sounddevice -q --no-warn-script-location 2>nul

if %errorlevel% equ 0 (
    echo   ✓ Python packages installed
) else (
    echo   ⚠ Some packages failed to install
    echo   Run: pip install -r requirements.txt
)

echo.
echo ============================================================
echo  Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Start your NodeFlow mobile app
echo   2. Run: python src\receiver_gui.py
echo   3. Click "Connect"
echo   4. Your phone's camera/mic will appear as virtual devices
echo.
echo Verification:
echo   - Video: Check Discord/Zoom camera settings for "OBS Virtual Camera"
echo   - Audio: Check Windows Sound Settings for "CABLE Output"
echo.
echo For more information, see: VIRTUAL_DEVICES_SETUP.md
echo.
pause
