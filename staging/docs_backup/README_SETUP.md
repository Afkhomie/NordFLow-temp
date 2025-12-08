# NodeFlow - Real-Time Media Streaming
**Stream your phone's camera and microphone to your PC in real-time with NodeFlow.**

---

## 🎯 What is NodeFlow?

NodeFlow is an end-to-end media streaming application that allows you to:
- **Stream camera video** from your phone to a Windows PC desktop receiver
- **Stream microphone audio** from your phone to the PC
- **View live video** on your PC with real-time preview on the phone
- **Zero latency** HTTPS connection with self-signed SSL certificates

---

## 📋 System Requirements

### Phone
- **Android 7+** or **iOS 12+**
- **Modern browser** (Chrome, Firefox, Safari, Edge)
- **WiFi connection** on the same network as PC

### PC (Windows)
- **Windows 10/11**
- **Python 3.8+** (Python 3.11 recommended)
- **1GB RAM** (minimum for GUI)
- **Port 5000** available (HTTPS server)

---

## ⚡ Quick Start

### Option 1: Automated Setup (Easiest)

1. **Navigate to the NodeFlow directory:**
   ```powershell
   cd "C:\path\to\NodeFlow"
   ```

2. **Run the startup script:**
   ```powershell
   .\start.bat
   ```

   This will:
   - Check your Python installation
   - Install all dependencies
   - Generate SSL certificates (if missing)
   - Start the HTTPS server
   - Launch the desktop receiver GUI

3. **On your phone:**
   - Open the URL printed in the server logs (e.g., `https://192.168.1.82:5000/`)
   - Accept the SSL certificate warning
   - Press **"Start Camera"** to begin streaming video
   - Press **"Start Microphone"** to begin streaming audio

4. **On your PC:**
   - Watch the live video feed in the desktop receiver window
   - Audio will play through your default speaker

---

### Option 2: Manual Setup

1. **Open PowerShell in the NodeFlow directory:**
   ```powershell
   cd "C:\path\to\NodeFlow"
   ```

2. **Activate the Python virtual environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r backend/requirements.txt
   ```

4. **Generate SSL certificates (if missing):**
   ```powershell
   cd backend/src
   python generate_cert.py
   ```

5. **Start the server:**
   ```powershell
   python run_dev.py
   ```

   The output will show:
   ```
   Starting dev server (listen on all interfaces) — access at: https://192.168.1.82:5000/
   ```

6. **In a new PowerShell window, start the desktop receiver:**
   ```powershell
   cd backend/src
   python receiver.py
   ```

7. **On your phone:**
   - Open the URL from the server output (e.g., `https://192.168.1.82:5000/`)
   - Accept the SSL certificate warning
   - Press **"Start Camera"** and **"Start Microphone"**

---

## 🎮 Mobile Interface

### Camera Controls
- **Start** - Begins streaming your camera video with horizontal mirroring
- **Stop** - Stops the camera stream
- **Preview** - Small preview canvas shows your mirrored video

### Microphone Controls
- **Start** - Begins streaming audio from your microphone
- **Stop** - Stops the audio stream

### Status Indicators
- **Status Dot** - Green (connected), Orange (connecting), Red (error)
- **Device Status** - Shows ✓/✗ for camera and microphone

---

## 🖥️ Desktop Receiver Interface

### Main Display
- **Video Preview** - Large canvas showing incoming video from your phone
- **Status Indicator** - Shows connection state (Connected/Disconnected/Error)
- **Statistics Panel** - Displays:
  - FPS (frames per second)
  - Total frames received
  - Data transferred (MB)
  - Audio frames received

### Controls
- **Connect** - Initiate connection to server and begin receiving streams
- **Disconnect** - Stop receiving streams and close connection

---

## 🔒 Security

### SSL Certificates
- **Self-signed certificates** are generated automatically
- **First connection:** Accept the certificate warning in your browser
- **This is safe for local network use** (same WiFi)
- **Certificates expire after 365 days** — regenerate if needed

### Permissions
- **Camera & Microphone**: Granted automatically for 24 hours on first connection
- **Mobile browser** will request permission when you press "Start"

### Network
- **HTTPS-only** — all traffic is encrypted
- **Local network only** — server binds to `0.0.0.0:5000` on your LAN
- **No data leaves your network**

---

## 🛠️ Troubleshooting

### "Phone can't connect to server"
1. Verify both PC and phone are on the **same WiFi network**
2. Check the IP address in server logs (e.g., `https://192.168.1.82:5000/`)
3. Replace with your actual PC IP if different
4. Disable phone's WiFi sleep (in WiFi settings)

### "ERR_SSL_PROTOCOL_ERROR" on phone
1. This is **normal** for self-signed certificates
2. In the browser address bar, tap "Advanced" or "Proceed"
3. Select "Accept risk" or "Continue anyway"

### "Microphone: AudioNodes from AudioContexts with different sample-rate"
1. **Fixed in latest version** — uses native browser sample rate
2. If still occurring, try a different browser on your phone
3. Try refreshing the page (F5 on phone)

### "Desktop receiver shows no video"
1. Ensure mobile page shows the **preview canvas** (small square below status)
2. Check PC receiver window title bar (should say "NodeFlow - Desktop Receiver")
3. Try clicking "Connect" button in receiver again
4. Check server logs for errors: `python run_dev.py` output
5. Ensure **no firewall** is blocking port 5000

### "Audio is not playing on PC"
1. Check **system audio settings** — ensure default playback device is correct
2. In receiver GUI, look for **"Audio frames: N"** stat (should be > 0 if audio is being sent)
3. If stat shows 0, the phone is not sending audio — press "Start Mic" on phone again
4. Try a different audio output device (Settings > Sound)

### "Server won't start on port 5000"
1. Check if another app is using port 5000:
   ```powershell
   netstat -ano | findstr :5000
   ```
2. Close the conflicting app or choose a different port by editing `run_dev.py`

### "Dependencies failed to install"
1. Ensure Python 3.8+ is installed:
   ```powershell
   python --version
   ```
2. Upgrade pip:
   ```powershell
   pip install --upgrade pip
   ```
3. Try installing dependencies individually:
   ```powershell
   pip install aiohttp websockets websocket-client PyQt6
   ```

---

## 📊 Performance Tips

### For Better Video Quality
- **Position your phone** with good lighting
- **Move closer** to your WiFi router
- **Reduce background applications** on both devices
- Video resolution is adaptive based on device capability

### For Better Audio Quality
- **Keep your phone's microphone** clear of obstructions
- **Reduce ambient noise** in your room
- Audio sample rate automatically matches your browser's native rate

### For Lower Latency
- **Use 5GHz WiFi** if available (faster than 2.4GHz)
- **Close unnecessary browser tabs** on your phone
- **Disable WiFi sleep** on your phone

---

## 📱 Device Compatibility

### Tested Phones
- ✅ Android 12+ (Chrome, Firefox)
- ✅ iOS 15+ (Safari)
- ✅ iPad/Tablets (works but optimized for phones)

### Browser Support
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## 🧹 Cleanup & Uninstall

### To stop the server
1. Press `Ctrl+C` in the PowerShell window running the server

### To remove dependencies
```powershell
pip uninstall -r backend/requirements.txt -y
```

### To remove SSL certificates (regenerate new ones)
```powershell
rm backend/src/server.crt backend/src/server.key
python backend/src/generate_cert.py
```

---

## 📝 Project Structure

```
NodeFlow/
├── README_SETUP.md          # This file
├── backend/
│   ├── requirements.txt     # Python dependencies
│   ├── src/
│   │   ├── run_dev.py       # Development server launcher
│   │   ├── receiver.py      # Desktop receiver GUI (PyQt6)
│   │   ├── generate_cert.py # SSL certificate generator
│   │   ├── templates/
│   │   │   └── index.html   # Mobile web interface
│   │   ├── streaming/
│   │   │   └── server_new.py # WebSocket & REST server
│   │   └── services/
│   │       └── hardware_service.py
│   └── server.crt, server.key # SSL certificates
├── frontend/                # React frontend (optional)
└── start.bat               # Windows startup script
```

---

## 🚀 Advanced Configuration

### Change Server Port
Edit `backend/src/run_dev.py` and modify:
```python
asyncio.run(server.run(host='0.0.0.0', port=5001, ssl_context=ssl_context))
```

### Adjust Video Quality
Edit `backend/src/templates/index.html` in the config section:
```javascript
const config = {
    video: {
        width: 1280,        // Change to 640 for lower quality
        height: 720,        // Change to 480 for lower quality
        frameRate: 15       // Change to 10 for lower frame rate
    },
    audio: {
        sampleRate: 16000   // Leave as is (auto-detected)
    }
};
```

### Change Desktop Receiver Connection
Edit `backend/src/receiver.py`:
```python
self.worker = WebSocketReceiver(host='127.0.0.1', port=5000)
```

---

## 📞 Support

For issues or suggestions:
1. Check the **Troubleshooting** section above
2. Review server logs for error messages
3. Ensure all dependencies are installed: `pip list | findstr -i "aiohttp|PyQt6|websocket"`
4. Verify Python version: `python --version` (should be 3.8+)

---

## 📄 License

NodeFlow is provided as-is for personal and educational use.

---

**Last Updated:** December 2025  
**Tested on:** Python 3.11, Windows 10/11, Android 12+, iOS 15+

---

## ✅ Checklist for First-Time Use

- [ ] PC and phone on same WiFi network
- [ ] Python 3.8+ installed on PC
- [ ] Ran `start.bat` or installed dependencies manually
- [ ] Server is running (`python run_dev.py`)
- [ ] Desktop receiver GUI is running (`python receiver.py`)
- [ ] Opened phone URL in browser (accept SSL warning)
- [ ] Pressed "Start Camera" on mobile
- [ ] Watched video appear in desktop receiver
- [ ] Pressed "Start Microphone" on mobile
- [ ] Heard audio play through PC speakers

**All checked? 🎉 You're ready to stream!**
