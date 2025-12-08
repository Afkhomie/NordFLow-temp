import cv2
import logging
from threading import Lock, Thread
import time
import queue
import numpy as np
import sounddevice as sd
from utils.audio_handler import AudioHandler


class HardwareService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.devices = {}
        self.locks = {"webcam": Lock(), "microphone": Lock(), "speaker": Lock()}
        self.running = False

    def get_device_status(self, device_type):
        """Get the status of a device"""
        device_name = device_type.value.lower()
        return "running" if device_name in self.devices else "stopped"

    def start_device(self, device_type):
        """Start a hardware device"""
        with self.locks[device_type]:
            # Check if device is already running and return success
            if device_type in self.devices:
                self.logger.info(f"{device_type} is already running")
                return

            try:
                if device_type == "webcam":
                    self._start_webcam()
                elif device_type == "microphone":
                    self._start_microphone()
                elif device_type == "speaker":
                    self._start_speaker()
                else:
                    raise ValueError(f"Unknown device type: {device_type}")

                self.logger.info(f"{device_type} started successfully")

            except Exception as e:
                self.logger.error(f"Error starting {device_type}: {e}")
                # Make sure device is not in running state if there was an error
                if device_type in self.devices:
                    del self.devices[device_type]
                raise

    def stop_device(self, device_type):
        """Stop a hardware device"""
        with self.locks[device_type]:
            # Check if device is already stopped and return success
            if device_type not in self.devices:
                self.logger.info(f"{device_type} is already stopped")
                return

            try:
                if device_type == "webcam":
                    self._stop_webcam()
                elif device_type == "microphone":
                    self._stop_microphone()
                elif device_type == "speaker":
                    self._stop_speaker()
                else:
                    raise ValueError(f"Unknown device type: {device_type}")

                del self.devices[device_type]
                self.logger.info(f"{device_type} stopped successfully")

            except Exception as e:
                self.logger.error(f"Error stopping {device_type}: {e}")
                # Make sure device is removed from running state even if there was an error
                if device_type in self.devices:
                    del self.devices[device_type]
                raise

    def _start_webcam(self):
        """Initialize and start webcam capture"""
        for index in range(2):
            try:
                cap = cv2.VideoCapture(index)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        self.devices["webcam"] = {
                            "device": cap,
                            "thread": Thread(target=self._webcam_thread),
                            "running": True,
                            "index": index,
                        }
                        self.devices["webcam"]["thread"].start()
                        self.logger.info(f"Successfully opened webcam at index {index}")
                        return
                    cap.release()
                else:
                    cap.release()
            except Exception as e:
                self.logger.error(f"Error trying camera index {index}: {e}")
                if cap:
                    cap.release()

        raise RuntimeError(
            "No working webcam found. Please check your camera connection."
        )

    def _start_microphone(self):
        """Initialize and start microphone capture"""
        self.devices["microphone"] = {
            "queue": queue.Queue(),
            "thread": Thread(target=self._microphone_thread),
            "running": True,
            "sample_rate": 44100,
            "channels": 1,
            "dtype": np.float32,
            "blocksize": 1024,
        }
        self.devices["microphone"]["thread"].start()

    def _start_speaker(self):
        """Initialize and start speaker output"""
        self.devices["speaker"] = {
            "queue": queue.Queue(),
            "thread": Thread(target=self._speaker_thread),
            "running": True,
            "sample_rate": 44100,
            "channels": 1,
            "dtype": np.float32,
            "blocksize": 1024,
        }
        self.devices["speaker"]["thread"].start()

    def _stop_webcam(self):
        """Stop webcam capture"""
        if "webcam" in self.devices:
            self.devices["webcam"]["running"] = False
            self.devices["webcam"]["thread"].join()
            self.devices["webcam"]["device"].release()

    def _stop_microphone(self):
        """Stop microphone capture"""
        if "microphone" in self.devices:
            self.devices["microphone"]["running"] = False
            self.devices["microphone"]["thread"].join()
            sd.stop()

    def _stop_speaker(self):
        """Stop speaker output"""
        if "speaker" in self.devices:
            self.devices["speaker"]["running"] = False
            self.devices["speaker"]["thread"].join()
            sd.stop()

    def _webcam_thread(self):
        """Webcam capture thread"""
        while self.devices["webcam"]["running"]:
            ret, frame = self.devices["webcam"]["device"].read()
            if ret:
                # Process frame here
                # For example, display it in a window
                cv2.imshow("NodeFlow Webcam", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        cv2.destroyAllWindows()

    def _microphone_thread(self):
        """Microphone capture thread"""
        device_info = self.devices["microphone"]

        def audio_callback(indata, frames, time, status):
            if status:
                self.logger.warning(f"Audio input status: {status}")
            device_info["queue"].put(indata.copy())

        try:
            with sd.InputStream(
                channels=device_info["channels"],
                samplerate=device_info["sample_rate"],
                blocksize=device_info["blocksize"],
                dtype=device_info["dtype"],
                callback=audio_callback,
            ):
                while device_info["running"]:
                    try:
                        device_info["queue"].get(timeout=1.0)
                    except queue.Empty:
                        continue

        except Exception as e:
            self.logger.error(f"Error in microphone thread: {e}")
            device_info["running"] = False

    def _speaker_thread(self):
        """Speaker output thread"""
        device_info = self.devices["speaker"]

        def audio_callback(outdata, frames, time, status):
            if status:
                self.logger.warning(f"Audio output status: {status}")

            try:
                # Generate a test tone (sine wave) if no data in queue
                t = np.linspace(0, frames / device_info["sample_rate"], frames)
                tone = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz test tone
                # Expand mono tone to match configured channels
                tone_col = tone.reshape(-1, 1)
                outdata[:] = np.tile(tone_col, (1, device_info["channels"]))
            except Exception as e:
                self.logger.error(f"Error generating audio: {e}")
                outdata.fill(0)

        try:
            with sd.OutputStream(
                channels=device_info["channels"],
                samplerate=device_info["sample_rate"],
                blocksize=device_info["blocksize"],
                dtype=device_info["dtype"],
                callback=audio_callback,
            ):
                while device_info["running"]:
                    time.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Error in speaker thread: {e}")
            device_info["running"] = False
