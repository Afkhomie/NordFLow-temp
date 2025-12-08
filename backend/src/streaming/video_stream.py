import cv2
import numpy as np
import asyncio
import logging
import queue
from queue import Queue
from threading import Thread, Event
from typing import Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class VideoConfig:
    width: int = 640
    height: int = 480
    fps: int = 20
    quality: int = 60  # JPEG quality (0-100)
    max_queue_size: int = 10


class VideoStreamProcessor:
    def __init__(self, config: VideoConfig = VideoConfig()):
        self.config = config
        self.frame_queue = Queue(maxsize=config.max_queue_size)
        self.last_frame: Optional[np.ndarray] = None
        self.stopped = Event()
        self.logger = logging.getLogger(__name__)

        # Performance metrics
        self.fps_counter = 0
        self.fps_timer = asyncio.get_event_loop().time()
        self.current_fps = 0.0

    async def process_frame(self, frame_data: bytes) -> Tuple[bool, Any]:
        """Process incoming frame data from WebSocket"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                return False, "Invalid frame data"

            # Resize if needed
            if (
                frame.shape[1] != self.config.width
                or frame.shape[0] != self.config.height
            ):
                frame = cv2.resize(frame, (self.config.width, self.config.height))

            # Update FPS counter
            self.fps_counter += 1
            current_time = asyncio.get_event_loop().time()
            if current_time - self.fps_timer >= 1.0:
                self.current_fps = self.fps_counter
                self.fps_counter = 0
                self.fps_timer = current_time

            # Add to queue, drop oldest frame if full
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass

            self.frame_queue.put(frame)
            return True, None

        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
            return False, str(e)

    def encode_frame(self, frame: np.ndarray) -> Optional[bytes]:
        """Encode frame as JPEG"""
        try:
            # Encode frame as JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.config.quality]
            _, buffer = cv2.imencode(".jpg", frame, encode_param)
            return buffer.tobytes()
        except Exception as e:
            self.logger.error(f"Error encoding frame: {str(e)}")
            return None

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the latest frame from queue"""
        try:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get_nowait()
                self.last_frame = frame
                return frame
            return self.last_frame
        except Exception:
            return self.last_frame

    def get_current_fps(self) -> float:
        """Get current FPS"""
        return self.current_fps

    def clear(self):
        """Clear all queued frames"""
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                pass
