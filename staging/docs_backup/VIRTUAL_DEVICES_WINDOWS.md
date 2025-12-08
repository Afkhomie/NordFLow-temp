NodeFlow - Virtual Camera + Microphone (Windows)
===============================================

**Your PC is now a wireless webcam and microphone!**

Use your phone's camera and microphone as input in ANY application:
- Discord, Zoom, Teams, Skype, etc.
- OBS Studio, Streamlabs, etc.
- Chrome, Firefox, Edge, any browser
- Any app that accepts a webcam input

No OBS Studio needed. Just lightweight drivers.

Quick Start (3 Steps)
====================

**Step 1: Install Drivers (one-time)**

Run the setup script:
```
virtual_devices_setup.bat
```

This installs:
- ✓ **OBS Virtual Camera driver** (~2 MB) - automatically installed by pyvirtualcam
- ? **VB-Cable** (optional, for audio) - https://vb-audio.com/Cable/

**Step 2: Start the Bridge**

Option A - Video Only (fastest):
```
python backend/src/virtual_devices_windows.py --server wss://192.168.1.82:5000/ws
```

Option B - Video + Audio to VB-Cable:
```
python backend/src/virtual_devices_windows.py --server wss://192.168.1.82:5000/ws ^
  --audio-device "Cable Input (VB-Audio Virtual Cable)"
```

Or use the setup script and choose option 2.

**Step 3: Stream from Your Phone**

1. Phone browser: Open https://<YOUR_PC_IP>:5000
2. Accept SSL certificate warning
3. Click "Start" for camera and microphone
4. In your app: Select "OBS Virtual Camera" as webcam

Done! Your phone is now your webcam.

What You Get
============

**Virtual Camera:** "OBS Virtual Camera"
- Resolution: Configurable (default 1280x720)
- FPS: Configurable (default 30)
- Format: RGB (H.264/MJPEG compatible)
- Visible in: Windows camera settings, all apps

**Virtual Microphone:** "Cable Input (VB-Audio Virtual Cable)" (if VB-Cable installed)
- Format: PCM 16/24-bit, any sample rate
- Latency: ~100ms (with buffering)
- Visible in: Windows audio settings, all apps

How It Works (Under the Hood)
=============================

**Video Pipeline:**
1. Phone captures video (1280x720 @ 12 FPS)
2. Encodes as JPEG (base64 over WebSocket)
3. Server broadcasts to PC
4. Virtual devices bridge receives frame
5. Decodes JPEG → RGB
6. Feeds RGB to "OBS Virtual Camera" driver
7. Windows apps see input from "OBS Virtual Camera"

**Audio Pipeline:**
1. Phone captures audio (PCM float32 @ native sample rate)
2. Encodes as JSON array (over WebSocket)
3. Server broadcasts to PC
4. Audio bridge receives frame
5. Buffers samples (circular 10-sec buffer)
6. Feeds to VB-Cable "Cable Input" device
7. Windows apps see input from "Cable Input"

Configuration
==============

**Change Camera Resolution:**
```
python backend/src/virtual_devices_windows.py --server wss://192.168.1.82:5000/ws \
  --camera-width 640 --camera-height 480 --camera-fps 15
```

**Change Server Address:**
```
python backend/src/virtual_devices_windows.py --server wss://YOUR_PC_IP:5000/ws
```

**Find Your Audio Device:**
```
python backend/src/virtual_devices_windows.py --list-audio-devices
```

Common device names:
- `"Cable Input (VB-Audio Virtual Cable)"` (VB-Cable)
- `"Stereo Mix"` (if enabled on your PC)
- `"Line In"` (if you have a physical input)

**Boost Audio Level:**
Currently uses raw phone mic input. If too quiet:
1. Increase phone mic volume
2. Or modify `virtual_devices_windows.py` to add gain (multiply by 2.0-5.0)

Troubleshooting
================

**"pyvirtualcam not found"**
- Run: `pip install pyvirtualcam`
- This auto-downloads OBS Virtual Camera driver
- If fails, install manually from: https://github.com/obsproject/obs-studio/releases

**"OBS Virtual Camera not visible in Discord/Teams/Zoom"**
1. Restart the app (after starting the bridge)
2. Check Windows Settings → Camera → "Allow camera" is ON
3. In Windows Settings → Privacy & Security → Camera: check app permissions
4. Disable hardware acceleration in the app (sometimes helps)

**"Audio not working"**
1. Did you install VB-Cable? (https://vb-audio.com/Cable/)
2. Is the bridge running with `--audio-device`?
3. Restart the app to refresh audio device list
4. Check Windows Sound Settings → Recording → "Cable Output" is set as default (optional)

**"Video is laggy"**
1. Reduce resolution: `--camera-width 640 --camera-height 480 --camera-fps 15`
2. Check WiFi signal strength (need 5+ Mbps)
3. Close other apps using bandwidth
4. Check phone CPU usage during streaming

**"Audio is distorted or robotic"**
1. Check phone microphone quality (use phone's built-in Voice Recorder test first)
2. Increase phone mic gain if too quiet
3. Restart both phone and PC bridge
4. Check if VB-Cable is working: Windows Sound Settings → Recording → "Cable Output" should show input

**"Driver won't install"**
- OBS Virtual Camera is bundled with OBS Studio
- Alternative: Install full OBS from https://obsproject.com/
- Or try: https://github.com/obsproject/obs-studio/releases → download latest
- Then: `pip install pyvirtualcam` will detect the existing driver

Using with Specific Apps
========================

**Discord:**
1. Settings → Voice & Video
2. Microphone: "Cable Input (VB-Audio Virtual Cable)"
3. Camera: "OBS Virtual Camera"

**Zoom:**
1. Settings → Audio
2. Microphone: "Cable Input (VB-Audio Virtual Cable)"
3. Video Settings
4. Camera: "OBS Virtual Camera"

**OBS Studio:**
1. Add new Video Capture Device source
2. Select "OBS Virtual Camera"
3. Add new Audio Input source
4. Select "Cable Output (VB-Audio Virtual Cable)"
5. Done! Can now re-stream this

**Chrome/Edge (Video Call):**
1. Join call
2. Browser will prompt for camera/mic
3. Allow both
4. Camera: "OBS Virtual Camera"
5. Microphone: "Cable Input (VB-Audio Virtual Cable)"

Advanced Tips
=============

**Multiple Receivers:**
Run multiple instances with different resolutions:
```
# Terminal 1: 1080p for OBS streaming
python backend/src/virtual_devices_windows.py --server wss://192.168.1.82:5000/ws \
  --camera-width 1920 --camera-height 1080 --camera-fps 30

# Terminal 2: 480p for Discord on low bandwidth
python backend/src/virtual_devices_windows.py --server wss://192.168.1.82:5000/ws \
  --camera-width 640 --camera-height 480 --camera-fps 15
```
(Only one can control OBS Virtual Camera at a time, but audio can go to different devices)

**Audio Routing with VirtualAudio:**
For advanced users, can create complex audio routing using VirtualAudio or Voicemeeter Banana.

**Record Streams:**
Use OBS to capture "OBS Virtual Camera" + "Cable Output" and save to file locally.

**Low Latency Setup:**
- Phone: Reduce capture resolution to 640x480
- Bridge: Run with `--camera-fps 15`
- Network: Use 5 GHz WiFi if available
- Latency should be 150-300ms typical

Performance Metrics
====================

On typical Windows 10/11 PC (mid-range i5/Ryzen 5):
- CPU: 5-15% (mostly JPEG decoding)
- Memory: 100-300 MB
- Bandwidth: 2-8 Mbps (depending on resolution/FPS)
- Latency: 100-300ms (phone → PC)
- FPS: 12-30 (depending on bandwidth)

Architecture
============

```
Phone (Camera/Mic) 
    ↓ (JPEG + PCM over HTTPS/WebSocket)
Server (Relay)
    ↓ (Broadcast to all receivers)
Virtual Device Bridge (PC)
    ├→ OBS Virtual Camera Driver (Windows Kernel)
    │   ↓
    └→ VB-Audio Virtual Cable (Windows Kernel)
        ↓
    Apps (Discord, Zoom, OBS, etc.)
```

Limitations
===========

- **Windows only** (Linux use virtual_output_linux.py with v4l2loopback)
- **One primary camera feed** (but multiple instances can listen)
- **No H.264 encoding** (JPEG frames only, converted to RGB)
- **Requires driver installation** (unavoidable for virtual devices on Windows)
- **Audio sample rate must match device** (auto-converts if mismatch)

FAQ
===

**Q: Why do I need drivers?**
A: Windows needs kernel-level drivers to create virtual hardware devices. Same reason you need GPU drivers. This is unavoidable for any virtual camera/mic solution on Windows.

**Q: Can I use this instead of OBS Virtual Camera?**
A: No, we USE the OBS Virtual Camera driver (just the driver, not the app). It's the best/most compatible option available.

**Q: Is this safe? Can viruses get in?**
A: Drivers are signed by OBS (Microsoft-verified). Same as any official driver. We don't run any unsigned code.

**Q: Why pyvirtualcam and not DirectShow filters?**
A: pyvirtualcam is simpler to use and requires no C++ compilation. DirectShow is more complex but equivalent functionality.

**Q: Can I use multiple phones at once?**
A: Server accepts only 1 phone stream. But multiple PCs can receive. Could extend server to handle multiple phones (future feature).

**Q: Will this work on Mac?**
A: Mac uses different virtual device system (CMIOext). Would need separate implementation using ScreenFlow or similar. Not currently supported.

Next Steps
===========

1. Run `virtual_devices_setup.bat` to install drivers
2. Start the bridge: `python backend/src/virtual_devices_windows.py --server wss://192.168.1.82:5000/ws --audio-device "Cable Input (VB-Audio Virtual Cable)"`
3. Open app (Discord, Zoom, etc.) and select devices
4. Stream from phone: https://<YOUR_PC_IP>:5000
5. Share screen/camera with audio! 🎉

Support
========

Issues? Check:
1. Is server running? `python backend/src/run_dev.py`
2. Is phone connected? Check server logs for "Received hello message from 192.168.1.X"
3. Are drivers installed? Run `virtual_devices_setup.bat` again
4. Is WiFi connection stable? Test with `ping <phone_ip>`
5. Check this guide's Troubleshooting section
