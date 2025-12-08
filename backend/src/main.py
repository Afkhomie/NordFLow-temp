import asyncio
import logging
import ssl
import os
import sys
import socket
from pathlib import Path


async def main():
    # Setup logging
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "server.log"),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger(__name__)

    # Get certificate paths
    cert_dir = Path(__file__).parent
    cert_file = cert_dir / "server.crt"
    key_file = cert_dir / "server.key"

    # Get local IP address
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    local_ip = get_local_ip()

    # Setup SSL context
    ssl_context = None
    if cert_file.exists() and key_file.exists():
        try:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(str(cert_file), str(key_file))
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            logger.info("SSL certificates loaded successfully")
        except Exception as e:
            logger.error(f"Error loading SSL certificates: {e}")
            ssl_context = None

    # Generate certificates if needed
    if ssl_context is None:
        logger.warning("SSL certificates not found or invalid, generating new ones...")
        try:
            from generate_cert import generate_self_signed_cert

            generate_self_signed_cert()

            # Try loading again
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(str(cert_file), str(key_file))
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            logger.info("New SSL certificates generated and loaded successfully")
        except ImportError:
            logger.error(
                "generate_cert.py not found. Please create SSL certificates manually."
            )
            logger.info("You can create self-signed certificates with:")
            logger.info(
                "  openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes"
            )
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error generating/loading new SSL certificates: {e}")
            logger.info("Continuing without SSL (not recommended for production)")
            ssl_context = None

    # Import and start server
    try:
        from streaming.server_new import StreamingServer
    except ImportError as e:
        logger.error(
            f"Could not import StreamingServer. Error: {e}"
        )
        sys.exit(1)

    server = StreamingServer()

    try:
        logger.info("Starting NodeFlow server...")
        logger.info("=" * 70)
        logger.info("SERVER INFORMATION:")
        logger.info(f"  Local URL:    https://localhost:5000")
        logger.info(f"  Network URL:  https://{local_ip}:5000")
        logger.info("=" * 70)
        logger.info("IMPORTANT SETUP INSTRUCTIONS:")
        logger.info("  1. On your client device, visit the URL above")
        logger.info("  2. Accept the security warning (self-signed certificate)")
        logger.info("  3. Grant camera/microphone permissions when prompted")
        logger.info("=" * 70)
        logger.info("Press Ctrl+C to stop the server")
        logger.info("")

        await server.run(host="0.0.0.0", port=5000, ssl_context=ssl_context)
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except OSError as e:
        if e.errno == 98 or e.errno == 48:
            logger.error(
                "Port 5000 is already in use. Please stop the other process or use a different port."
            )
        else:
            logger.error(f"OS error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
