NodeFlow Installer - Quick Guide

This folder contains a template Inno Setup script and assets for building a Windows `setup.exe`.

Steps to create the installer:

1. Generate icon assets (if you have a PNG or SVG):

   - From project root run:

     ```powershell
     python tools\make_icons.py --src path\to\your_icon.png --out installers\assets --name nodeflow
     ```

   - This creates `installers/assets/nodeflow.ico` and sized PNGs.

2. Install Inno Setup on Windows:
   - Download from https://jrsoftware.org/
   - Run the Inno Setup Compiler (ISCC.exe) or use the GUI.

3. Build installer:

   - Open `installers/NodeFlowInstaller.iss` in Inno Setup and adjust `AppExe` to point to the actual launcher executable you want to ship (we recommend bundling a small launcher that starts the backend server and GUI).
   - Compile to produce `NodeFlow-Setup.exe`.

Notes & suggestions:
- The installer template copies everything in `backend/src/` and `frontend/` into the installation directory. You should create a small launcher exe or batch file (for example `NodeFlow.exe`) that starts the server and GUI. Consider using PyInstaller to bundle Python code into a standalone exe.
- Replace the placeholder icon `installers/assets/nodeflow.ico` with your real icon before building.
- Keep the distribution minimal: include only the runtime/executables, the three documentation files (`README.md`, `QUICKSTART.md`, `LICENSE`) and the `assets` folder.

If you want, I can:
- Add a small `launcher.py` and a `pyinstaller` spec so we can create a single `NodeFlow.exe`.
- Patch the Inno script to add Start Menu/desktop shortcuts and to register services to auto-start the server if desired.

