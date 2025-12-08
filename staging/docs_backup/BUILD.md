NodeFlow - Packaging & Virtual Device Guide
===========================================

This document explains how to create platform builds (Windows & Linux) and how to expose the project stream as a system webcam and microphone.

Summary
-------
- Windows: create executables with PyInstaller; use OBS Virtual Camera + VB-Audio (VB-Cable) to expose webcam/microphone system-wide.
- Linux: create executables with PyInstaller; use `v4l2loopback` for virtual webcam and `snd-aloop` (ALSA loopback) for virtual microphone. Use `virtual_output_linux.py` to push frames/samples into these loopback devices via `ffmpeg`.

Prerequisites (Windows)
-----------------------
- Python 3.11+ installed and added to PATH
- Recommended: create a virtual environment `python -m venv .venv` and activate it
- Install build tools in the environment:
  - `pip install pyinstaller pyinstaller-hooks-contrib`
- For virtual devices (system-wide webcam/mic):
  - Install OBS Studio: https://obsproject.com/
  - Install OBS Virtual Camera (Windows: built-in in recent OBS versions) — start Virtual Camera from OBS
  - Install VB-Audio Virtual Cable (VB-Cable) for virtual microphone: https://vb-audio.com/Cable/

How to expose NodeFlow as webcam+mic on Windows (recommended approach)
--------------------------------------------------------------------
Option A — OBS (recommended, no drivers to build):
1. Install OBS and VB-Cable.
2. In OBS create a new Scene. Add a "Browser" source that points to `https://<SERVER_IP>:5000/` (accept certificate on phone first or copy page to PC browser and authenticate).
   - Width/Height should match your video stream (e.g., 640x480).
3. Start the Virtual Camera in OBS (Controls -> Start Virtual Camera).
4. In Windows Audio settings, set OBS or a routed Virtual Audio Device as the default input for apps:
   - Use VB-Cable to route audio output from NodeFlow/OBS to a virtual input used by apps.
5. In any application (Zoom, Chrome, etc.) select "OBS Virtual Camera" as webcam and "Cable Output (VB-Audio)" as microphone (depending on routing).

Notes:
- This approach uses OBS as an intermediary; it does not require writing a kernel/driver.
- You can automate OBS with `obs-websocket` if needed (start/stop scene programmatically).

Building Windows executables (PyInstaller)
-----------------------------------------
Run these commands inside an activated virtual environment in the repository root.

# Receiver GUI
pyinstaller --noconfirm --onefile --name NodeFlowReceiverGUI backend\\src\\receiver_gui.py

# Console receiver
pyinstaller --noconfirm --onefile --name NodeFlowReceiverConsole backend\\src\\receiver_console.py

# Server (optional to run as exe)
pyinstaller --noconfirm --onefile --name NodeFlowServer backend\\src\\run_dev.py

After building, executables will appear in the `dist/` folder. Test them on the target machine.

Prerequisites (Linux)
---------------------
- Python 3.11+ and virtualenv
- `ffmpeg` installed (apt/yum)
- `v4l2loopback` kernel module for virtual webcam:
  sudo apt install v4l2loopback-dkms v4l2loopback-utils
  sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="NodeFlow" exclusive_caps=1
  This creates `/dev/video10` (change video_nr as needed).

- ALSA loopback for audio (snd-aloop):
  sudo modprobe snd_aloop
  This creates `hw:Loopback` devices. Configure ALSA/ PulseAudio accordingly.

Virtual output helper (Linux)
-----------------------------
We provide `backend/src/virtual_output_linux.py` which:
- Connects to NodeFlow server WebSocket
- Receives `video` and `audio` frames
- Pipes decoded JPEG frames into `ffmpeg -f mjpeg -i - -f v4l2 /dev/videoX`
- Pipes raw f32le audio into `ffmpeg -f f32le -ar <rate> -ac 1 -i - -f alsa hw:Loopback,0,0`

Usage example (after creating loopback devices):
python backend/src/virtual_output_linux.py --server wss://192.168.1.82:5000 --video-device /dev/video10 --audio-device hw:Loopback,0,0

This will map the incoming phone stream to `/dev/video10` and ALSA loopback card. Then pick `/dev/video10` in apps that accept v4l2 devices and select the loopback ALSA input as microphone.

Files added
-----------
- `build_windows.bat` — Windows build convenience script (PyInstaller commands).
- `build_linux.sh` — Linux build script for PyInstaller.
- `backend/src/virtual_output_linux.py` — helper that pushes stream into v4l2 and ALSA loopback via ffmpeg.
- `BUILD.md` — this documentation (this file).

Limitations & Notes
-------------------
- Creating a true system-level virtual camera driver for Windows in pure Python is not feasible here; using OBS Virtual Camera or a third-party virtual camera driver is the practical route.
- For professional usage, consider creating an installer that bundles OBS + virtual audio cable + your exe and configures routing.
- The `virtual_output_linux.py` helper depends on `ffmpeg` and kernel modules (`v4l2loopback`, `snd_aloop`) being installed and configured.

Next steps
----------
- Test `virtual_output_linux.py` on a Linux machine with `v4l2loopback` installed.
- Build Windows exe with `build_windows.bat` and test with OBS Virtual Camera + VB-Cable.
- If you'd like, I can automate OBS control using `obs-websocket` and create a small installer script to configure virtual devices.
