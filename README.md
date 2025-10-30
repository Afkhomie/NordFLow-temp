# NodeFlow

NodeFlow is a personal desktop application for securely controlling sensitive hardware (Microphone, Webcam, Speaker) on your PC using a modern CustomTkinter GUI.

## Features

- Control PC hardware devices (Webcam, Microphone, Speaker)
- Modern, dark-themed CustomTkinter GUI
- Real-time device status monitoring
- Secure local device control
- Session-based permissions
- Visual indicators for active devices
- Comprehensive logging system

## Project Structure

```
nodeflow/
├── src/                  # Source code
│   ├── app.py           # Main application entry point
│   ├── controllers/     # Device control logic
│   ├── models/         # Data models
│   ├── services/       # Hardware interaction services
│   └── utils/         # Security and helper utilities
├── tests/             # Python unit tests
├── logs/             # Application logs
└── requirements.txt   # Python dependencies
```

## Setup Instructions

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python src/app.py
   ```

## Building Executable

1. Build standalone executable:
   ```bash
   pyinstaller --name nodeflow --windowed --onefile src/app.py
   ```

2. The executable will be created in the `dist` directory

## Security Features

- Local-only operation (no network access required)
- Session-based device permissions
- Explicit user consent required for device access
- Visual indicators for active devices
- Comprehensive activity logging
- System-based authentication

## Required Permissions

The application requires permissions to access:
- Webcam
- Microphone
- Audio output devices

## Development

To contribute to NodeFlow:

1. Fork the repository
2. Create a virtual environment
3. Install development dependencies
4. Make your changes
5. Run tests
6. Submit a pull request

## Dependencies

- Python 3.8+
- CustomTkinter
- OpenCV
- PyAudio
- Pillow
- Other dependencies listed in requirements.txt

## License

This project is licensed under the MIT License - see the LICENSE file for details.
