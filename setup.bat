@echo off
echo Setting up NodeFlow...

REM Check if Python 3.11 is available
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3.11 not found!
    exit /b 1
)

REM Create virtual environment
py -3.11 -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements-windows.txt

echo Setup complete! Run 'venv\Scripts\activate' to activate the environment.
pause
