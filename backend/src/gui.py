import tkinter as tk
from tkinter import ttk, messagebox
import threading
import cv2
import pyaudio
import json
import logging
from PIL import Image, ImageTk
import websockets
import asyncio
import base64
import os
import socket
import sys
from pathlib import Path


class NodeFlowGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NodeFlow")
        self.root.geometry("800x600")

        # Initialize logger
        self.logger = logging.getLogger(__name__)

        # Connection variables
        self.ws = None
        self.connected = False
        self.server_url = None
        self.ws_loop = None
        self.ws_thread = None

        # Video variables
        self.video_capture = None
        self.is_streaming = False

        # Audio variables
        self.audio = pyaudio.PyAudio()
        self.audio_stream = None
        self.is_audio_streaming = False

        self.setup_gui()

    def setup_gui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Status frame
        self.status_frame = ttk.LabelFrame(
            self.main_frame, text="Connection Status", padding="5"
        )
        self.status_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )

        self.status_label = ttk.Label(
            self.status_frame, text="Disconnected", foreground="red"
        )
        self.status_label.grid(row=0, column=0, padx=5)

        self.connect_btn = ttk.Button(
            self.status_frame, text="Connect", command=self.toggle_connection
        )
        self.connect_btn.grid(row=0, column=1, padx=5)

        # Server URL entry
        ttk.Label(self.status_frame, text="Server URL:").grid(
            row=1, column=0, padx=5, sticky=tk.W
        )
        self.url_entry = ttk.Entry(self.status_frame, width=40)
        self.url_entry.insert(0, "wss://localhost:5000")
        self.url_entry.grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E))

        # Video frame
        self.video_frame = ttk.LabelFrame(
            self.main_frame, text="Video Preview", padding="5"
        )
        self.video_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )

        self.video_label = ttk.Label(self.video_frame, text="No video stream")
        self.video_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Controls frame
        self.controls_frame = ttk.LabelFrame(
            self.main_frame, text="Controls", padding="5"
        )
        self.controls_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )

        self.stream_btn = ttk.Button(
            self.controls_frame,
            text="Start Video",
            command=self.toggle_stream,
            state="disabled",
        )
        self.stream_btn.grid(row=0, column=0, padx=5)

        self.audio_btn = ttk.Button(
            self.controls_frame,
            text="Start Audio",
            command=self.toggle_audio,
            state="disabled",
        )
        self.audio_btn.grid(row=0, column=1, padx=5)

        # Make the window resizable
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

    def toggle_connection(self):
        if not self.connected:
            self.server_url = self.url_entry.get().strip()
            if not self.server_url:
                messagebox.showerror("Error", "Please enter a server URL")
                return

            # Start websocket in separate thread with its own event loop
            self.ws_thread = threading.Thread(
                target=self._run_websocket_thread, daemon=True
            )
            self.ws_thread.start()
        else:
            self._disconnect()

    def _run_websocket_thread(self):
        """Run websocket connection in a separate thread with its own event loop"""
        self.ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_loop)
        try:
            self.ws_loop.run_until_complete(self._connect_websocket())
        except Exception as e:
            self.logger.error(f"Websocket thread error: {e}")
            self.root.after(
                0, lambda: self._update_status("Disconnected", "red", "Connect")
            )

    async def _connect_websocket(self):
        try:
            import ssl

            ssl_context = ssl._create_unverified_context()
            self.ws = await websockets.connect(self.server_url, ssl=ssl_context)
            self.connected = True

            # Update GUI from main thread
            self.root.after(
                0, lambda: self._update_status("Connected", "green", "Disconnect")
            )
            self.root.after(0, lambda: self._enable_controls(True))
            self.logger.info("Connected to server")

            # Start listening for messages
            await self._message_handler()
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
            self.root.after(
                0, lambda: self._update_status("Connection Failed", "red", "Connect")
            )

    async def _message_handler(self):
        try:
            while self.connected and self.ws:
                message = await self.ws.recv()
                data = json.loads(message)
                self.logger.debug(f"Received: {data}")

                # Handle different message types
                if data.get("type") == "error":
                    self.logger.error(f"Server error: {data.get('message')}")
                    self.root.after(
                        0,
                        lambda msg=data.get("message"): messagebox.showerror(
                            "Server Error", msg
                        ),
                    )
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Connection closed")
            self.connected = False
            self.root.after(
                0, lambda: self._update_status("Disconnected", "red", "Connect")
            )
            self.root.after(0, lambda: self._enable_controls(False))
        except Exception as e:
            self.logger.error(f"Message handler error: {e}")

    def _disconnect(self):
        """Disconnect from websocket"""
        self.connected = False
        if self.ws_loop and self.ws:
            asyncio.run_coroutine_threadsafe(self.ws.close(), self.ws_loop)
        self._update_status("Disconnected", "red", "Connect")
        self._enable_controls(False)

    def _update_status(self, text, color, button_text):
        """Update connection status in GUI"""
        self.status_label.config(text=text, foreground=color)
        self.connect_btn.config(text=button_text)

    def _enable_controls(self, enabled):
        """Enable or disable control buttons"""
        state = "normal" if enabled else "disabled"
        self.stream_btn.config(state=state)
        self.audio_btn.config(state=state)

    def toggle_stream(self):
        if not self.is_streaming:
            self.start_video_stream()
            self.stream_btn.config(text="Stop Video")
        else:
            self.stop_video_stream()
            self.stream_btn.config(text="Start Video")

    def start_video_stream(self):
        try:
            if self.video_capture is None:
                self.video_capture = cv2.VideoCapture(0)
                if not self.video_capture.isOpened():
                    raise Exception("Could not open webcam")

            self.is_streaming = True
            threading.Thread(target=self.update_video, daemon=True).start()
            self.logger.info("Video stream started")
        except Exception as e:
            self.logger.error(f"Error starting video: {e}")
            messagebox.showerror("Video Error", f"Could not start video: {e}")
            self.video_capture = None

    def stop_video_stream(self):
        self.is_streaming = False
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        self.video_label.config(image="", text="No video stream")
        self.logger.info("Video stream stopped")

    def update_video(self):
        while self.is_streaming:
            if self.video_capture is None:
                break

            ret, frame = self.video_capture.read()
            if ret:
                # Convert to RGB for PIL
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Resize for display
                display_size = (640, 480)
                image = Image.fromarray(frame_rgb)
                image.thumbnail(display_size, Image.Resampling.LANCZOS)

                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image=image)

                # Update label in main thread
                self.root.after(0, lambda p=photo: self._update_video_label(p))

                # Send frame to server if connected
                if self.connected and self.ws:
                    self._send_video_frame(frame)
            else:
                self.logger.warning("Failed to read frame from webcam")
                break

    def _update_video_label(self, photo):
        """Update video label with new frame"""
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo

    def _send_video_frame(self, frame):
        """Send video frame to server via websocket"""
        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()
            frame_b64 = base64.b64encode(frame_bytes).decode("utf-8")

            # Send as JSON message
            message = json.dumps({"type": "video_frame", "data": frame_b64})

            if self.ws_loop:
                asyncio.run_coroutine_threadsafe(self.ws.send(message), self.ws_loop)
        except Exception as e:
            self.logger.error(f"Error sending video frame: {e}")

    def toggle_audio(self):
        if not self.is_audio_streaming:
            self.start_audio_stream()
            self.audio_btn.config(text="Stop Audio")
        else:
            self.stop_audio_stream()
            self.audio_btn.config(text="Start Audio")

    def start_audio_stream(self):
        try:
            if self.audio_stream is None:
                self.audio_stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024,
                )
            self.is_audio_streaming = True
            threading.Thread(target=self.stream_audio, daemon=True).start()
            self.logger.info("Audio stream started")
        except Exception as e:
            self.logger.error(f"Error starting audio: {e}")
            messagebox.showerror("Audio Error", f"Could not start audio: {e}")

    def stop_audio_stream(self):
        self.is_audio_streaming = False
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except Exception as e:
                self.logger.error(f"Error stopping audio: {e}")
            finally:
                self.audio_stream = None
        self.logger.info("Audio stream stopped")

    def stream_audio(self):
        while self.is_audio_streaming:
            if self.audio_stream is None:
                break
            try:
                data = self.audio_stream.read(1024, exception_on_overflow=False)

                # Send to server if connected
                if self.connected and self.ws and self.ws_loop:
                    # Encode audio data as base64
                    audio_b64 = base64.b64encode(data).decode("utf-8")
                    message = json.dumps({"type": "audio_data", "data": audio_b64})

                    asyncio.run_coroutine_threadsafe(
                        self.ws.send(message), self.ws_loop
                    )
            except Exception as e:
                self.logger.error(f"Audio streaming error: {e}")
                break

    def on_closing(self):
        """Clean up resources when closing"""
        self.logger.info("Shutting down...")

        # Stop streams
        self.stop_video_stream()
        self.stop_audio_stream()

        # Terminate audio
        if self.audio:
            try:
                self.audio.terminate()
            except Exception as e:
                self.logger.error(f"Error terminating audio: {e}")

        # Disconnect websocket
        if self.connected:
            self._disconnect()

        # Stop event loop
        if self.ws_loop:
            self.ws_loop.call_soon_threadsafe(self.ws_loop.stop)

        self.root.destroy()


def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    # Setup logging
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "gui.log"),
            logging.StreamHandler(),
        ],
    )

    root = tk.Tk()
    app = NodeFlowGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
