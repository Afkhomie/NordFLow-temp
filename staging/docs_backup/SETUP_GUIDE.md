# NodeFlow - Complete Setup Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Save the Files

Save these files in your project:

1. **`backend/src/gui.py`** - The GUI file I created
2. **`NodeFlow.spec`** - PyInstaller configuration
3. **`build.bat`** - Build script
4. **`.github/workflows/release.yml`** - GitHub Actions (optional)
5. **`README.md`** - Updated documentation

### Step 2: Update Requirements

Make sure `backend/requirements.txt` has these packages:

```txt
# Core dependencies
customtkinter>=5.2.0
aiohttp>=3.8.0
opencv-python>=4.8.0
Pillow>=10.0.0
cryptography>=41.0.4
pyOpenSSL>=23.0.0
websockets>=10.0
pyinstaller>=6.1.0
```

### Step 3: First Time Setup

```bash
# Run setup
setup.bat

# This will:
# - Create virtual environment
# - Install all dependencies
# - Setup Python 3.11
```

### Step 4: Build Your .exe

```bash
# Run the build script
build.bat

# Wait 2-5 minutes for build to complete
```

### Step 5: Test Your Build

```bash
# Your files will be in:
# - dist/NodeFlow.exe (ready to run)
# - release/NodeFlow-v1.0.0.zip (for distribution)
# - release/NodeFlow-Source-v1.0.0.zip (source code)
```

## 📁 File Structure (What Goes Where)

```
your-repo/
├── .github/
│   └── workflows/
│       └── release.yml          # NEW - Add this
├── backend/
│   ├── src/
│   │   ├── gui.py               # NEW - Replace empty file
│   │   ├── streaming/
│   │   ├── templates/
│   │   ├── generate_cert.py
│   │   ├── main.py
│   │   └── ... (other files)
│   └── requirements.txt         # UPDATE - Add customtkinter
├── NodeFlow.spec                # NEW - Add this
├── build.bat                    # NEW - Add this
├── setup.bat                    # Already exists
└── README.md                    # UPDATE with new version
```

## 🔧 What Each File Does

### `gui.py`
- Creates the dark-themed GUI window
- Shows server IP and port
- Starts server in background thread
- Displays server logs
- Start/Stop buttons

### `NodeFlow.spec`
- Tells PyInstaller how to bundle everything
- Includes templates and SSL certificates
- Creates single .exe file
- Sets icon and window style

### `build.bat`
- Cleans old builds
- Generates SSL certificates
- Runs PyInstaller
- Creates release ZIPs
- Does everything automatically

### `release.yml`
- Automates GitHub releases
- Builds on tag push (v1.0.0, etc.)
- Creates release with ZIPs attached
- Runs on GitHub servers (free)

## 🎯 Testing Your Build

### 1. Test Locally First

```bash
# Activate venv
venv\Scripts\activate

# Run GUI directly
python backend/src/gui.py
```

### 2. Test the .exe

```bash
# Run the built executable
dist\NodeFlow.exe
```

### 3. Test From Phone

1. Start server in GUI
2. Note the IP (e.g., 192.168.1.100:5000)
3. On phone, go to `https://192.168.1.100:5000`
4. Accept security warning
5. Grant camera/mic permissions
6. Click "Start Camera"

## 📦 Creating a Release

### Manual Release

1. Build with `build.bat`
2. Upload `release/NodeFlow-v1.0.0.zip` to GitHub Releases
3. Upload `release/NodeFlow-Source-v1.0.0.zip` too

### Automatic Release (GitHub Actions)

1. Commit all files
2. Create a tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. GitHub Actions will:
   - Build the .exe
   - Create release
   - Upload both ZIPs
   - All automatically!

## 🐛 Common Issues & Fixes

### Issue: "Python 3.11 not found"
**Fix**: Install Python 3.11 from python.org

### Issue: "Build failed - import error"
**Fix**: 
```bash
venv\Scripts\activate
pip install --upgrade -r backend/requirements.txt
```

### Issue: "GUI doesn't show"
**Fix**: Check `console=False` in NodeFlow.spec

### Issue: "Server won't start"
**Fix**: 
- Check port 5000 is free
- Run as Administrator
- Check firewall

### Issue: "Can't connect from phone"
**Fix**:
- Same WiFi network?
- Accept security warning?
- Grant browser permissions?

## 📊 File Sizes (Approximate)

- `NodeFlow.exe`: ~80-100 MB
- `NodeFlow-v1.0.0.zip`: ~30-40 MB (compressed)
- Source code zip: ~1-5 MB

## 🔄 Updating Your App

1. Make code changes
2. Update version in:
   - `gui.py` (window title)
   - `version.json`
   - `README.md`
   - Tag name (v1.0.1, etc.)
3. Run `build.bat`
4. Create new release

## 🎨 Customization Ideas

### Change Colors
Edit in `gui.py`:
```python
ctk.set_default_color_theme("blue")  # Try: "green", "dark-blue"
```

### Change Port
Edit in `gui.py`:
```python
port = 5000  # Change to any port
```

### Add Icon
1. Create `icon.ico` file
2. Place in root directory
3. Rebuild

## ✅ Checklist Before Release

- [ ] Tested GUI locally
- [ ] Tested .exe build
- [ ] Tested from phone/mobile
- [ ] Updated version numbers
- [ ] Updated CHANGELOG.md
- [ ] Committed all changes
- [ ] Created git tag
- [ ] Pushed to GitHub

## 🎉 You're Done!

Your project now has:
- ✅ Modern GUI with server controls
- ✅ Single .exe file (portable)
- ✅ Automatic builds on GitHub
- ✅ Two release packages (exe + source)
- ✅ Professional documentation

## Need Help?

1. Check the logs in GUI
2. Look at `build.bat` output
3. Test with `/test` page
4. Open an issue on GitHub

---

**Made by Afkhomie | Let's goooo! 🚀**