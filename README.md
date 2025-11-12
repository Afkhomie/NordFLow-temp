# NodeFlow

NodeFlow is a real-time audio/video streaming application with a modern desktop GUI. Control your PC's webcam and microphone remotely through a secure HTTPS connection.

## Features

- 🎥 **Real-time Video Streaming** - Stream webcam video with low latency
- 🎤 **Audio Streaming** - Transmit microphone audio in real-time
- 🔒 **Secure Connection** - HTTPS/WSS with automatic SSL certificate generation
- 🖥️ **Modern GUI** - Clean, dark-themed CustomTkinter interface
- 📱 **Mobile Compatible** - Access from any device with a web browser
- 🚀 **Single Executable** - Everything bundled in one `.exe` file

## Quick Start

### Download Release (Easiest)

1. Download `NodeFlow-v1.0.0.zip` from [Releases](https://github.com/yourusername/nodeflow/releases)
2. Extract and run `NodeFlow.exe`
3. Click "Start Server"
4. Access from your phone/browser using the displayed URL

### Build from Source

#### Prerequisites
- Python 3.11+
- Windows OS (for building .exe)

#### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/nodeflow.git
   cd nodeflow
   ```

2. **Run setup**
   ```bash
   setup.bat
   ```

3. **Build the executable**
   ```bash
   build.bat
   ```

4. **Find your build**
   - Executable: `dist/NodeFlow.exe`
   - Releases: `release/NodeFlow-v1.0.0.zip` and `release/NodeFlow-Source-v1.0.0.zip`

## Usage

### Desktop Application

1. Launch `NodeFlow.exe`
2. Click **Start Server**
3. Note the displayed IP address and URL
4. Keep the application running

### Mobile/Web Access

1. On your phone/tablet, open a web browser
2. Navigate to the HTTPS URL shown in the GUI (e.g., `https://192.168.1.100:5000`)
3. **Accept the security warning** (self-signed certificate)
4. Grant camera/microphone permissions when prompted
5. Click "Start Camera" or "Start Mic"

### Testing Connection

- Use the test page: `https://YOUR_IP:5000/test`
- Check the server log in the GUI for connection status

## Project Structure

```
nodeflow/
├── backend/
│   ├── src/
│   │   ├── gui.py              # Main GUI application
│   │   ├── streaming/          # WebSocket server
│   │   ├── templates/          # Web interface files
│   │   ├── generate_cert.py    # SSL certificate generator
│   │   └── server.crt/key      # SSL certificates
│   └── requirements.txt        # Python dependencies
├── NodeFlow.spec               # PyInstaller configuration
├── build.bat                   # Build script
└── setup.bat                   # Setup script
```

## Configuration

The server runs on:
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `5000`
- **Protocol**: HTTPS/WSS

To change settings, edit `backend/src/core/config.py`

## Security Notes

⚠️ **Important Security Information**:

- NodeFlow uses **self-signed SSL certificates** for HTTPS
- Your browser will show a security warning - this is expected
- **Only use on trusted networks** (home WiFi, etc.)
- The connection is encrypted but not verified by a Certificate Authority
- For production use, replace with proper SSL certificates

### Accepting Security Warnings

**Chrome/Edge**: Click "Advanced" → "Proceed to [IP] (unsafe)"
**Firefox**: Click "Advanced" → "Accept Risk and Continue"
**Safari**: Click "Show Details" → "visit this website"

## Troubleshooting

### "Server won't start"
- Check if port 5000 is already in use
- Run as Administrator if needed
- Check firewall settings

### "Can't connect from phone"
- Ensure phone and PC are on the same network
- Check firewall allows incoming connections on port 5000
- Try disabling VPN

### "Camera/Mic not working"
- Grant browser permissions for camera/microphone
- Ensure HTTPS is used (not HTTP)
- Try the test page first

### "Build failed"
- Ensure Python 3.11+ is installed
- Run `setup.bat` first
- Check all dependencies installed correctly

## Development

### Running from Source

```bash
# Activate virtual environment
venv\Scripts\activate

# Run GUI
python backend/src/gui.py

# Or run server only
python backend/src/main.py
```

### Building for Distribution

```bash
# Full build with release packages
build.bat

# Just PyInstaller
pyinstaller NodeFlow.spec --clean
```

## Technologies Used

- **Backend**: Python, aiohttp, WebSockets
- **GUI**: CustomTkinter
- **Video Processing**: OpenCV
- **SSL/TLS**: cryptography, OpenSSL
- **Packaging**: PyInstaller

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)

## Author

**Afkhomie**

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history

---

Made with ❤️ by Afkhomie