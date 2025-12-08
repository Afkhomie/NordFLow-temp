"""
NodeFlow launcher

Starts the backend server process and then launches the desktop receiver GUI.
Behavior:
 - If a bundled server executable `NodeFlowServer.exe` exists in the same folder, it will be launched.
 - Otherwise it will launch the server Python script using the same Python interpreter.
 - It will then run the GUI (prefer bundled `NodeFlowGUI.exe` if present, else run `backend/src/receiver_gui.py`).
 - On GUI exit, the launcher will terminate the server subprocess.

This simple launcher makes packaging easier: you can create two one-file executables (server + launcher)
and ship them together in the installer.
"""
import os
import sys
import subprocess
import time
import signal

ROOT = os.path.dirname(os.path.abspath(__file__))

def find_executable(name):
    path = os.path.join(ROOT, name)
    if os.path.exists(path):
        return path
    return None


def run_server():
    # Prefer bundled server exe
    exe = find_executable('NodeFlowServer.exe')
    if exe:
        proc = subprocess.Popen([exe], cwd=ROOT)
        return proc

    # Fallback to running the server Python script
    server_py = os.path.join(ROOT, 'backend', 'src', 'server.py')
    if os.path.exists(server_py):
        proc = subprocess.Popen([sys.executable, server_py], cwd=ROOT)
        return proc

    print('No server executable or script found. Please ensure backend/src/server.py exists or build NodeFlowServer.exe')
    return None


def run_gui():
    # Prefer bundled GUI
    exe = find_executable('NodeFlowGUI.exe')
    if exe:
        proc = subprocess.Popen([exe], cwd=ROOT)
        return proc

    # Fallback to running GUI python script
    gui_py = os.path.join(ROOT, 'backend', 'src', 'receiver_gui.py')
    if os.path.exists(gui_py):
        # Run in foreground so launcher waits for GUI exit
        return subprocess.call([sys.executable, gui_py], cwd=ROOT)

    print('No GUI executable or script found. Please ensure backend/src/receiver_gui.py exists or build NodeFlowGUI.exe')
    return None


def terminate(proc):
    try:
        if proc and proc.poll() is None:
            proc.terminate()
            # give it a moment
            time.sleep(1)
            if proc.poll() is None:
                proc.kill()
    except Exception:
        pass


def main():
    print('Launcher starting server...')
    server_proc = run_server()
    if server_proc is None:
        print('Server not started. Exiting launcher.')
        return 1

    print('Server started (pid=%s).' % (server_proc.pid if hasattr(server_proc, 'pid') else 'unknown'))
    print('Starting GUI...')

    try:
        # If run_gui returns an int (exit code), propagate it
        ret = run_gui()
        if isinstance(ret, int):
            exit_code = ret
        else:
            exit_code = 0
    except KeyboardInterrupt:
        exit_code = 0
    except Exception as e:
        print('GUI crashed or failed to start:', e)
        exit_code = 1

    print('GUI exited. Shutting down server...')
    terminate(server_proc)
    print('Done.')
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
