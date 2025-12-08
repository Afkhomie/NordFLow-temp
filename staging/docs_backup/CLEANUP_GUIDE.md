NODEFLOW - VIRTUAL ENVIRONMENT CLEANUP GUIDE
==============================================

QUICK START
-----------
Run: cleanup.bat
This script will safely remove unused virtual environments and cache files.

WHAT GETS DELETED
-----------------
Virtual Environments (Optional):
  • .\.venv                 (~300-500 MB) - Python packages and interpreter copy
  • .\venv                  (~300-500 MB) - Alternative venv location
  • .\env                   (~300-500 MB) - Alternative venv location

Python Cache (Always Removed):
  • __pycache__/            (~50-100 MB)  - Python bytecode cache
  • *.pyc files             (~20-50 MB)   - Compiled Python files
  • ~/.pip/cache/           (~100-200 MB) - Pip package cache

WHAT DOES NOT GET DELETED
--------------------------
✓ Source code (backend/, frontend/)
✓ Configuration files (*.json, *.txt, *.md)
✓ Project documentation
✓ build/, release/ directories
✓ Unit tests

SPACE FREED
-----------
Total space recovered: 500 MB to 1.2 GB

Breakdown (typical):
  • Virtual environment: 500-700 MB
  • Python cache: 50-100 MB
  • Pip cache: 100-200 MB
  ─────────────────────────
  Total: 650-1,000 MB

VIRTUAL ENVIRONMENT DETAILS
----------------------------

Current Setup (.\.venv - KEEP if developing):
  • Python 3.11
  • ~80 packages installed (aiohttp, PyQt6, numpy, etc.)
  • Size: ~500 MB
  • Location: c:\Users\Prakash\OneDrive\Desktop\NodeFlow\.venv
  • Status: Active development environment

When to DELETE:
  • Need to free up disk space
  • Switching to different Python version
  • Starting fresh development environment
  • Archiving completed project

When to KEEP:
  • Active development planned
  • Quick testing needed
  • Temporary space issues will be resolved

HOW TO REINSTALL
-----------------
If you delete .venv, reinstall with:

1. Open PowerShell in NodeFlow directory
2. Create new environment:
   python -m venv .venv

3. Activate:
   .\.venv\Scripts\Activate.ps1

4. Install dependencies:
   pip install -r backend/requirements.txt

5. Verify installation:
   pip list

Expected packages (key ones):
  • aiohttp 3.13.2
  • PyQt6 6.10.0
  • websocket-client 1.9.0
  • sounddevice 0.5.3
  • numpy 2.3.5
  • opencv-python 4.11.0.86

Time to reinstall: ~5-10 minutes (depending on internet speed)

CLEANUP OPTIONS
----------------

Option 1: Clean Virtual Environments Only (Recommended)
  rmdir .\.venv /s /q
  rmdir .\venv /s /q
  rmdir .\env /s /q

Option 2: Clean Python Cache Only (Safe - Can always do this)
  for /r . %D in (__pycache__) do rmdir "%D" /s /q
  del /s /q *.pyc
  python -m pip cache purge

Option 3: Complete Cleanup (Frees most space)
  [Run cleanup.bat with all options]

Option 4: Selective Cleanup Script
  [See custom_cleanup.ps1 below for PowerShell version]

AUTOMATED CLEANUP SCRIPT (cleanup.bat)
---------------------------------------
The cleanup.bat script:

1. Detects existing virtual environments
2. Shows user what will be deleted
3. Asks for confirmation (Y/N)
4. Removes selected items
5. Cleans Python cache
6. Purges pip cache
7. Reports total space freed

Usage:
  Double-click: cleanup.bat
  OR from command line: cleanup.bat

The script is safe and won't delete project files.

MANUAL CLEANUP (PowerShell)
-----------------------------
For more control, use PowerShell commands:

# Deactivate environment first (if active)
deactivate

# Remove specific environment
Remove-Item -Path ".\.venv" -Recurse -Force

# Clean all __pycache__ folders
Get-ChildItem -Path . -Directory -Filter __pycache__ -Recurse | 
  ForEach-Object { Remove-Item $_.FullName -Recurse -Force }

# Clean all .pyc files
Get-ChildItem -Path . -Filter "*.pyc" -Recurse | 
  Remove-Item -Force

# Purge pip cache
python -m pip cache purge

TROUBLESHOOTING
----------------

Issue: "Cannot delete .venv - File is in use"
Solution:
  1. Run: deactivate
  2. Close all Python windows/terminals
  3. Try cleanup again
  4. If still locked: Restart Windows and try again

Issue: Cleanup.bat closed immediately
Solution:
  1. Open Command Prompt
  2. Navigate to NodeFlow folder
  3. Run: cleanup.bat
  4. Now you can see any error messages

Issue: Pip cache cleanup failed
Solution:
  This is non-critical. Pip cache can be manually deleted:
  C:\Users\[YourUsername]\AppData\Local\pip\Cache

Issue: "Access Denied" errors
Solution:
  Run Command Prompt as Administrator:
  1. Press Win+X
  2. Select "Command Prompt (Admin)"
  3. Navigate to NodeFlow folder
  4. Run: cleanup.bat

STORAGE ANALYSIS
-----------------
Check current disk usage:

Option 1: Using cleanup.bat
  [Script shows estimated space before cleanup]

Option 2: Using PowerShell
  # Size of .venv folder
  (Get-ChildItem -Path ".\.venv" -Recurse | 
    Measure-Object -Property Length -Sum).Sum / 1MB

  # Total NodeFlow folder
  (Get-ChildItem -Path "." -Recurse | 
    Measure-Object -Property Length -Sum).Sum / 1MB

Option 3: Using Explorer
  Right-click NodeFlow folder > Properties
  Shows total size used

RECOMMENDATIONS
----------------
✓ DO: Clean cache files (__pycache__, pip cache) regularly
✓ DO: Delete virtual environment when not using for a while
✓ DO: Keep source code and documentation
✓ DO: Backup requirements.txt before deleting .venv
✓ DO: Use cleanup.bat for guided cleanup

✗ DON'T: Delete source files (backend/, frontend/)
✗ DON'T: Delete configuration files (*.json, *.txt, *.md)
✗ DON'T: Delete build/ or release/ folders
✗ DON'T: Delete test files

RECOVERY
---------
If you accidentally delete something important:

1. Virtual environment deleted: Reinstall with steps above
2. Python cache deleted: Automatically regenerated on first run
3. Source code deleted: Use Git to restore (if available)

For complete recovery, keep a backup of NodeFlow folder:
  Copy entire folder to external drive or cloud storage

VERSION INFORMATION
--------------------
This cleanup guide applies to:
  • NodeFlow Project
  • Python 3.11+
  • Windows 10/11
  • Development Setup

Created: [Current Date]
Last Updated: December 2024

SUPPORT
-------
For issues or questions about cleanup:
  1. Check TROUBLESHOOTING section above
  2. Review SUMMARY.txt for project overview
  3. Check README_SETUP.md for installation help

Questions about specific files:
  • Backend: backend/src/ → Python source code (KEEP)
  • Frontend: frontend/src/ → React components (KEEP)
  • Tests: backend/tests/ → Unit tests (KEEP)
  • Cache: __pycache__/ → Python cache (SAFE TO DELETE)
  • Venv: .venv/ → Virtual environment (OK TO DELETE)
