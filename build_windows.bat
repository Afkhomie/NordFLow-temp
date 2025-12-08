@echo off
REM Build NodeFlow executables on Windows using PyInstaller
REM Run inside an activated virtual environment

echo Building NodeFlow Receiver GUI...
pyinstaller --noconfirm --onefile --name NodeFlowReceiverGUI backend\src\receiver_gui.py

echo Building NodeFlow Console Receiver...
pyinstaller --noconfirm --onefile --name NodeFlowReceiverConsole backend\src\receiver_console.py

echo Building NodeFlow Server (optional)...
pyinstaller --noconfirm --onefile --name NodeFlowServer backend\src\run_dev.py

echo Build complete. Check the dist\\ folder.
pause
