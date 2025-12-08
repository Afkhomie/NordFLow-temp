"""
NodeFlow Desktop Receiver (Console Mode)
Alternative receiver that works in all environments (headless, SSH, GUI, etc.)
Displays video stats and audio playback information
Built with asyncio for cross-platform compatibility
"""

import sys
import json
import base64
import asyncio
import logging
from collections import deque
from datetime import datetime
import time

import numpy as np
import websocket
import sounddevice as sd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AudioPlayer:
    """Plays float32 PCM audio using sounddevice"""
    def __init__(self, sample_rate=16000, channels=1, blocksize=1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.blocksize = blocksize
        self.buffer = deque(maxlen=sample_rate * 10)  # 10 second buffer
        self.lock = False
        self.stream = None
        self.running = True
        
        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                blocksize=self.blocksize,
                callback=self._callback
            )
            self.stream.start()
            logger.info(f"Audio playback initialized: {sample_rate}Hz, {channels}ch")
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
                            logger.info(f"Audio playback initialized (device {i}, {use_ch}ch): {sample_rate}Hz")
                            break
                        except Exception:
                            continue
            except Exception:
                pass

            if not self.stream:
                logger.warning(f"Audio stream failed: {e}. Continuing without audio.")

    def _callback(self, outdata, frames, time_info, status):
        if status:
            logger.debug(f"Audio callback status: {status}")
        
        # Try to fill buffer
        samples_needed = frames * self.channels
        samples = []
        
        for _ in range(samples_needed):
            if self.buffer:
                samples.append(self.buffer.popleft())
            else:
                samples.append(0.0)  # Silence if buffer empty
        
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
            logger.debug(f"Audio buffer error: {e}")

    def stop(self):
        self.running = False
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
        except Exception as e:
            logger.debug(f"Audio stop error: {e}")


class ConsoleReceiver:
    """Console-based receiver for NodeFlow streams"""
    
    def __init__(self, host='192.168.1.82', port=5000):
        self.host = host
        self.port = port
        self.ws = None
        self.audio_player = None
        self.running = False
        
        # Statistics
        self.stats = {
            'frames_received': 0,
            'bytes_received': 0,
            'audio_frames': 0,
            'start_time': time.time(),
            'last_frame_time': time.time()
        }
        
    def connect(self):
        """Connect to WebSocket server"""
        protocol = 'wss' if self.port == 5000 else 'ws'
        uri = f'{protocol}://{self.host}:{self.port}/ws'
        
        logger.info(f"Connecting to {uri}...")
        
        try:
            self.ws = websocket.WebSocketApp(
                uri,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            self.running = True
            self.ws.run_forever(sslopt={'cert_reqs': 0})
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.running = False

    def _on_open(self, ws):
        logger.info("✓ WebSocket connected!")
        # Do not initialize audio player until we have sample rate from sender
        self.audio_player = None
        
        # Send hello
        try:
            self.ws.send(json.dumps({
                'type': 'hello',
                'client': 'console-receiver'
            }))
            logger.info("✓ Hello message sent")
        except Exception as e:
            logger.error(f"Failed to send hello: {e}")
        
        # Reset stats and show status
        self.stats['start_time'] = time.time()
        self._show_status()

    def _on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'video':
                self._handle_video(data)
            elif msg_type == 'audio':
                self._handle_audio(data)
            elif msg_type == 'connection':
                logger.info("✓ Connection confirmed by server")
                
        except Exception as e:
            logger.debug(f"Message error: {e}")

    def _handle_video(self, data):
        """Handle incoming video frame"""
        try:
            frame_data = base64.b64decode(data.get('data', ''))
            
            self.stats['frames_received'] += 1
            self.stats['bytes_received'] += len(frame_data)
            self.stats['last_frame_time'] = time.time()
            
            # Log every 30 frames
            if self.stats['frames_received'] % 30 == 0:
                elapsed = time.time() - self.stats['start_time']
                fps = self.stats['frames_received'] / elapsed if elapsed > 0 else 0
                mb = self.stats['bytes_received'] / (1024 * 1024)
                logger.info(
                    f"📹 Video: {self.stats['frames_received']} frames, "
                    f"{fps:.1f} FPS, {mb:.2f} MB received"
                )
        except Exception as e:
            logger.debug(f"Video error: {e}")

    def _handle_audio(self, data):
        """Handle incoming audio frame"""
        try:
            audio_field = data.get('data')
            sample_rate = int(data.get('sampleRate', 16000))
            samples = None
            
            if isinstance(audio_field, str):
                # Try base64 decode
                try:
                    decoded = base64.b64decode(audio_field)
                    samples = np.frombuffer(decoded, dtype=np.float32)
                except Exception:
                    samples = None
            elif isinstance(audio_field, list):
                samples = np.array(audio_field, dtype=np.float32)
            
            if samples is not None and samples.size > 0:
                # Ensure audio player sample rate matches incoming frames
                if not self.audio_player or getattr(self.audio_player, 'sample_rate', None) != int(sample_rate):
                    try:
                        if self.audio_player:
                            self.audio_player.stop()
                    except Exception:
                        pass
                    self.audio_player = AudioPlayer(sample_rate=int(sample_rate), channels=1)

                if self.audio_player:
                    self.audio_player.put(samples)
                
                self.stats['audio_frames'] += 1
                
                # Log every 30 audio frames
                if self.stats['audio_frames'] % 30 == 0:
                    logger.info(f"🎵 Audio: {self.stats['audio_frames']} frames received")
                    
        except Exception as e:
            logger.debug(f"Audio error: {e}")

    def _on_error(self, ws, error):
        logger.error(f"✗ WebSocket error: {error}")

    def _on_close(self, ws, close_status, close_msg):
        logger.info("✗ WebSocket disconnected")
        self.running = False
        if self.audio_player:
            self.audio_player.stop()

    def disconnect(self):
        """Disconnect from server"""
        if self.ws:
            self.ws.close()
        if self.audio_player:
            self.audio_player.stop()
        self.running = False

    def _show_status(self):
        """Display current status"""
        logger.info(f"Status: {'●' if self.running else '○'} Receiving")
        logger.info(f"Host: {self.host}:{self.port}")
        logger.info("Press Ctrl+C to stop")


def main():
    """Main entry point"""
    print("""
╔════════════════════════════════════════╗
║  NodeFlow - Console Receiver           ║
║  Real-time media streaming             ║
╚════════════════════════════════════════╝
""")
    
    receiver = ConsoleReceiver(host='192.168.1.82', port=5000)
    
    try:
        print("Starting receiver...")
        print()
        receiver.connect()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        receiver.disconnect()
        print("Goodbye!")
    except Exception as e:
        print(f"Error: {e}")
        receiver.disconnect()


if __name__ == '__main__':
    main()
