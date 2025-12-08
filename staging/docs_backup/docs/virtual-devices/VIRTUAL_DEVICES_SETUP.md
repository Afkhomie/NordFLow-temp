# Virtual Devices Setup Guide

This guide explains how to enable virtual camera and microphone support in NodeFlow, allowing your phone stream to be recognized as actual input devices in Windows.

## Overview

The virtual devices system lets Windows apps (Discord, Zoom, OBS, Teams, etc.) detect your phone's video/audio stream as native input devices.

- **Virtual Camera**: Phone video appears as "OBS Virtual Camera" 
- **Virtual Microphone**: Phone audio routes to "CABLE Output" (VB-Audio Virtual Cable)

## Prerequisites

### 1. OBS Virtual Camera (For Video)

**What it does:** Creates a virtual camera that Windows and apps can use

**Installation:**
1. Download: https://obsproject.com/forum/resources/obs-virtualcam.949/
2. Run the installer: `OBS-Studio-*.exe`
3. During installation, check "OBS Virtual Camera Plugin"
4. Complete installation

**Verify:**
```powershell
# Open Discord/Zoom and check camera sources
# You should see "OBS Virtual Camera" as an option
```

### 2. VB-Audio Virtual Cable (For Audio)

**What it does:** Creates a virtual microphone that receives audio from NodeFlow

**Installation:**
1. Download: https://vb-audio.com/Cable/
2. Download the installer: `VB-CABLE_Driver_Pack*.zip`
3. Extract and run `VBCABLE_Setup.exe` (or `VBCABLE_Setup_x64.exe` for 64-bit)
4. Click "Install Driver"
5. **Important:** You may need to restart Windows

**Verify:**
```powershell
# Open Sound Settings
# Check Recording Devices
# You should see "CABLE Input" or "VB-CABLE Input"
```

## Python Setup

NodeFlow already includes `pyvirtualcam` in requirements.txt. Just install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Running NodeFlow with Virtual Devices

### GUI Version (receiver_gui.py)

```bash
cd backend/src
python receiver_gui.py
```

When you connect to your phone:
- ✓ Video automatically streams to OBS Virtual Camera
- ✓ Audio automatically routes to VB-Cable
- Both devices appear in Windows device list

### Console Version (receiver.py)

```bash
cd backend/src
python receiver.py
```

## Testing Virtual Devices

### Test Video Camera

**Option 1: Windows Camera App**
```powershell
# Open Camera app
# Select "OBS Virtual Camera" from camera list
# You should see your phone's video
```

**Option 2: Discord**
1. Open Discord
2. Start a voice call or screen share
3. Click camera icon
4. Select "OBS Virtual Camera"
5. You should see your phone's video

### Test Audio Microphone

**Option 1: Windows Sound Settings**
```powershell
# Open Settings > Sound > Input devices
# Look for "CABLE Input" or "VB-CABLE Input"
# It should show activity when NodeFlow is connected
```

**Option 2: Discord**
1. Open Discord
2. Start a voice call
3. Click microphone icon
4. Select microphone as "CABLE Output"
5. Others should hear your phone's audio

## Troubleshooting

### "OBS Virtual Camera not available"

**Solution:**
1. Make sure OBS Virtual Camera is installed (not OBS Studio)
2. Download the standalone plugin from: https://obsproject.com/forum/resources/obs-virtualcam.949/
3. Reinstall the plugin

### "Virtual Audio Device not found"

**Solution:**
1. Install VB-Audio Virtual Cable: https://vb-audio.com/Cable/
2. **Restart Windows after installation**
3. Run NodeFlow again

### Virtual camera appears but no video

**Solution:**
1. Check that your phone is streaming to NodeFlow GUI
2. Look at the console for errors like "Virtual camera send error"
3. Try restarting the receiver application
4. Verify frame format with: `cv2.cvtColor()` is working

### Audio not routing to virtual mic

**Solution:**
1. Check that VB-Cable is installed and Windows is restarted
2. In Windows Sound Settings, verify "CABLE Input" exists in Recording devices
3. Try reconnecting NodeFlow receiver
4. Check logs for audio routing errors

## Advanced: Bundled Installation

To create a single installer that includes everything:

```batch
:: setup_all.bat
@echo off

echo Installing NodeFlow Virtual Devices...

:: Install OBS Virtual Camera
echo [1/2] Installing OBS Virtual Camera...
start /wait installers\OBS-VirtualCam-Installer.exe /S

:: Install VB-Audio Cable
echo [2/2] Installing VB-Audio Virtual Cable...
start /wait installers\VB-CABLE_Setup_x64.exe /VERYSILENT /RESTART

:: Install Python dependencies
echo [3/3] Installing Python packages...
cd backend
pip install -r requirements.txt -q

echo.
echo ✓ Installation complete!
echo You may need to restart Windows for audio device to work.
pause
```

## Architecture

### Video Pipeline
```
Phone Camera
    ↓
Mobile App (streams JPEG via WebSocket)
    ↓
receiver_gui.py (receives JPEG)
    ↓
VirtualCameraManager (converts to BGR numpy array)
    ↓
pyvirtualcam (sends to OBS Virtual Camera)
    ↓
Windows sees "OBS Virtual Camera"
    ↓
Apps (Discord, Zoom, OBS, etc.)
```

### Audio Pipeline
```
Phone Microphone
    ↓
Mobile App (streams float32 PCM via WebSocket)
    ↓
receiver_gui.py (receives PCM samples)
    ↓
VirtualAudioRouter (routes to VB-Cable)
    ↓
sounddevice.OutputStream (plays to CABLE Input)
    ↓
Windows sees "CABLE Output" as microphone
    ↓
Apps (Discord, Zoom, OBS, etc.)
```

## Performance Notes

- **Video:** ~30 FPS at 1280x720 (typical)
- **Audio:** 16kHz sample rate, 1 channel (mono)
- **Latency:** 100-200ms typical (depends on network)
- **CPU:** ~5-15% (varies by resolution)

## Security Considerations

- Virtual devices are **local only** (no network exposure)
- Audio/video only available to apps on your Windows device
- No data leaves your computer except to your phone and apps using the virtual devices
- Encryption: Uses same SSL/TLS as regular NodeFlow connection

## Uninstalling

To remove virtual device support:

### OBS Virtual Camera
1. Control Panel → Programs → Programs and Features
2. Find "OBS Virtual Camera"
3. Click Uninstall

### VB-Audio Virtual Cable
1. Control Panel → Programs → Programs and Features
2. Find "VB-CABLE"
3. Click Uninstall
4. Restart Windows

## Advanced Configuration

### Custom Resolution

Edit `receiver_gui.py`:
```python
# Change from 1280x720 to custom size
self.virtual_manager = initialize_virtual_devices(
    video_width=1920,    # 1920x1080
    video_height=1080,
    fps=30
)
```

### Custom Audio Device

Edit `services/virtual_devices.py` - add device name to `virtual_names` list:
```python
virtual_names = [
    'CABLE Input',           # VB-Audio
    'Your Custom Device',    # Add here
    'Another Device',
]
```

### Disable Virtual Devices

In `receiver_gui.py`, comment out:
```python
# self.virtual_manager = initialize_virtual_devices(...)
# self.virtual_manager.activate_audio_routing()
```

## Support

For issues:
1. Check console logs for errors
2. Verify OBS Virtual Camera and VB-Cable are installed
3. Restart Windows after installing drivers
4. Check that NodeFlow desktop app is running
5. Ensure phone is connected and streaming

## References

- OBS Virtual Camera: https://obsproject.com/forum/resources/obs-virtualcam.949/
- VB-Audio Virtual Cable: https://vb-audio.com/Cable/
- pyvirtualcam: https://github.com/letmaik/pyvirtualcam
- sounddevice: https://python-sounddevice.readthedocs.io/
