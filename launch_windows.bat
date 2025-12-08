@echo off
REM NodeFlow Windows Setup & Launch Script
REM One-click setup and launch with OBS Virtual Camera + VB-Cable

echo.
echo ======================================
echo  NodeFlow - Windows Setup & Launch
echo ======================================
echo.

REM Check if OBS is installed
echo Checking for OBS Studio...
if exist "C:\Program Files\obs-studio\bin\obs64.exe" (
    echo ✓ OBS Studio found
    set OBS_INSTALLED=1
) else if exist "C:\Program Files (x86)\obs-studio\bin\obs32.exe" (
    echo ✓ OBS Studio found
    set OBS_INSTALLED=1
) else (
    echo ✗ OBS Studio not found
    echo   Please install from: https://obsproject.com/
    set OBS_INSTALLED=0
)

echo.
echo Checking for VB-Cable...
if exist "C:\Program Files\VB\Audio\VBCable" (
    echo ✓ VB-Cable found
    set VBCABLE_INSTALLED=1
) else (
    echo ! VB-Cable not found (optional for audio)
    echo   Install from: https://vb-audio.com/Cable/
    set VBCABLE_INSTALLED=0
)

echo.
echo ======================================
echo  Startup Options
echo ======================================
echo.
echo 1. Start PC Receiver GUI (recommended)
echo 2. Start PC Receiver Console (headless)
echo 3. Launch with OBS automation (requires OBS + obs-websocket)
echo 4. Start audio router (requires VB-Cable)
echo 5. Exit
echo.

setlocal enabledelayedexpansion
set /p CHOICE="Enter choice (1-5): "

if "%CHOICE%"=="1" (
    echo.
    echo Starting NodeFlow Receiver GUI...
    echo.
    call dist\NodeFlowReceiverGUI.exe
) else if "%CHOICE%"=="2" (
    echo.
    echo Starting NodeFlow Receiver Console...
    echo.
    call dist\NodeFlowReceiverConsole.exe
) else if "%CHOICE%"=="3" (
    if "%OBS_INSTALLED%"=="0" (
        echo OBS Studio not found. Please install it first.
        pause
        exit /b 1
    )
    echo.
    echo Launching OBS automation...
    echo Note: Make sure OBS WebSocket plugin is installed
    echo.
    set /p STREAM_URL="Enter NodeFlow server URL (default https://192.168.1.82:5000): "
    if "!STREAM_URL!"=="" set STREAM_URL=https://192.168.1.82:5000
    python backend\src\obs_automation.py --stream-url !STREAM_URL!
) else if "%CHOICE%"=="4" (
    if "%VBCABLE_INSTALLED%"=="0" (
        echo VB-Cable not found. Please install it first.
        echo https://vb-audio.com/Cable/
        pause
        exit /b 1
    )
    echo.
    echo Starting audio router for VB-Cable...
    echo.
    python backend\src\audio_routing_windows.py --output-device "Cable Input"
) else (
    echo Exiting.
    exit /b 0
)

pause
