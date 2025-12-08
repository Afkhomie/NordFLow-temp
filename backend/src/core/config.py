import json
import os
import logging
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class NetworkConfig:
    host: str = "0.0.0.0"
    port: int = 5000
    use_ssl: bool = True
    ssl_cert: str = "server.crt"
    ssl_key: str = "server.key"
    force_https: bool = True
    max_connections: int = 1


@dataclass
class StreamConfig:
    video_width: int = 640
    video_height: int = 480
    video_fps: int = 20
    video_quality: int = 60
    audio_channels: int = 1
    audio_sample_rate: int = 44100
    audio_chunk_size: int = 1024
    buffer_size: int = 10


@dataclass
class Config:
    network: NetworkConfig = field(default_factory=NetworkConfig)
    stream: StreamConfig = field(default_factory=StreamConfig)
    log_level: str = "INFO"
    data_dir: str = "data"
    cert_path: Optional[str] = None
    key_path: Optional[str] = None


class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = Config()
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    data = json.load(f)

                # Update network config
                self.config.network = NetworkConfig(**data.get("network", {}))

                # Update stream config
                self.config.stream = StreamConfig(**data.get("stream", {}))

                # Update other configs
                self.config.log_level = data.get("log_level", self.config.log_level)
                self.config.data_dir = data.get("data_dir", self.config.data_dir)
                self.config.cert_path = data.get("cert_path", self.config.cert_path)
                self.config.key_path = data.get("key_path", self.config.key_path)

        except Exception as e:
            logger.error(f"Error loading config: {e}")

    def save_config(self):
        """Save configuration to file"""
        try:
            config_dict = {
                "network": {
                    "host": self.config.network.host,
                    "port": self.config.network.port,
                    "use_ssl": self.config.network.use_ssl,
                    "max_connections": self.config.network.max_connections,
                },
                "stream": {
                    "video_width": self.config.stream.video_width,
                    "video_height": self.config.stream.video_height,
                    "video_fps": self.config.stream.video_fps,
                    "video_quality": self.config.stream.video_quality,
                    "audio_channels": self.config.stream.audio_channels,
                    "audio_sample_rate": self.config.stream.audio_sample_rate,
                    "audio_chunk_size": self.config.stream.audio_chunk_size,
                    "buffer_size": self.config.stream.buffer_size,
                },
                "log_level": self.config.log_level,
                "data_dir": self.config.data_dir,
                "cert_path": self.config.cert_path,
                "key_path": self.config.key_path,
            }

            with open(self.config_path, "w") as f:
                json.dump(config_dict, f, indent=4)

        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def get_ssl_context(self):
        """Get SSL context if SSL is enabled"""
        if not (self.config.network.use_ssl or self.config.network.force_https):
            return None

        try:
            # Use configured paths or default to the src directory
            cert_path = self.config.cert_path or os.path.join(
                os.path.dirname(__file__), "..", self.config.network.ssl_cert
            )
            key_path = self.config.key_path or os.path.join(
                os.path.dirname(__file__), "..", self.config.network.ssl_key
            )

            # Generate certificates if they don't exist
            if not (os.path.exists(cert_path) and os.path.exists(key_path)):
                logger.info("SSL certificates not found. Generating new ones...")
                from generate_cert import generate_self_signed_cert

                generate_self_signed_cert()

            # Create and configure SSL context
            import ssl

            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_path, key_path)
            return ssl_context

        except Exception as e:
            logger.error(f"Error setting up SSL: {e}")
            if self.config.network.force_https:
                raise Exception("HTTPS is required but SSL setup failed") from e
            return None

    def ensure_directories(self):
        """Ensure required directories exist"""
        Path(self.config.data_dir).mkdir(parents=True, exist_ok=True)
