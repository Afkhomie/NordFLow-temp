@echo off
REM Virtual Devices Setup & Launcher
REM One-click setup for virtual camera + microphone on Windows

echo.
echo ============================================================
echo  NodeFlow - Virtual Camera + Microphone Setup
echo ============================================================
echo.

REM Check for pyvirtualcam (OBS Virtual Camera driver)
python -c "import pyvirtualcam" >nul 2>&1
if errorlevel 1 (
    echo Installing pyvirtualcam (OBS Virtual Camera driver)...
    echo This will download and install the OBS Virtual Camera driver (~2MB)
    echo.
    pip install pyvirtualcam
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install pyvirtualcam
        echo Please install manually: pip install pyvirtualcam
        pause
        exit /b 1
    )
    echo ✓ pyvirtualcam installed
)

REM Check for Pillow (image processing)
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing Pillow (image processing)...
    pip install Pillow
)

echo.
echo ============================================================
echo  Setup Complete!
echo ============================================================
echo.
echo Your PC is now ready to become a virtual camera + microphone!
echo.
echo Prerequisites:
echo   ✓ OBS Virtual Camera driver (auto-installed above)
echo   ? VB-Cable (for virtual microphone) - optional
echo     Install from: https://vb-audio.com/Cable/
echo.
echo Next Steps:
echo   1. Start the server: python backend/src/run_dev.py
echo   2. Stream from phone: https://<YOUR_PC_IP>:5000
echo   3. Run the bridge (choose option below)
echo.
echo ============================================================
echo  Bridge Options
echo ============================================================
echo.
echo 1. Virtual Camera ONLY (no audio)
echo 2. Virtual Camera + Audio to VB-Cable
echo 3. Virtual Camera + Audio to specific device
echo 4. List available audio devices
echo 5. Run with custom resolution/FPS
echo 6. Exit
echo.

setlocal enabledelayedexpansion
set /p CHOICE="Enter choice (1-6): "

if "%CHOICE%"=="1" (
    echo.
    echo Starting Virtual Camera Bridge...
    echo.
    python backend\src\virtual_devices_windows.py --server wss://192.168.1.82:5000/ws
    goto :done
)

if "%CHOICE%"=="2" (
    echo.
    echo Starting Virtual Camera + Audio Bridge (VB-Cable)...
    echo.
    python backend\src\virtual_devices_windows.py --server wss://192.168.1.82:5000/ws --audio-device "Cable Input (VB-Audio Virtual Cable)"
    goto :done
)

if "%CHOICE%"=="3" (
    echo.
    set /p DEVICE="Enter audio device name: "
    echo Starting bridge with device: !DEVICE!
    echo.
    python backend\src\virtual_devices_windows.py --server wss://192.168.1.82:5000/ws --audio-device "!DEVICE!"
    goto :done
)

if "%CHOICE%"=="4" (
    echo.
    python backend\src\virtual_devices_windows.py --list-audio-devices
    pause
    goto :done
)

if "%CHOICE%"=="5" (
    echo.
    set /p WIDTH="Enter camera width (default 1280): "
    set /p HEIGHT="Enter camera height (default 720): "
    set /p FPS="Enter FPS (default 30): "
    if "!WIDTH!"=="" set WIDTH=1280
    if "!HEIGHT!"=="" set HEIGHT=720
    if "!FPS!"=="" set FPS=30
    echo.
    echo Starting bridge with resolution !WIDTH!x!HEIGHT@ !FPS!fps...
    echo.
    python backend\src\virtual_devices_windows.py --server wss://192.168.1.82:5000/ws --camera-width !WIDTH! --camera-height !HEIGHT! --camera-fps !FPS!
    goto :done
)

if "%CHOICE%"=="6" (
    echo Exiting.
    exit /b 0
)

echo Invalid choice. Exiting.
:done
pause
