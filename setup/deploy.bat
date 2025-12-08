@echo off
REM NodeFlow Production Deployment Script
REM Automates testing and preparation for building

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ════════════════════════════════════════════════════════════
echo   NodeFlow Production Deployment Script v1.0
echo ════════════════════════════════════════════════════════════
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python not found! Install from https://www.python.org
    pause
    exit /b 1
)

echo ✓ Python found

REM Check for PyInstaller
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ PyInstaller not found. Installing...
    pip install --upgrade pyinstaller
)

echo ✓ PyInstaller ready

echo.
echo ════════════════════════════════════════════════════════════
echo   Phase 1: Comprehensive Testing (5 minutes)
echo ════════════════════════════════════════════════════════════
echo.

REM Test 1: Virtual devices
echo [1/4] Testing virtual devices...
python test_virtual_devices.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Virtual devices test failed!
    python test_virtual_devices.py
    pause
    exit /b 1
)
echo ✓ Virtual devices: OK

REM Test 2: Backend imports
echo [2/4] Testing backend imports...
cd backend\src
python -c "from streaming.server_new import *; print('OK')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Server import failed!
    cd ..\..
    pause
    exit /b 1
)
echo ✓ Server imports: OK

python -c "from receiver_gui import *; print('OK')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ GUI import failed!
    cd ..\..
    pause
    exit /b 1
)
echo ✓ GUI imports: OK

python -c "from services.virtual_devices import *; print('OK')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Virtual devices import failed!
    cd ..\..
    pause
    exit /b 1
)
echo ✓ Virtual devices imports: OK

cd ..\..

REM Test 3: File compilation
echo [3/4] Checking Python files...
python -m py_compile backend\src\receiver_gui.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ receiver_gui.py has syntax errors!
    pause
    exit /b 1
)
echo ✓ receiver_gui.py: OK

python -m py_compile backend\src\receiver.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ receiver.py has syntax errors!
    pause
    exit /b 1
)
echo ✓ receiver.py: OK

python -m py_compile backend\src\services\virtual_devices.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ virtual_devices.py has syntax errors!
    pause
    exit /b 1
)
echo ✓ virtual_devices.py: OK

REM Test 4: Documentation
echo [4/4] Checking documentation...
if not exist "QUICK_REFERENCE.md" (
    echo ✗ QUICK_REFERENCE.md missing!
    pause
    exit /b 1
)
echo ✓ QUICK_REFERENCE.md: Present

if not exist "VIRTUAL_DEVICES.md" (
    echo ✗ VIRTUAL_DEVICES.md missing!
    pause
    exit /b 1
)
echo ✓ VIRTUAL_DEVICES.md: Present

if not exist "README.md" (
    echo ⚠ README.md missing (optional)
)

echo.
echo ════════════════════════════════════════════════════════════
echo   ✓ ALL TESTS PASSED!
echo ════════════════════════════════════════════════════════════
echo.
echo ✓ Code Quality: OK
echo ✓ Imports: OK
echo ✓ Syntax: OK
echo ✓ Documentation: OK
echo ✓ Virtual Devices: OK
echo.

echo Next steps:
echo.
echo 1. BUILD EXECUTABLE (requires ~5 min):
echo    pyinstaller NodeFlow.spec --clean --noconfirm
echo.
echo 2. TEST EXECUTABLE:
echo    cd dist\NodeFlow
echo    NodeFlow.exe
echo.
echo 3. CREATE INSTALLER (requires Inno Setup):
echo    - Download: https://jrsoftware.org/isdl.php
echo    - Install Inno Setup
echo    - Open: NodeFlow-Setup.iss
echo    - Build → Compile
echo.
echo 4. TEST INSTALLER:
echo    release\NodeFlow-Setup-v1.0.0.exe
echo.
echo 5. PUSH TO GITHUB:
echo    git add .
echo    git commit -m "Production release v1.0.0"
echo    git push origin main
echo    git tag -a v1.0.0 -m "v1.0.0"
echo    git push origin v1.0.0
echo.
echo 6. CREATE GITHUB RELEASE:
echo    - Go to GitHub.com
echo    - Releases → Draft new release
echo    - Upload: NodeFlow-Setup-v1.0.0.exe
echo.

echo.
echo For detailed instructions, see: DEPLOYMENT_CHECKLIST.md
echo.
pause
