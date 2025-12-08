import asyncio
import logging
import ssl
import os
from pathlib import Path
from streaming.server_new import StreamingServer

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    server = StreamingServer()

    # Determine a friendly LAN IP to print for mobile connections
    def get_local_ip():
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '127.0.0.1'

    local_ip = get_local_ip()
    
    # Setup SSL context for HTTPS
    cert_file = Path(__file__).parent / 'server.crt'
    key_file = Path(__file__).parent / 'server.key'
    
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
    else:
        logger.warning(f"SSL certificates not found at {cert_file} or {key_file}")

    protocol = "https" if ssl_context else "http"
    logger.info(f"Starting dev server (listen on all interfaces) — access at: {protocol}://{local_ip}:5000/")
    logger.info(f"On your phone, open: {protocol}://{local_ip}:5000/")
    if ssl_context:
        logger.info("(You may see a certificate warning — that's normal for self-signed certs. Accept/Continue anyway.)")

    try:
        asyncio.run(server.run(host='0.0.0.0', port=5000, ssl_context=ssl_context))
    except KeyboardInterrupt:
        logger.info('Dev server stopped')
