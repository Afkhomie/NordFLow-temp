NodeFlow - Windows Quick Start Guide
======================================

You now have fully built Windows executables and helper scripts to use NodeFlow as a system webcam and microphone.

What You Have
=============

1. **NodeFlowReceiverGUI.exe** — Professional GUI receiver with video display and real-time stats
2. **NodeFlowReceiverConsole.exe** — Lightweight console receiver (headless-compatible)
3. **launch_windows.bat** — One-click launcher with all options
4. **obs_automation.py** — Automate OBS Virtual Camera setup
5. **audio_routing_windows.py** — Route audio to VB-Cable

Quick Start (3 Steps)
=====================

Step 1: Start the server on the PC that will receive streams
    - Run the backend server (or keep it running from earlier testing)
    - Command: `python backend/src/run_dev.py`
    - Or use the provided `start.bat`

Step 2: Stream from your phone
    - Open https://<YOUR_PC_IP>:5000 on phone (e.g., https://192.168.1.82:5000)
    - Accept SSL certificate warning
    - Click "Start" for camera and microphone

Step 3: Receive on PC
    Option A — GUI Receiver (Recommended):
        `dist\NodeFlowReceiverGUI.exe`
        - Shows live video in a window
        - Displays real-time stats (FPS, audio level, etc.)
        - Just click "Connect" button

    Option B — Console Receiver:
        `dist\NodeFlowReceiverConsole.exe`
        - Lightweight, no GUI
        - Shows stats in console
        - Good for debugging

Using NodeFlow as System Webcam + Microphone
==============================================

You have two methods:

METHOD 1: OBS Virtual Camera + VB-Cable (Recommended & Easiest)
================================================================

Prerequisites:
    1. Install OBS Studio: https://obsproject.com/
    2. Install OBS Virtual Camera (built-in on OBS 28+)
    3. Install VB-Audio Virtual Cable: https://vb-audio.com/Cable/ (for virtual microphone)
    4. Install OBS WebSocket plugin: https://github.com/obsproject/obs-websocket
       - In OBS: Tools -> WebSocket Server Settings -> Enable Server

Steps:
    1. Run the launcher:
       `launch_windows.bat`
       Choose option 3 (OBS automation)

    2. Or manually:
       - Open OBS Studio
       - Add a new "Browser" source pointing to https://<YOUR_PC_IP>:5000
       - In OBS: Controls -> Start Virtual Camera
       - In any app (Zoom, Teams, Chrome, etc.):
         * Select "OBS Virtual Camera" as webcam
         * Select "Cable Input (VB-Audio Virtual Cable)" as microphone (if routed)

    3. For audio routing:
       - In Windows Sound Settings: set default microphone to "Cable Output (VB-Audio Virtual Cable)"
       - In the app: select that device as microphone

METHOD 2: Direct Audio Routing (Windows Audio Device)
=======================================================

If you only want to route audio (not use OBS for video):

1. Install VB-Cable: https://vb-audio.com/Cable/
2. Run the audio router:
   `dist\AudioRouterWindows.exe`
   or
   `python backend/src/audio_routing_windows.py --output-device "Cable Input"`

3. In any app:
   - Select microphone: "Cable Input (VB-Audio Virtual Cable)"

To list available devices:
   `python backend/src/audio_routing_windows.py --list-devices`

Testing (No Extra Software)
=============================

Without OBS or VB-Cable, you can still test locally:

1. Run the server on one PC:
   `python backend/src/run_dev.py`

2. Stream from phone:
   Open https://<PC_IP>:5000 in phone browser

3. Receive on another PC (or same PC):
   `dist\NodeFlowReceiverGUI.exe`
   (local reception works perfectly)

Troubleshooting
================

Q: Can I use NodeFlow in Zoom, Teams, OBS, etc. WITHOUT OBS Virtual Camera?
A: Not directly without virtual camera drivers. OBS Virtual Camera is the easiest method.
   Alternative: Use OBS as an intermediary (add NodeFlow as Browser source in OBS, then use OBS Virtual Camera).

Q: Audio doesn't work in my app?
A: Make sure you've selected the correct audio input device in your app settings.
   - In Windows, go to Sound Settings and set default microphone
   - In the app, check audio/microphone input settings

Q: "OBS Virtual Camera not found" error?
A: Ensure:
   1. OBS Studio is installed and running
   2. You have the latest version (OBS 28+)
   3. Virtual Camera is enabled: Controls -> Start Virtual Camera
   4. Check Windows Display Settings -> Camera (allow access)

Q: Video is laggy or audio is distorted?
A: Try:
   1. Reduce video resolution on phone (640x480 is default)
   2. Reduce frame rate (Settings in mobile UI if available)
   3. Close other apps consuming bandwidth
   4. Ensure phone and PC are on same WiFi network (not cellular)

Q: Can I use NodeFlow outside my home network?
A: Yes, but requires port forwarding or VPN. See SETUP_GUIDE.md for secure setup.

Performance Tips
=================

- Use 640x480 @ 12 FPS for best mobile performance
- Close other streaming apps to reduce bandwidth
- Use 5 GHz WiFi if available (faster than 2.4 GHz)
- Audio works best with 16000 Hz sample rate

Next Steps
===========

1. Test with OBS + Virtual Camera: follow METHOD 1 above
2. Check BUILD.md for building on Linux or creating custom builds
3. Customize: modify `backend/src/templates/index.html` for UI changes
4. Deploy: share `dist/NodeFlow*.exe` files to other PCs

Questions or Issues?
====================

- Check the troubleshooting section above
- Review SETUP_GUIDE.md for setup help
- Check SUMMARY.txt for technical details
