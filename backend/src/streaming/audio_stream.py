import numpy as np
import logging
from queue import Queue
from threading import Thread, Event
from typing import Optional, Tuple, Any
from dataclasses import dataclass

# Try to import sounddevice, fallback to pyaudio if not available
try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except ImportError:
    try:
        import pyaudio
        HAS_SOUNDDEVICE = False
    except ImportError:
        HAS_SOUNDDEVICE = False
        pyaudio = None


@dataclass
class AudioConfig:
    channels: int = 1
    sample_rate: int = 44100
    chunk_size: int = 1024
    max_queue_size: int = 50
    target_latency: float = 0.1  # Target latency in seconds


class AudioStreamProcessor:
    def __init__(self, config: AudioConfig = AudioConfig()):
        self.config = config
        self.audio_queue = Queue(maxsize=config.max_queue_size)
        self.stopped = Event()
        self.logger = logging.getLogger(__name__)
        self.stream: Optional[sd.OutputStream] = None
        self.playback_thread: Optional[Thread] = None

    def start_playback(self):
        """Start audio playback thread"""
        if self.playback_thread is not None and self.playback_thread.is_alive():
            return

        try:
            if HAS_SOUNDDEVICE:
                try:
                    # Try default output device first
                    self.stream = sd.OutputStream(
                        channels=self.config.channels,
                        samplerate=self.config.sample_rate,
                        blocksize=self.config.chunk_size,
                        dtype=np.float32,
                    )
                    self.stream.start()
                except Exception:
                    # Fallback: scan devices for first working output device
                    devices = sd.query_devices()
                    for i, d in enumerate(devices):
                        max_out = int(d.get('max_output_channels', 0) or 0)
                        if max_out >= 1:
                            try:
                                ch = max(min(max_out, self.config.channels), 1)
                                self.stream = sd.OutputStream(
                                    channels=ch,
                                    samplerate=self.config.sample_rate,
                                    blocksize=self.config.chunk_size,
                                    dtype=np.float32,
                                    device=i
                                )
                                self.stream.start()
                                self.logger.info(f"Audio playback using device {i} ({d['name']})")
                                break
                            except Exception:
                                continue
            else:
                self.logger.warning("sounddevice not available, audio playback disabled")
                return

            self.stopped.clear()
            self.playback_thread = Thread(target=self._playback_worker)
            self.playback_thread.daemon = True
            self.playback_thread.start()

        except Exception as e:
            self.logger.error(f"Error starting audio playback: {str(e)}")

    def stop_playback(self):
        """Stop audio playback"""
        self.stopped.set()
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def _playback_worker(self):
        """Worker thread for audio playback"""
        while not self.stopped.is_set():
            try:
                if not self.audio_queue.empty() and self.stream is not None:
                    audio_data = self.audio_queue.get()
                    if isinstance(audio_data, np.ndarray):
                        self.stream.write(audio_data)
            except Exception as e:
                self.logger.error(f"Error in audio playback: {str(e)}")

    async def process_audio(self, audio_data: bytes) -> Tuple[bool, Any]:
        """Process incoming audio data from WebSocket"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)

            # Add to queue, drop oldest chunk if full
            if self.audio_queue.full():
                try:
                    self.audio_queue.get_nowait()
                except Exception:
                    pass

            self.audio_queue.put(audio_array)
            return True, None

        except Exception as e:
            self.logger.error(f"Error processing audio: {str(e)}")
            return False, str(e)

    def clear(self):
        """Clear audio queue"""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except Exception:
                pass
