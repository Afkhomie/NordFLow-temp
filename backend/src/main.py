import asyncio
import logging
import ssl
import os
from streaming.server_new import StreamingServer

async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    cert_file = os.path.join(os.path.dirname(__file__), 'server.crt')
    key_file = os.path.join(os.path.dirname(__file__), 'server.key')
    
    ssl_context = None
    if os.path.exists(cert_file) and os.path.exists(key_file):
        try:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_file, key_file)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            logger.info("SSL certificates loaded successfully")
        except Exception as e:
            logger.error(f"Error loading SSL certificates: {e}")
            ssl_context = None
    
    if ssl_context is None:
        logger.warning("SSL certificates not found or invalid, generating new ones...")
        from generate_cert import generate_self_signed_cert
        generate_self_signed_cert()
        try:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_file, key_file)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            logger.info("New SSL certificates generated and loaded successfully")
        except Exception as e:
            logger.error(f"Error loading new SSL certificates: {e}")
            ssl_context = None
    server = StreamingServer()
    try:
        logger.info("Starting server...")
        logger.info("=" * 50)
        logger.info("IMPORTANT: On your phone, you MUST:")
        logger.info("1. Visit https://192.168.1.82:5000 and accept the security warning")
        logger.info("2. Grant camera/microphone permissions when prompted")
        logger.info("=" * 50)
        await server.run(
            host='0.0.0.0',
            port=5000,
            ssl_context=ssl_context
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
