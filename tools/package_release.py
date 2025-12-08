"""
package_release.py

Utility to automate asset generation and packaging steps locally.
This script does NOT actually run Inno Setup (that's a GUI/install), but it:
 - generates icon assets (uses tools/make_icons.py)
 - runs the PyInstaller batch build (build/pyinstaller_build.bat)
 - prepares installer folder by copying the built exes into installers\staging (so you can open the .iss in Inno Setup)

Run locally on Windows from the repo root:
    python tools\package_release.py

Requirements:
 - Python with Pillow (and cairosvg if source icon is SVG)
 - PyInstaller installed
 - Inno Setup installed (for final bundling)

"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_SRC = os.path.join(ROOT, 'icon.png')
ASSETS_OUT = os.path.join(ROOT, 'installers', 'assets')
STAGING = os.path.join(ROOT, 'installers', 'staging')
ISS_FILE = os.path.join(ROOT, 'installers', 'NodeFlowInstaller.iss')


def run(cmd, cwd=None):
    print('> ', ' '.join(cmd))
    r = subprocess.run(cmd, cwd=cwd or ROOT)
    if r.returncode != 0:
        raise SystemExit(f'Command failed: {cmd}')


def make_icons():
    if not os.path.exists(ICON_SRC):
        print('icon.png not found at', ICON_SRC)
        return
    ico_path = os.path.join(ASSETS_OUT, 'nodeflow.ico')
    if os.path.exists(ico_path):
        print('Icon already generated at', ico_path)
        return
    print('Generating icon assets...')
    run([sys.executable, os.path.join('tools','make_icons.py'), '--src', ICON_SRC, '--out', ASSETS_OUT, '--name', 'nodeflow'])


def build_exes():
    print('Building single EXE with PyInstaller...')
    # Ensure icon exists
    ico_path = os.path.join(ASSETS_OUT, 'nodeflow.ico')
    if not os.path.exists(ico_path):
        print('ICO not found at', ico_path)
        raise SystemExit('Run make_icons first')
    # If dist\NodeFlow.exe already exists, skip rebuild (resumable)
    dist_exe = os.path.join(ROOT, 'dist', 'NodeFlow.exe')
    if os.path.exists(dist_exe):
        print('Found existing build at', dist_exe, '- skipping PyInstaller step')
        return

    # Use PyInstaller to build a single-file exe from bundle.py
    pyinstaller_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm', '--onefile',
        '--name', 'NodeFlow',
        '--add-data', f"backend{os.sep}src{os.sep}templates{os.pathsep}backend{os.sep}src{os.sep}templates",
        '--icon', ico_path,
        'bundle.py'
    ]
    run(pyinstaller_cmd, cwd=ROOT)


def prepare_staging():
    print('Preparing installer staging folder...')
    if os.path.exists(STAGING):
        shutil.rmtree(STAGING)
    os.makedirs(STAGING, exist_ok=True)
    dist = os.path.join(ROOT, 'dist')
    if os.path.exists(dist):
        for f in os.listdir(dist):
            if f.lower().endswith('.exe'):
                shutil.copy(os.path.join(dist,f), STAGING)
    # copy assets
    if os.path.exists(ASSETS_OUT):
        dest_assets = os.path.join(STAGING, 'assets')
        shutil.copytree(ASSETS_OUT, dest_assets)

    print('Staging ready at', STAGING)


def main():
    make_icons()
    build_exes()
    prepare_staging()
    print('\nPackaging steps completed.\n')
    print('Staging folder prepared at installers\\staging')
    # Attempt to locate Inno Setup's ISCC.exe and run it if available
    iscc_candidates = [
        shutil.which('ISCC'),
        shutil.which('ISCC.exe'),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    iscc = next((p for p in iscc_candidates if p and os.path.exists(p)), None)
    if iscc:
        print('Found Inno Setup compiler at', iscc)
        if not os.path.exists(ISS_FILE):
            print('ISS file not found at', ISS_FILE)
            return
        print('Running ISCC to build installer...')
        run([iscc, ISS_FILE], cwd=ROOT)
        print('If successful, setup.exe will be created in the current folder (per .iss script settings)')
    else:
        print('ISCC.exe not found on PATH or default locations. Open installers\\NodeFlowInstaller.iss in Inno Setup and compile manually.')

if __name__ == '__main__':
    main()
