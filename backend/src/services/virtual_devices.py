"""
Virtual Devices Manager
Handles virtual camera and microphone setup for Windows
Integrates pyvirtualcam for video and routes audio to virtual cable
"""

import logging
import threading
import cv2
import numpy as np
import sounddevice as sd
from typing import Optional, Tuple
from pathlib import Path

try:
    import pyvirtualcam
    PYVIRTUALCAM_AVAILABLE = True
except ImportError:
    PYVIRTUALCAM_AVAILABLE = False

logger = logging.getLogger(__name__)


class VirtualCameraManager:
    """Manages virtual camera device"""
    
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.camera = None
        self.is_active = False
        self.lock = threading.Lock()
        
        if not PYVIRTUALCAM_AVAILABLE:
            logger.warning("pyvirtualcam not installed. Virtual camera disabled.")
            return
        
        try:
            self.camera = pyvirtualcam.Camera(
                width=self.width,
                height=self.height,
                fps=self.fps,
                fmt=pyvirtualcam.PixelFormat.BGR
            )
            logger.info(f"✓ Virtual Camera initialized: {self.width}x{self.height} @ {self.fps}fps")
            logger.info(f"  Device: {self.camera.device}")
        except Exception as e:
            logger.error(f"✗ Failed to initialize virtual camera: {e}")
            logger.info("  Install OBS Virtual Camera: https://obsproject.com/forum/resources/obs-virtualcam.949/")
            self.camera = None
    
    def send_frame(self, frame: np.ndarray) -> bool:
        """
        Send frame to virtual camera
        
        Args:
            frame: numpy array in BGR format
            
        Returns:
            True if successful, False otherwise
        """
        if not self.camera or not PYVIRTUALCAM_AVAILABLE:
            return False
        
        try:
            with self.lock:
                # Ensure frame is BGR and correct size
                if frame.shape[:2] != (self.height, self.width):
                    frame = cv2.resize(frame, (self.width, self.height))
                
                if len(frame.shape) == 2:  # Grayscale
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                elif frame.shape[2] == 4:  # RGBA
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                elif frame.shape[2] == 3 and np.mean(frame[:,:,0]) > np.mean(frame[:,:,2]):  # RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                self.camera.send(frame)
                self.camera.sleep_until_next_frame()
                self.is_active = True
                return True
        except Exception as e:
            logger.debug(f"Virtual camera send error: {e}")
            return False
    
    def start(self) -> bool:
        """Start virtual camera"""
        if not self.camera:
            logger.warning("Virtual camera not initialized")
            return False
        
        try:
            self.is_active = True
            logger.info("Virtual camera started")
            return True
        except Exception as e:
            logger.error(f"Failed to start virtual camera: {e}")
            return False
    
    def stop(self):
        """Stop virtual camera"""
        if self.camera:
            try:
                self.camera.close()
                self.is_active = False
                logger.info("Virtual camera stopped")
            except Exception as e:
                logger.debug(f"Error stopping virtual camera: {e}")
    
    def __del__(self):
        """Cleanup"""
        self.stop()


class VirtualAudioRouter:
    """Routes audio to virtual cable/microphone"""
    
    def __init__(self):
        self.virtual_device_index = None
        self.device_name = None
        self.is_active = False
        self._detect_virtual_audio()
    
    def _detect_virtual_audio(self):
        """Detect virtual audio devices (VB-Cable, Virtual Audio Cable, etc.)"""
        try:
            devices = sd.query_devices()
            
            virtual_names = [
                'CABLE Input',  # VB-Audio Virtual Cable
                'VB-Audio Virtual Cable',
                'Virtual Audio Cable',
                'Stereo Mix',
                'Wave Out Mix',
                'What U Hear',
                'Listening to this device',
            ]
            
            for idx, device in enumerate(devices):
                device_name = device.get('name', '').lower()
                for virtual_name in virtual_names:
                    if virtual_name.lower() in device_name and device.get('max_input_channels', 0) > 0:
                        self.virtual_device_index = idx
                        self.device_name = device.get('name')
                        logger.info(f"✓ Virtual Audio Device detected: {self.device_name}")
                        return
            
            logger.warning("✗ No virtual audio device detected")
            logger.info("  Install VB-Cable: https://vb-audio.com/Cable/")
            
        except Exception as e:
            logger.error(f"Error detecting virtual audio devices: {e}")
    
    def get_device_index(self) -> Optional[int]:
        """Get virtual audio device index"""
        return self.virtual_device_index
    
    def get_device_name(self) -> Optional[str]:
        """Get virtual audio device name"""
        return self.device_name
    
    def is_available(self) -> bool:
        """Check if virtual audio device is available"""
        return self.virtual_device_index is not None
    
    def activate(self) -> bool:
        """Activate virtual audio routing"""
        if not self.is_available():
            logger.warning("Virtual audio device not available")
            return False
        
        try:
            sd.default.device = self.virtual_device_index
            self.is_active = True
            logger.info(f"✓ Audio routing activated to: {self.device_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to activate virtual audio routing: {e}")
            return False
    
    def deactivate(self):
        """Deactivate virtual audio routing"""
        self.is_active = False
        logger.info("Audio routing deactivated")


class VirtualDeviceManager:
    """
    Master manager for all virtual devices
    Coordinates virtual camera and audio routing
    """
    
    def __init__(self, video_width: int = 1280, video_height: int = 720, fps: int = 30):
        self.video_camera = VirtualCameraManager(width=video_width, height=video_height, fps=fps)
        self.audio_router = VirtualAudioRouter()
        self.is_enabled = PYVIRTUALCAM_AVAILABLE
        
        self._log_status()
    
    def _log_status(self):
        """Log initialization status"""
        logger.info("=" * 60)
        logger.info("Virtual Devices Status:")
        logger.info(f"  Virtual Camera: {'✓ Available' if self.video_camera.camera else '✗ Not Available'}")
        logger.info(f"  Virtual Audio:  {'✓ Available' if self.audio_router.is_available() else '✗ Not Available'}")
        logger.info("=" * 60)
    
    def send_video_frame(self, frame: np.ndarray) -> bool:
        """Send frame to virtual camera"""
        return self.video_camera.send_frame(frame)
    
    def activate_audio_routing(self) -> bool:
        """Activate virtual audio routing"""
        return self.audio_router.activate()
    
    def get_virtual_camera_info(self) -> dict:
        """Get virtual camera information"""
        return {
            'available': self.video_camera.camera is not None,
            'device': getattr(self.video_camera.camera, 'device', 'Unknown'),
            'width': self.video_camera.width,
            'height': self.video_camera.height,
            'fps': self.video_camera.fps,
            'active': self.video_camera.is_active
        }
    
    def get_virtual_audio_info(self) -> dict:
        """Get virtual audio information"""
        return {
            'available': self.audio_router.is_available(),
            'device_name': self.audio_router.device_name,
            'device_index': self.audio_router.virtual_device_index,
            'active': self.audio_router.is_active
        }
    
    def get_status(self) -> dict:
        """Get comprehensive status of all virtual devices"""
        return {
            'enabled': self.is_enabled,
            'video': self.get_virtual_camera_info(),
            'audio': self.get_virtual_audio_info()
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.video_camera.stop()
        self.audio_router.deactivate()
        logger.info("Virtual devices cleaned up")
    
    def __del__(self):
        """Destructor"""
        try:
            self.cleanup()
        except:
            pass


# Global instance
_virtual_manager: Optional[VirtualDeviceManager] = None


def get_virtual_manager() -> VirtualDeviceManager:
    """Get or create global virtual device manager"""
    global _virtual_manager
    if _virtual_manager is None:
        _virtual_manager = VirtualDeviceManager()
    return _virtual_manager


def initialize_virtual_devices(video_width: int = 1280, video_height: int = 720, fps: int = 30) -> VirtualDeviceManager:
    """Initialize virtual devices"""
    global _virtual_manager
    _virtual_manager = VirtualDeviceManager(video_width=video_width, video_height=video_height, fps=fps)
    return _virtual_manager
