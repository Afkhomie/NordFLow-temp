"""
NodeFlow Desktop Receiver
Receives and displays video/audio streams from the mobile phone
Built with PyQt6 for Windows
"""

import sys
import json
import base64
import threading
import logging
from io import BytesIO
from collections import deque
from pathlib import Path
import ssl

import numpy as np
import cv2
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStatusBar, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread, QSize
from PyQt6.QtGui import QImage, QPixmap, QFont, QColor
import websocket
import sounddevice as sd

from services.virtual_devices import initialize_virtual_devices

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoBuffer:
    """Thread-safe video frame buffer"""
    def __init__(self, max_frames=30):
        self.buffer = deque(maxlen=max_frames)
        self.lock = threading.Lock()

    def put(self, frame_data):
        with self.lock:
            self.buffer.append(frame_data)

    def get(self):
        with self.lock:
            if self.buffer:
                return self.buffer.popleft()
            return None

    def size(self):
        with self.lock:
            return len(self.buffer)


class AudioPlayer:
    """Plays float32 PCM audio using sounddevice in a non-blocking OutputStream."""
    def __init__(self, sample_rate=16000, channels=1, blocksize=1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.blocksize = blocksize
        self.buffer = deque()
        self.lock = threading.Lock()
        self.stream = None
        self.enabled = False
        
        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                blocksize=self.blocksize,
                callback=self._callback
            )
            self.stream.start()
            self.enabled = True
            logger.info(f"Audio player initialized (sample rate: {self.sample_rate} Hz)")
        except Exception as e:
            # Fallback: scan devices and find first output-capable one
            try:
                devices = sd.query_devices()
                for i, d in enumerate(devices):
                    max_out = int(d.get('max_output_channels', 0) or 0)
                    if max_out >= 1:
                        try:
                            use_ch = max(min(max_out, self.channels), 1)
                            self.stream = sd.OutputStream(
                                samplerate=self.sample_rate,
                                channels=use_ch,
                                dtype='float32',
                                blocksize=self.blocksize,
                                device=i,
                                callback=self._callback
                            )
                            self.stream.start()
                            self.channels = use_ch
                            self.enabled = True
                            logger.info(f"Audio player initialized using device {i} (channels={use_ch})")
                            break
                        except Exception:
                            continue
            except Exception:
                pass

            if not self.enabled:
                logger.warning(f"Audio stream initialization failed: {e}. Continuing without audio.")

    def _callback(self, outdata, frames, time, status):
        if status and status != sd.CallbackFlags.output_underflow:
            logger.debug(f"Audio status: {status}")
        # Fill outdata from buffer or zeros
        with self.lock:
            if len(self.buffer) >= frames * self.channels:
                # Pop needed samples
                samples = [self.buffer.popleft() for _ in range(frames * self.channels)]
                arr = np.array(samples, dtype=np.float32)
                outdata[:] = arr.reshape((frames, self.channels))
            else:
                # Not enough data, output silence
                outdata.fill(0)

    def put(self, samples: np.ndarray):
        """Append a numpy float32 array (mono or shape (N,)) to buffer"""
        if not self.enabled or samples is None or len(samples) == 0:
            return
        try:
            flat = samples.flatten().astype(np.float32)
            with self.lock:
                for v in flat.tolist():
                    self.buffer.append(v)
        except Exception as e:
            logger.debug(f"Audio buffer error: {e}")

    def stop(self):
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
        except Exception as e:
            logger.debug(f"Audio stop error: {e}")


class WebSocketWorker(QObject):
    """Handles WebSocket connection in a separate thread"""
    video_frame_received = pyqtSignal(QImage)
    connection_status = pyqtSignal(str)
    stats_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, host='127.0.0.1', port=5000, virtual_manager=None):
        super().__init__()
        self.host = host
        self.port = port
        self.ws = None
        self.running = False
        self.virtual_manager = virtual_manager
        self.stats = {
            'frames_received': 0,
            'bytes_received': 0,
            'audio_frames': 0,
            'fps': 0
        }
        self.frame_count = 0
        self.last_update = None
        # Audio player will handle playback of incoming audio frames
        try:
            self.audio_player = AudioPlayer(sample_rate=16000, channels=1)
        except Exception as e:
            logger.warning(f"Audio player could not be initialized: {e}")
            self.audio_player = None

    def connect(self):
        """Connect to the server and receive streams"""
        protocol = 'wss' if self.port == 5000 else 'ws'
        uri = f'{protocol}://{self.host}:{self.port}/ws'
        
        try:
            # Disable certificate verification for self-signed certs
            ssl_opts = {'cert_reqs': ssl.CERT_NONE, 'check_hostname': False}
            
            self.connection_status.emit('Connecting...')
            self.ws = websocket.WebSocketApp(
                uri,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            self.ws.run_forever(sslopt=ssl_opts)
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.error_occurred.emit(f"Connection failed: {str(e)[:50]}")
            self.connection_status.emit('Error')

    def _on_open(self, ws):
        """Called when connection is established"""
        logger.info("WebSocket connected")
        self.connection_status.emit('Connected')
        self.running = True
        
        # Send hello message
        try:
            self.ws.send(json.dumps({
                'type': 'hello',
                'client': 'desktop-receiver'
            }))
        except Exception as e:
            logger.error(f"Failed to send hello: {e}")

    def _on_message(self, ws, message):
        """Called when a message is received"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')

            if msg_type == 'video':
                self._handle_video(data)
            elif msg_type == 'audio':
                self._handle_audio(data)
            elif msg_type == 'connection':
                self.connection_status.emit('Ready')

        except Exception as e:
            logger.error(f"Message handling error: {e}")

    def _handle_video(self, data):
        """Handle incoming video frame"""
        try:
            frame_data = base64.b64decode(data.get('data', ''))
            image = QImage()
            image.loadFromData(frame_data, 'JPEG')
            
            if not image.isNull():
                self.video_frame_received.emit(image)
                self.stats['frames_received'] += 1
                self.stats['bytes_received'] += len(frame_data)
                self._update_stats()
                
                # Send to virtual camera
                if self.virtual_manager:
                    try:
                        # Convert QImage to numpy array for virtual camera
                        width = image.width()
                        height = image.height()
                        ptr = image.bits()
                        ptr.setsize(image.byteCount())
                        arr = np.array(ptr).reshape(height, width, 4)  # RGBA
                        frame_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
                        self.virtual_manager.send_video_frame(frame_bgr)
                    except Exception as e:
                        pass  # Silent fail, virtual camera is optional
        except Exception as e:
            logger.error(f"Video decode error: {e}")

    def _handle_audio(self, data):
        """Handle incoming audio frame"""
        try:
            # Support two formats: list of floats in JSON or base64-encoded float32 bytes
            audio_field = data.get('data')
            sample_rate = int(data.get('sampleRate', 16000))
            samples = None
            if isinstance(audio_field, str):
                # try base64 decode
                try:
                    decoded = base64.b64decode(audio_field)
                    samples = np.frombuffer(decoded, dtype=np.float32)
                except Exception:
                    # fallback: empty
                    samples = None
            elif isinstance(audio_field, list):
                samples = np.array(audio_field, dtype=np.float32)

            if samples is not None and samples.size > 0:
                # Play via audio player if available
                if self.audio_player:
                    # If sample rates mismatch, we could resample; assume matching for now
                    self.audio_player.put(samples)
                self.stats['audio_frames'] += 1
                self._update_stats()
        except Exception as e:
            logger.error(f"Audio error: {e}")

    def _update_stats(self):
        """Update and emit statistics"""
        self.stats_updated.emit(self.stats.copy())

    def _on_error(self, ws, error):
        """Called on WebSocket error"""
        logger.error(f"WebSocket error: {error}")
        self.error_occurred.emit(str(error)[:50])

    def _on_close(self, ws, close_status_code, close_msg):
        """Called when connection closes"""
        logger.info("WebSocket disconnected")
        self.running = False
        self.connection_status.emit('Disconnected')

    def disconnect(self):
        """Disconnect from server"""
        if self.ws:
            self.ws.close()


class ReceiverGUI(QMainWindow):
    """Main GUI window for receiving streams"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('NodeFlow - Desktop Receiver')
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5568d3;
            }
            QPushButton:pressed {
                background-color: #445ab8;
            }
        """)
        
        # Initialize virtual devices
        self.virtual_manager = initialize_virtual_devices(video_width=1280, video_height=720, fps=30)
        self.virtual_manager.activate_audio_routing()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Video display area
        video_frame = QFrame()
        video_frame.setStyleSheet('background-color: #000; border: 2px solid #333; border-radius: 10px;')
        video_layout = QVBoxLayout(video_frame)
        
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet('background-color: #000;')
        video_layout.addWidget(self.video_label)
        
        layout.addWidget(video_frame, 3)
        
        # Control panel
        control_frame = QFrame()
        control_frame.setStyleSheet('background-color: white; border-radius: 10px;')
        control_frame.setMaximumWidth(300)
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(15)
        
        # Title
        title = QLabel('📡 NodeFlow')
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        control_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel('Desktop Receiver')
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet('color: #666;')
        control_layout.addWidget(subtitle)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        control_layout.addWidget(sep)
        
        # Status
        status_label_text = QLabel('Status:')
        status_label_text.setStyleSheet('font-weight: bold; color: #667eea;')
        control_layout.addWidget(status_label_text)
        
        self.status_label = QLabel('Disconnected')
        self.status_label.setStyleSheet('color: #f44336; font-weight: bold; font-size: 14px;')
        control_layout.addWidget(self.status_label)
        
        # Stats box
        stats_frame = QFrame()
        stats_frame.setStyleSheet('background: #f5f5f5; border-radius: 5px; padding: 10px;')
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        
        stats_title = QLabel('📊 Statistics')
        stats_title.setStyleSheet('font-weight: bold; color: #667eea;')
        stats_layout.addWidget(stats_title)
        
        self.stats_label = QLabel(
            'FPS: 0.0\n'
            'Frames: 0\n'
            'Data: 0.00 MB\n'
            'Audio: 0'
        )
        self.stats_label.setStyleSheet('font-family: monospace; font-size: 11px; color: #333;')
        stats_layout.addWidget(self.stats_label)
        control_layout.addWidget(stats_frame)
        
        # Connection info
        self.info_label = QLabel('Click "Connect" to start receiving streams from your phone.')
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet('font-size: 11px; color: #999; line-height: 1.5;')
        control_layout.addWidget(self.info_label)
        
        # Buttons
        connect_btn = QPushButton('🔗 Connect')
        connect_btn.setMinimumHeight(40)
        connect_btn.clicked.connect(self.start_connection)
        control_layout.addWidget(connect_btn)
        
        disconnect_btn = QPushButton('🔌 Disconnect')
        disconnect_btn.setMinimumHeight(40)
        disconnect_btn.clicked.connect(self.stop_connection)
        control_layout.addWidget(disconnect_btn)
        
        control_layout.addStretch()
        
        # Footer
        footer = QLabel('Phone URL: https://192.168.1.82:5000')
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet('font-size: 10px; color: #999; padding-top: 10px; border-top: 1px solid #eee;')
        control_layout.addWidget(footer)
        
        layout.addWidget(control_frame, 1)
        
        # WebSocket worker
        self.worker_thread = QThread()
        self.worker = WebSocketWorker(virtual_manager=self.virtual_manager)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.connection_status.connect(self._on_connection_status)
        self.worker.video_frame_received.connect(self._on_video_frame)
        self.worker.stats_updated.connect(self._on_stats_updated)
        self.worker.error_occurred.connect(self._on_error)
        
        self.worker_thread.started.connect(self.worker.connect)
        
        # Status bar
        self.statusBar().showMessage('Ready')

    def start_connection(self):
        """Start WebSocket connection"""
        if self.worker_thread.isRunning():
            return
        
        self.info_label.setText('Connecting to server...')
        self.worker_thread.start()

    def stop_connection(self):
        """Stop WebSocket connection"""
        self.worker.disconnect()
        self.worker_thread.quit()
        self.worker_thread.wait()
        
        # Clean up virtual devices
        if self.virtual_manager:
            self.virtual_manager.cleanup()
        
        # Create new thread for next connection
        self.worker_thread = QThread()
        self.worker = WebSocketWorker(virtual_manager=self.virtual_manager)
        self.worker.moveToThread(self.worker_thread)
        
        self.worker.connection_status.connect(self._on_connection_status)
        self.worker.video_frame_received.connect(self._on_video_frame)
        self.worker.stats_updated.connect(self._on_stats_updated)
        self.worker.error_occurred.connect(self._on_error)
        
        self.worker_thread.started.connect(self.worker.connect)
        self.info_label.setText('Disconnected.')

    def _on_connection_status(self, status):
        """Update connection status"""
        self.status_label.setText(status)
        if status == 'Connected':
            self.status_label.setStyleSheet('color: #4CAF50; font-weight: bold; font-size: 14px;')
            self.info_label.setText('✓ Connected! Receiving streams...')
        elif status == 'Ready':
            self.status_label.setStyleSheet('color: #4CAF50; font-weight: bold; font-size: 14px;')
            self.info_label.setText('✓ Ready to receive!')
        elif 'Error' in status or status == 'Disconnected':
            self.status_label.setStyleSheet('color: #f44336; font-weight: bold; font-size: 14px;')
            if status == 'Disconnected':
                self.info_label.setText('Disconnected from server.')
        else:
            self.status_label.setStyleSheet('color: #ff9800; font-weight: bold; font-size: 14px;')

    def _on_video_frame(self, image):
        """Display video frame"""
        if isinstance(image, QImage):
            # Scale to fit label while maintaining aspect ratio
            scaled = image.scaledToWidth(
                self.video_label.width(),
                Qt.TransformationMode.SmoothTransformation
            )
            pixmap = QPixmap.fromImage(scaled)
            self.video_label.setPixmap(pixmap)

    def _on_stats_updated(self, stats):
        """Update statistics display"""
        stats_text = (
            f"FPS: {stats['fps']:.1f}\n"
            f"Frames: {stats['frames_received']}\n"
            f"Data: {stats['bytes_received'] / (1024*1024):.2f} MB\n"
            f"Audio: {stats['audio_frames']}"
        )
        self.stats_label.setText(stats_text)

    def _on_error(self, error_msg):
        """Handle error"""
        logger.error(f"Error: {error_msg}")

    def closeEvent(self, event):
        """Handle window close"""
        self.stop_connection()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = ReceiverGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

