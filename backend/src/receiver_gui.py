"""
NodeFlow Desktop Receiver - Professional GUI
Real-time video display and audio playback with comprehensive statistics
Built with PyQt6 for cross-platform GUI support
"""

import sys
import json
import base64
import threading
import time
from collections import deque
from datetime import datetime

import numpy as np
import websocket
import sounddevice as sd
import cv2
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStatusBar, QScrollArea, QFrame
)
from PyQt6.QtGui import QImage, QPixmap, QFont, QColor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtWidgets import QProgressBar

from services.virtual_devices import initialize_virtual_devices


class AudioPlayer:
    """Plays float32 PCM audio using sounddevice"""
    def __init__(self, sample_rate=16000, channels=1, blocksize=1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.blocksize = blocksize
        self.buffer = deque(maxlen=sample_rate * 10)
        self.stream = None
        self.running = True
        
        # Try to open stream using system default device
        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                blocksize=self.blocksize,
                callback=self._callback
            )
            self.stream.start()
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
                            break
                        except Exception:
                            continue
            except Exception:
                pass
            
            if not self.stream:
                print(f"Audio warning: {e}")
                print("Continuing without audio.")

    def _callback(self, outdata, frames, time_info, status):
        if status:
            print(f"Audio status: {status}")
        
        samples = []
        for _ in range(frames * self.channels):
            if self.buffer:
                samples.append(self.buffer.popleft())
            else:
                samples.append(0.0)
        
        if samples:
            arr = np.array(samples, dtype=np.float32)
            outdata[:] = arr.reshape((frames, self.channels))
        else:
            outdata.fill(0)

    def put(self, samples: np.ndarray):
        """Add audio samples to playback buffer"""
        if samples is None or len(samples) == 0:
            return
        try:
            flat = samples.flatten().astype(np.float32)
            for v in flat.tolist():
                self.buffer.append(v)
        except Exception as e:
            print(f"Audio error: {e}")

    def stop(self):
        self.running = False
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
        except:
            pass


class WebSocketWorker(QThread):
    """WebSocket client running in separate thread"""
    
    video_frame_received = pyqtSignal(bytes)
    audio_frame_received = pyqtSignal(np.ndarray, int)
    connection_status = pyqtSignal(str)
    stats_updated = pyqtSignal(dict)
    
    def __init__(self, host='192.168.1.82', port=5000):
        super().__init__()
        self.host = host
        self.port = port
        self.ws = None
        self.running = False
        self.stats = {
            'video_frames': 0,
            'audio_frames': 0,
            'bytes_received': 0,
            'fps': 0,
            'start_time': time.time()
        }
        self.last_frame_time = time.time()
        self.frame_times = deque(maxlen=30)
    
    def run(self):
        """Connect and receive data"""
        try:
            protocol = 'wss' if self.port == 5000 else 'ws'
            uri = f'{protocol}://{self.host}:{self.port}/ws'
            
            self.connection_status.emit("Connecting...")
            
            self.ws = websocket.WebSocketApp(
                uri,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            self.ws.run_forever(sslopt={'cert_reqs': 0})
        except Exception as e:
            self.connection_status.emit(f"Error: {str(e)}")
    
    def _on_open(self, ws):
        """Connected"""
        self.running = True
        self.connection_status.emit("✓ Connected")
        print("WebSocket connected!")
        
        # Send hello
        hello = json.dumps({'type': 'hello', 'receiver': 'desktop'})
        ws.send(hello)
    
    def _on_message(self, ws, message):
        """Receive message"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'video':
                self.stats['video_frames'] += 1
                video_data = data.get('data', '')
                if video_data:
                    self.video_frame_received.emit(video_data.encode())
                    self.frame_times.append(time.time())
                    
                    if len(self.frame_times) > 1:
                        fps = len(self.frame_times) / (self.frame_times[-1] - self.frame_times[0] + 0.001)
                        self.stats['fps'] = fps
                        
            elif msg_type == 'audio':
                self.stats['audio_frames'] += 1
                audio_field = data.get('data')
                sample_rate = int(data.get('sampleRate', 16000))
                
                if isinstance(audio_field, str):
                    try:
                        decoded = base64.b64decode(audio_field)
                        samples = np.frombuffer(decoded, dtype=np.float32)
                        self.audio_frame_received.emit(samples, sample_rate)
                    except:
                        pass
                elif isinstance(audio_field, list):
                    samples = np.array(audio_field, dtype=np.float32)
                    self.audio_frame_received.emit(samples, sample_rate)
            
            self.stats_updated.emit(self.stats.copy())
            
        except Exception as e:
            print(f"Message error: {e}")
    
    def _on_error(self, ws, error):
        """Error"""
        self.connection_status.emit(f"✗ Error: {str(error)}")
        print(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Disconnected"""
        self.running = False
        self.connection_status.emit("✗ Disconnected")
        print("WebSocket closed")
    
    def stop(self):
        """Stop receiving"""
        self.running = False
        if self.ws:
            self.ws.close()


class ReceiverGUI(QMainWindow):
    """Main GUI window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodeFlow - Desktop Receiver")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        
        # Initialize virtual devices
        self.virtual_manager = initialize_virtual_devices(video_width=1280, video_height=720, fps=30)
        self.virtual_manager.activate_audio_routing()
        
        self.init_ui()
        
        self.ws_worker = None
        self.audio_player = None
        self.current_frame = None
    
    def init_ui(self):
        """Initialize UI"""
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # LEFT: Video Display
        left_panel = QVBoxLayout()
        
        video_label = QLabel("Waiting for video...")
        video_label.setMinimumSize(800, 600)
        video_label.setMaximumWidth(900)
        video_label.setStyleSheet("""
            background-color: #000000;
            border: 2px solid #0d47a1;
            border-radius: 4px;
            color: #666666;
            font-size: 14px;
            font-weight: bold;
        """)
        video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label = video_label
        
        left_panel.addWidget(video_label)
        
        # Connection button
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_btn)
        button_layout.addStretch()
        left_panel.addLayout(button_layout)
        
        # RIGHT: Stats Panel
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📊 STATISTICS")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        right_panel.addWidget(title)
        
        # Status
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
        right_panel.addWidget(self.status_label)
        
        # Video Stats
        video_frame = QFrame()
        video_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-left: 4px solid #4CAF50;
                padding: 12px;
                border-radius: 4px;
            }
        """)
        video_layout = QVBoxLayout()
        
        video_title = QLabel("🎥 VIDEO")
        video_title.setStyleSheet("color: #4CAF50; font-weight: bold;")
        video_layout.addWidget(video_title)
        
        self.fps_label = QLabel("FPS: 0")
        self.video_frames_label = QLabel("Frames: 0")
        self.resolution_label = QLabel("Resolution: --")
        video_layout.addWidget(self.fps_label)
        video_layout.addWidget(self.video_frames_label)
        video_layout.addWidget(self.resolution_label)
        video_frame.setLayout(video_layout)
        right_panel.addWidget(video_frame)
        
        # Audio Stats
        audio_frame = QFrame()
        audio_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-left: 4px solid #2196F3;
                padding: 12px;
                border-radius: 4px;
            }
        """)
        audio_layout = QVBoxLayout()
        
        audio_title = QLabel("🎵 AUDIO")
        audio_title.setStyleSheet("color: #2196F3; font-weight: bold;")
        audio_layout.addWidget(audio_title)
        
        self.audio_frames_label = QLabel("Frames: 0")
        self.sample_rate_label = QLabel("Sample Rate: --")
        self.audio_level_label = QLabel("Level: █░░░░░░░░")
        audio_layout.addWidget(self.audio_frames_label)
        audio_layout.addWidget(self.sample_rate_label)
        audio_layout.addWidget(self.audio_level_label)
        audio_frame.setLayout(audio_layout)
        right_panel.addWidget(audio_frame)
        
        # Network Stats
        network_frame = QFrame()
        network_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-left: 4px solid #FF9800;
                padding: 12px;
                border-radius: 4px;
            }
        """)
        network_layout = QVBoxLayout()
        
        network_title = QLabel("🌐 NETWORK")
        network_title.setStyleSheet("color: #FF9800; font-weight: bold;")
        network_layout.addWidget(network_title)
        
        self.bytes_label = QLabel("Bytes: 0 MB")
        self.uptime_label = QLabel("Uptime: 00:00")
        network_layout.addWidget(self.bytes_label)
        network_layout.addWidget(self.uptime_label)
        network_frame.setLayout(network_layout)
        right_panel.addWidget(network_frame)
        
        # Virtual Devices Status
        vdev_frame = QFrame()
        vdev_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-left: 4px solid #9C27B0;
                padding: 12px;
                border-radius: 4px;
            }
        """)
        vdev_layout = QVBoxLayout()
        
        vdev_title = QLabel("⚙️ VIRTUAL DEVICES")
        vdev_title.setStyleSheet("color: #9C27B0; font-weight: bold;")
        vdev_layout.addWidget(vdev_title)
        
        self.vcam_label = QLabel("Camera: ✗ Not Available")
        self.vaudio_label = QLabel("Audio: ✗ Not Available")
        vdev_layout.addWidget(self.vcam_label)
        vdev_layout.addWidget(self.vaudio_label)
        vdev_frame.setLayout(vdev_layout)
        right_panel.addWidget(vdev_frame)
        
        right_panel.addStretch()
        
        # Add panels to main layout
        left_container = QWidget()
        left_container.setLayout(left_panel)
        
        right_container = QWidget()
        right_container.setLayout(right_panel)
        right_container.setMaximumWidth(400)
        right_container.setStyleSheet("background-color: #1a1a1a;")
        
        main_layout.addWidget(left_container, 1)
        main_layout.addWidget(right_container, 0)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Timer for stats update
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_uptime)
        self.stats_timer.start(1000)
        
        self.start_time = None
    
    def toggle_connection(self):
        """Connect/Disconnect"""
        if self.ws_worker and self.ws_worker.running:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        """Connect to server"""
        self.audio_player = AudioPlayer()
        
        self.ws_worker = WebSocketWorker('192.168.1.82', 5000)
        self.ws_worker.video_frame_received.connect(self.on_video_frame)
        self.ws_worker.audio_frame_received.connect(self.on_audio_frame)
        self.ws_worker.connection_status.connect(self.on_connection_status)
        self.ws_worker.stats_updated.connect(self.on_stats_updated)
        
        self.ws_worker.start()
        self.connect_btn.setText("Disconnect")
        self.start_time = time.time()
        
        # Update virtual devices status
        self.update_virtual_devices_status()
    
    def disconnect(self):
        """Disconnect from server"""
        if self.ws_worker:
            self.ws_worker.stop()
            self.ws_worker.wait()
        
        if self.audio_player:
            self.audio_player.stop()
        
        self.connect_btn.setText("Connect")
        self.status_label.setText("Status: Disconnected")
        self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
        
        # Clean up virtual devices
        if self.virtual_manager:
            self.virtual_manager.cleanup()
    
    def update_virtual_devices_status(self):
        """Update virtual devices status display"""
        vcam_info = self.virtual_manager.get_virtual_camera_info()
        vaudio_info = self.virtual_manager.get_virtual_audio_info()
        
        if vcam_info['available']:
            self.vcam_label.setText(f"Camera: ✓ {vcam_info['device']}")
            self.vcam_label.setStyleSheet("color: #4CAF50;")
        else:
            self.vcam_label.setText("Camera: ✗ Not Available")
            self.vcam_label.setStyleSheet("color: #ff6b6b;")
        
        if vaudio_info['available']:
            self.vaudio_label.setText(f"Audio: ✓ {vaudio_info['device_name']}")
            self.vaudio_label.setStyleSheet("color: #4CAF50;")
        else:
            self.vaudio_label.setText("Audio: ✗ Not Available")
            self.vaudio_label.setStyleSheet("color: #ff6b6b;")
    
    def on_video_frame(self, frame_data):
        """Display video frame and send to virtual camera"""
        try:
            image_data = base64.b64decode(frame_data)
            image = QImage.fromData(image_data)
            
            if not image.isNull():
                # Scale to fit label
                pixmap = QPixmap.fromImage(image)
                scaled = pixmap.scaledToWidth(
                    self.video_label.width() - 4,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.video_label.setPixmap(scaled)
                
                self.resolution_label.setText(f"Resolution: {image.width()}x{image.height()}")
                self.current_frame = scaled
                
                # Send to virtual camera
                try:
                    # Convert QImage to numpy array for virtual camera
                    width = image.width()
                    height = image.height()
                    ptr = image.bits()
                    ptr.setsize(image.byteCount())
                    arr = np.array(ptr).reshape(height, width, 4)  # RGBA
                    frame_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
                    
                    # Send to virtual camera
                    self.virtual_manager.send_video_frame(frame_bgr)
                except Exception as e:
                    pass  # Silent fail, virtual camera is optional
        except Exception as e:
            print(f"Video frame error: {e}")
    
    def on_audio_frame(self, samples, sample_rate):
        """Play audio frame"""
        try:
            # Ensure audio player uses the incoming sample rate
            if not self.audio_player or getattr(self.audio_player, 'sample_rate', None) != int(sample_rate):
                # Recreate audio player with correct sample rate
                try:
                    if self.audio_player:
                        self.audio_player.stop()
                except Exception:
                    pass
                self.audio_player = AudioPlayer(sample_rate=int(sample_rate), channels=1)

            if self.audio_player:
                self.audio_player.put(samples)
                
                # Update audio level visualization
                if len(samples) > 0:
                    level = int(abs(np.max(samples)) * 10)
                    level = min(level, 10)
                    bar = "█" * level + "░" * (10 - level)
                    self.audio_level_label.setText(f"Level: {bar}")
                
                self.sample_rate_label.setText(f"Sample Rate: {sample_rate} Hz")
        except Exception as e:
            print(f"Audio error: {e}")
    
    def on_connection_status(self, status):
        """Update connection status"""
        self.status_label.setText(f"Status: {status}")
        
        if "Connected" in status:
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
        else:
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
    
    def on_stats_updated(self, stats):
        """Update statistics"""
        self.fps_label.setText(f"FPS: {stats.get('fps', 0):.1f}")
        self.video_frames_label.setText(f"Frames: {stats.get('video_frames', 0)}")
        self.audio_frames_label.setText(f"Frames: {stats.get('audio_frames', 0)}")
        
        bytes_mb = stats.get('bytes_received', 0) / (1024 * 1024)
        self.bytes_label.setText(f"Bytes: {bytes_mb:.2f} MB")
    
    def update_uptime(self):
        """Update uptime"""
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.uptime_label.setText(f"Uptime: {minutes:02d}:{seconds:02d}")
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.disconnect()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = ReceiverGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
