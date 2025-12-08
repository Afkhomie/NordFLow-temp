# NodeFlow Virtual Devices - Quick Reference

## Installation (5 minutes) ⚡

```bash
# 1. Run setup script (requires Admin)
setup_virtual_devices.bat

# 2. Follow on-screen instructions to install:
#    - OBS Virtual Camera
#    - VB-Audio Virtual Cable

# 3. Restart Windows (important!)
```

## Running (2 minutes) ▶️

```bash
# Start receiver with virtual devices
start_receiver_virtual.bat

# Or manually:
cd backend/src
python receiver_gui.py
```

## Using in Apps 📱

### Discord
1. Click camera icon during call
2. Select **"OBS Virtual Camera"**
3. Share your phone's video! 🎥

### Zoom  
1. Settings → Video → Camera
2. Select **"OBS Virtual Camera"**
3. Your phone video streams to everyone

### OBS Studio
1. Sources → Video Capture Device
2. Select **"OBS Virtual Camera"**
3. Phone video appears on stream

### Teams/Webex
Same steps as above - just select "OBS Virtual Camera"

## Status Indicators 🟢

### In Console
```
✓ Virtual Camera initialized: 1280x720 @ 30fps
✓ Virtual Audio Device detected: CABLE Input
```

### In GUI
- Camera: ✓ or ✗ 
- Audio: ✓ or ✗

## Troubleshooting 🔧

### No camera in Discord?
→ Run `setup_virtual_devices.bat` to install OBS Virtual Camera

### No audio in Discord?
→ Install VB-Cable from https://vb-audio.com/Cable/ and restart Windows

### Camera works but laggy?
→ Reduce resolution in `receiver_gui.py`:
```python
initialize_virtual_devices(video_width=640, video_height=480, fps=15)
```

### Not finding phone?
→ Check IP address and WiFi connection
→ Verify phone app is running

## Commands

| Task | Command |
|------|---------|
| Setup devices | `setup_virtual_devices.bat` |
| Start receiver | `start_receiver_virtual.bat` |
| Install Python deps | `cd backend & pip install -r requirements.txt` |
| Check Python | `python --version` |
| Check pyvirtualcam | `python -c "import pyvirtualcam; print(pyvirtualcam.__version__)"` |

## Downloads

| Component | Link |
|-----------|------|
| OBS Virtual Camera | https://obsproject.com/forum/resources/obs-virtualcam.949/ |
| VB-Audio Virtual Cable | https://vb-audio.com/Cable/ |
| Python | https://www.python.org/downloads/ |

## Files Overview

| File | Purpose |
|------|---------|
| `VIRTUAL_DEVICES.md` | Full user guide |
| `VIRTUAL_DEVICES_SETUP.md` | Technical details |
| `IMPLEMENTATION_SUMMARY.md` | Developer reference |
| `setup_virtual_devices.bat` | Auto installer |
| `start_receiver_virtual.bat` | Quick launcher |
| `src/services/virtual_devices.py` | Core implementation |
| `src/receiver_gui.py` | Updated GUI |
| `src/receiver.py` | Updated receiver |

## Performance

| Metric | Value |
|--------|-------|
| Video FPS | ~30 |
| Resolution | 1280x720 (configurable) |
| Latency | 100-200ms |
| CPU | 10-15% |
| Memory | ~150MB |

## Support

1. Check VIRTUAL_DEVICES.md for detailed guide
2. Check console for error messages
3. Verify OBS Virtual Camera installed
4. Verify VB-Cable installed and Windows restarted
5. Try restarting receiver application

---

**Made for streaming your phone to anywhere! 🎥🎤**
