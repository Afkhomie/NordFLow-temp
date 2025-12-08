NodeFlow - Windows Quick Start Guide (Virtual Devices)
=======================================================

**Your phone is now a wireless webcam + microphone for your PC!**

Use in Discord, Zoom, Teams, OBS, Chrome, or ANY app that accepts a camera/mic input.

## Quick Start (3 Steps)

### Step 1: Install Drivers (one-time, ~30 seconds)
```
virtual_devices_setup.bat
```
Choose option 1 or 2 (auto-installs OBS Virtual Camera driver)

### Step 2: Start the Bridge
```
python backend/src/virtual_devices_windows.py --server wss://192.168.1.82:5000/ws --audio-device "Cable Input (VB-Audio Virtual Cable)"
```
Or run `virtual_devices_setup.bat` and choose option 2

### Step 3: Stream from Phone & Use in Apps
1. On phone: Open https://192.168.1.82:5000 → click "Start"
2. In your app: Select "OBS Virtual Camera" (camera) + audio device
3. Done! Your phone's camera and mic are now in the app.

## Why This Approach?

✅ **NO OBS Studio needed** — Just the lightweight driver (~2 MB)  
✅ **Works with ALL apps** — Discord, Zoom, Teams, OBS, browsers, etc.  
✅ **One-time setup** — Driver installs once, works forever  
✅ **Low resource use** — ~5-15% CPU, minimal memory  
✅ **Professional quality** — Full resolution, real-time audio  

## What Gets Installed

**Automatic:**
- OBS Virtual Camera Driver (2 MB) — lightweight kernel driver

**Optional (manual):**
- VB-Cable (500 KB) — for virtual microphone
  Download: https://vb-audio.com/Cable/

That's it. No bloated OBS app.

## Using with Your App

**Discord:**
```
Settings → Voice & Video
- Camera: "OBS Virtual Camera"
- Microphone: "Cable Input (VB-Audio Virtual Cable)"
```

**Zoom:**
```
Settings → Audio Device
- Camera: "OBS Virtual Camera"
- Microphone: "Cable Input (VB-Audio Virtual Cable)"
```

**OBS Studio (re-streaming):**
```
Add Video Capture Device → "OBS Virtual Camera"
Add Audio Input Device → "Cable Output (VB-Audio Virtual Cable)"
```

**Chrome/Firefox/Edge (video calls):**
```
Browser prompts when joining call
- Camera: "OBS Virtual Camera"
- Microphone: "Cable Input (VB-Audio Virtual Cable)"
```

## Server Side (Always Running)

Make sure server is running on the PC:
```
python backend/src/run_dev.py
```

Or on startup:
```
start.bat
```

## Configuration

**Custom resolution:**
```
python backend/src/virtual_devices_windows.py --server wss://192.168.1.82:5000/ws ^
  --camera-width 640 --camera-height 480 --camera-fps 15
```

**List audio devices:**
```
python backend/src/virtual_devices_windows.py --list-audio-devices
```

**Video only (no audio):**
```
python backend/src/virtual_devices_windows.py --server wss://192.168.1.82:5000/ws
```

## Troubleshooting

**"OBS Virtual Camera not found in app"**
1. Restart the app after starting the bridge
2. Check Windows Settings → Camera → app is allowed
3. Run `virtual_devices_setup.bat` again

**"Audio not working"**
1. Install VB-Cable: https://vb-audio.com/Cable/
2. Use `--audio-device "Cable Input (VB-Audio Virtual Cable)"`
3. Restart app to refresh audio device list
4. Check Windows Sound Settings

**"Video is laggy"**
1. Reduce resolution: `--camera-width 640 --camera-height 480 --camera-fps 15`
2. Check WiFi signal
3. Close bandwidth-heavy apps

For more details, see: **VIRTUAL_DEVICES_WINDOWS.md**

## Architecture

```
Phone (Camera/Mic)
    ↓ HTTPS/WebSocket
Server (Relay) 
    ↓ Broadcast
Virtual Device Bridge (PC)
    ├→ OBS Virtual Camera driver
    └→ VB-Cable driver
        ↓
    Any App (Discord, Zoom, OBS, etc.)
```

## Next Steps

1. Run: `virtual_devices_setup.bat`
2. Choose option 2 (Camera + Audio)
3. Open app (Discord, Zoom, Teams, etc.)
4. Select "OBS Virtual Camera" + audio device
5. Stream from phone: https://192.168.1.82:5000
6. Start video call! 🎉

Your phone is now a wireless webcam + mic for any app on your PC!
