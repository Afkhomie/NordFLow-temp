@echo off
echo ========================================
echo Building NodeFlow v1.0.0
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if NodeFlow.spec exists
if not exist "NodeFlow.spec" (
    echo Error: NodeFlow.spec not found in root directory!
    echo Please make sure NodeFlow.spec is in the same folder as build.bat
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist\" rmdir /s /q dist
if exist "build\" rmdir /s /q build

REM Generate SSL certificates if they don't exist
echo Checking SSL certificates...
cd backend\src
if not exist "server.crt" (
    echo Generating SSL certificates...
    python generate_cert.py
) else (
    echo SSL certificates already exist.
)
cd ..\..

REM Build the executable
echo.
echo Building executable...
echo This may take 2-5 minutes...
echo.
pyinstaller NodeFlow.spec --clean

REM Check if build was successful
if not exist "dist\NodeFlow.exe" (
    echo.
    echo ========================================
    echo Build FAILED!
    echo ========================================
    echo Check the error messages above.
    pause
    exit /b 1
)

REM Create release directory
echo.
echo Creating release packages...
if not exist "release\" mkdir release

REM Create NodeFlow.zip (just the executable)
echo Creating NodeFlow-v1.0.0.zip...
cd dist
powershell -Command "Compress-Archive -Path NodeFlow.exe -DestinationPath ..\release\NodeFlow-v1.0.0.zip -Force"
cd ..

REM Create source code zip (excluding venv, dist, build, etc.)
echo Creating source code zip...
powershell -Command "$exclude = @('venv', 'dist', 'build', '__pycache__', '*.pyc', '.git', 'release', '*.zip'); Get-ChildItem -Exclude $exclude | Compress-Archive -DestinationPath release\NodeFlow-Source-v1.0.0.zip -Force"

echo.
echo ========================================
echo Build SUCCESSFUL!
echo ========================================
echo.
echo Output files:
echo - dist\NodeFlow.exe (Standalone executable)
echo - release\NodeFlow-v1.0.0.zip (Executable package)
echo - release\NodeFlow-Source-v1.0.0.zip (Source code)
echo.
echo You can now:
echo 1. Test: dist\NodeFlow.exe
echo 2. Distribute: release\NodeFlow-v1.0.0.zip
echo.
pause