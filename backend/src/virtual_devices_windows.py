"""
virtual_devices_windows.py

Standalone bridge that converts NodeFlow streams into Windows virtual devices.
- Receives video frames from phone via WebSocket
- Feeds frames into OBS Virtual Camera driver (pyvirtualcam)
- Routes audio to VB-Audio Virtual Cable (via sounddevice)

No OBS Studio required - just driver dependencies (installed once).

Requirements:
- pyvirtualcam (pip install pyvirtualcam)
  - Downloads and installs OBS Virtual Camera driver automatically
- VB-Cable (https://vb-audio.com/Cable/) - manual installation for audio
- sounddevice (already in requirements.txt)

Usage:
python virtual_devices_windows.py --server wss://192.168.1.82:5000/ws
     [--camera-width 1280] [--camera-height 720] [--camera-fps 30]
     [--audio-device "Cable Input (VB-Audio Virtual Cable)"]

What happens:
1. Connects to NodeFlow server WebSocket
2. Receives video frames (base64 JPEG)
3. Decodes JPEG → RGB array
4. Feeds RGB to virtual camera (Windows sees as "OBS Virtual Camera")
5. Receives audio frames (raw PCM float32)
6. Writes audio to virtual cable device
7. Other apps (Discord, Zoom, Teams, OBS) can select:
   - Webcam: "OBS Virtual Camera"
   - Microphone: "Cable Input (VB-Audio Virtual Cable)"

Performance:
- Video: 15-30 FPS depending on bandwidth and PC specs
- Audio: Real-time with 10-second buffer to handle jitter
- CPU: ~5-15% (mostly JPEG decoding and frame resizing)
"""

import argparse
import base64
import json
import logging
import sys
from collections import deque
from io import BytesIO

import numpy as np
import websocket

try:
    import pyvirtualcam
except ImportError:
    print("ERROR: pyvirtualcam not installed")
    print("Install with: pip install pyvirtualcam")
    print("(This will auto-download the OBS Virtual Camera driver)")
    sys.exit(1)

try:
    import sounddevice as sd
except ImportError:
    print("ERROR: sounddevice not installed")
    print("Install with: pip install sounddevice")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed")
    print("Install with: pip install Pillow")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('virtual_devices')


class VirtualDevicesBridge:
    def __init__(self, server, camera_width=1280, camera_height=720, camera_fps=30, audio_device=None):
        self.server = server
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera_fps = camera_fps
        self.audio_device = audio_device
        
        self.ws = None
        self.camera = None
        self.audio_stream = None
        self.audio_buffer = deque(maxlen=480000)  # ~10 seconds @ 48kHz
        self.sample_rate = 16000
        self.running = False

    def init_camera(self):
        """Initialize virtual camera"""
        logger.info(f"Initializing virtual camera: {self.camera_width}x{self.camera_height}@{self.camera_fps}fps")
        try:
            self.camera = pyvirtualcam.Camera(
                width=self.camera_width,
                height=self.camera_height,
                fps=self.camera_fps
            )
            logger.info("✓ Virtual camera initialized")
            logger.info("  Windows now sees: OBS Virtual Camera")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize virtual camera: {e}")
            logger.error("Make sure OBS Virtual Camera driver is installed:")
            logger.error("  1. pyvirtualcam will attempt to install it automatically")
            logger.error("  2. Or download from: https://github.com/obsproject/obs-studio/releases")
            return False

    def init_audio(self, sample_rate=16000):
        """Initialize virtual audio output"""
        if not self.audio_device:
            logger.info("Audio device not specified; audio will not be routed")
            return True

        logger.info(f"Initializing audio to device: {self.audio_device}")
        self.sample_rate = sample_rate
        self.audio_buffer.clear()

        def audio_callback(outdata, frames, time_info, status):
            if status:
                logger.debug(f"Audio callback status: {status}")
            
            samples = []
            for _ in range(frames):
                if self.audio_buffer:
                    samples.append(self.audio_buffer.popleft())
                else:
                    samples.append(0.0)
            
            outdata[:, 0] = np.array(samples, dtype=np.float32)

        try:
            self.audio_stream = sd.OutputStream(
                samplerate=sample_rate,
                channels=1,
                dtype='float32',
                device=self.audio_device,
                callback=audio_callback
            )
            self.audio_stream.start()
            logger.info("✓ Virtual audio output initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            logger.warning("Audio will not be routed. Make sure VB-Cable is installed:")
            logger.warning("  https://vb-audio.com/Cable/")
            logger.warning("  Then set audio_device to: 'Cable Input (VB-Audio Virtual Cable)'")
            return False

    def on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')

            if msg_type == 'video':
                self._handle_video(data)
            elif msg_type == 'audio':
                self._handle_audio(data)

        except Exception as e:
            logger.debug(f"Message error: {e}")

    def _handle_video(self, data):
        """Handle incoming video frame"""
        if not self.camera:
            return

        try:
            b64_data = data.get('data', '')
            if not b64_data:
                return

            # Decode base64 JPEG
            jpeg_data = base64.b64decode(b64_data)
            image = Image.open(BytesIO(jpeg_data))

            # Convert to RGB (in case it's RGBA or grayscale)
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize to match camera resolution
            image = image.resize((self.camera_width, self.camera_height), Image.Resampling.LANCZOS)

            # Convert to numpy array
            frame = np.array(image, dtype=np.uint8)

            # Send to virtual camera
            self.camera.send(frame)

        except Exception as e:
            logger.debug(f"Video frame error: {e}")

    def _handle_audio(self, data):
        """Handle incoming audio frame"""
        if not self.audio_stream:
            return

        try:
            audio_field = data.get('data')
            sample_rate = int(data.get('sampleRate', 16000))
            samples = None

            # Recreate stream if sample rate changed
            if sample_rate != self.sample_rate:
                logger.info(f"Sample rate change: {self.sample_rate}Hz → {sample_rate}Hz")
                if self.audio_stream:
                    self.audio_stream.stop()
                    self.audio_stream.close()
                self.init_audio(sample_rate)

            # Decode audio data
            if isinstance(audio_field, str):
                try:
                    decoded = base64.b64decode(audio_field)
                    samples = np.frombuffer(decoded, dtype=np.float32)
                except Exception:
                    samples = None
            elif isinstance(audio_field, list):
                samples = np.array(audio_field, dtype=np.float32)

            # Add to buffer
            if samples is not None and samples.size > 0:
                flat = samples.flatten().astype(np.float32)
                for s in flat.tolist():
                    self.audio_buffer.append(s)

        except Exception as e:
            logger.debug(f"Audio frame error: {e}")

    def on_open(self, ws):
        """WebSocket connected"""
        logger.info("✓ Connected to NodeFlow server")
        try:
            ws.send(json.dumps({
                'type': 'hello',
                'client': 'virtual-devices-windows'
            }))
        except Exception:
            pass

    def on_close(self, ws, close_status, close_msg):
        """WebSocket closed"""
        logger.info("WebSocket disconnected")
        self.running = False

    def on_error(self, ws, err):
        """WebSocket error"""
        logger.error(f"WebSocket error: {err}")

    def run(self):
        """Main loop"""
        if not self.init_camera():
            logger.error("Cannot proceed without virtual camera. Exiting.")
            return False

        self.init_audio(self.sample_rate)

        logger.info("\n" + "=" * 70)
        logger.info("NodeFlow Virtual Devices Bridge (Windows)")
        logger.info("=" * 70)
        logger.info("\nYour PC is now a virtual webcam + microphone!\n")
        logger.info("In any app (Discord, Zoom, Teams, OBS, Chrome, etc.):")
        logger.info("  • Select Webcam: 'OBS Virtual Camera'")
        if self.audio_device:
            logger.info(f"  • Select Microphone: '{self.audio_device}'")
        logger.info("\nStreaming from phone:")
        logger.info(f"  • Open: https://<YOUR_PC_IP>:5000 on phone")
        logger.info("  • Accept SSL certificate warning")
        logger.info("  • Click 'Start' for camera and microphone")
        logger.info("\nPress Ctrl+C to stop\n")
        logger.info("=" * 70 + "\n")

        self.running = True
        self.ws = websocket.WebSocketApp(
            self.server,
            on_message=self.on_message,
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error
        )
        self.ws.run_forever(sslopt={'cert_reqs': 0})

        return True

    def stop(self):
        """Clean up"""
        if self.camera:
            self.camera.close()
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
        if self.ws:
            self.ws.close()


def list_audio_devices():
    """List available audio output devices"""
    print("\nAvailable audio output devices:")
    print("=" * 80)
    try:
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0:
                print(f"Device {i}: {dev['name']}")
                print(f"  Channels: {dev['max_output_channels']}, SR: {dev['default_samplerate']}")
                print()
    except Exception as e:
        print(f"Error querying devices: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='NodeFlow Virtual Devices Bridge - Use phone as PC webcam + mic',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (video only)
  python virtual_devices_windows.py --server wss://192.168.1.82:5000/ws

  # Video + audio to VB-Cable
  python virtual_devices_windows.py --server wss://192.168.1.82:5000/ws \\
    --audio-device "Cable Input (VB-Audio Virtual Cable)"

  # Custom resolution
  python virtual_devices_windows.py --server wss://192.168.1.82:5000/ws \\
    --camera-width 640 --camera-height 480 --camera-fps 15

  # List available audio devices
  python virtual_devices_windows.py --list-audio-devices
        """
    )
    parser.add_argument('--server', default='wss://192.168.1.82:5000/ws',
                        help='NodeFlow server WebSocket URL (default: wss://192.168.1.82:5000/ws)')
    parser.add_argument('--camera-width', type=int, default=1280,
                        help='Virtual camera width (default: 1280)')
    parser.add_argument('--camera-height', type=int, default=720,
                        help='Virtual camera height (default: 720)')
    parser.add_argument('--camera-fps', type=int, default=30,
                        help='Virtual camera FPS (default: 30)')
    parser.add_argument('--audio-device',
                        help='Audio device name for routing (e.g., "Cable Input (VB-Audio Virtual Cable)")')
    parser.add_argument('--list-audio-devices', action='store_true',
                        help='List available audio devices and exit')

    args = parser.parse_args()

    if args.list_audio_devices:
        list_audio_devices()
        return

    bridge = VirtualDevicesBridge(
        args.server,
        args.camera_width,
        args.camera_height,
        args.camera_fps,
        args.audio_device
    )

    try:
        bridge.run()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        bridge.stop()
        logger.info("Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        bridge.stop()
        sys.exit(1)


if __name__ == '__main__':
    main()
