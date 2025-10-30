import platform
import logging
import threading
import queue
from pathlib import Path
from typing import Optional
import time

logger = logging.getLogger(__name__)

class AudioHandler:
    def __init__(self):
        self.system = platform.system()
        self.recording: bool = False
        self.playback_active: bool = False
        self._audio_queue = queue.Queue()
        self._setup_audio()
        
    def _setup_audio(self):
        """Initialize audio backend based on platform"""
        try:
            if self.system == "Windows":
                from playsound3 import playsound
                self.play_audio = playsound
            elif self.system == "Linux":
                import vlc
                self.player = vlc.MediaPlayer()
                def vlc_play(file_path):
                    self.player.set_mrl(str(file_path))
                    self.player.play()
                self.play_audio = vlc_play
            elif self.system == "Darwin":  # macOS
                import subprocess
                def afplay(file_path):
                    subprocess.run(['afplay', str(file_path)])
                self.play_audio = afplay
        except Exception as e:
            logger.error(f"Failed to initialize audio system: {e}")
            def dummy_play(file_path):
                logger.warning("Audio playback not available")
            self.play_audio = dummy_play

    def start_recording(self, output_path: Path):
        """Start recording audio"""
        if self.recording:
            return False
            
        try:
            import sounddevice as sd
            self.recording = True
            self.audio_data = []
            
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio input status: {status}")
                if self.recording:
                    self.audio_data.extend(indata.copy())
                    
            self.stream = sd.InputStream(
                channels=1,
                samplerate=44100,
                callback=callback
            )
            self.stream.start()
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.recording = False
            return False
            
    def stop_recording(self, output_path: Optional[Path] = None):
        """Stop recording and optionally save to file"""
        if not self.recording:
            return False
            
        try:
            self.recording = False
            self.stream.stop()
            self.stream.close()
            
            if output_path and self.audio_data:
                audio_array = np.array(self.audio_data)
                wavio.write(
                    str(output_path),
                    audio_array,
                    44100,
                    sampwidth=2
                )
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return False
            
    def play_file(self, file_path: Path):
        """Play audio file using platform-specific method"""
        if self.playback_active:
            return False
            
        try:
            self.playback_active = True
            
            def play_thread():
                try:
                    self.play_audio(str(file_path))
                finally:
                    self.playback_active = False
                    
            threading.Thread(target=play_thread, daemon=True).start()
            return True
            
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
            self.playback_active = False
            return False
            
    def stop_playback(self):
        """Stop current playback"""
        if not self.playback_active:
            return False
            
        try:
            if self.system == "Linux" and hasattr(self, 'player'):
                self.player.stop()
            self.playback_active = False
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop playback: {e}")
            return False

# Usage example:
# audio = AudioHandler()
# 
# # Recording
# audio.start_recording(Path("output.wav"))
# time.sleep(5)  # Record for 5 seconds
# audio.stop_recording()
# 
# # Playback
# audio.play_file(Path("output.wav"))
# time.sleep(2)
# audio.stop_playback()
