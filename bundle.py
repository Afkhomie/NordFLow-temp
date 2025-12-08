"""
Bundle launcher that runs the StreamingServer (asyncio) in a background thread
and starts the desktop GUI in the main thread so we can build a single EXE.

This script is intended to be the PyInstaller entrypoint for the single `NodeFlow.exe`.
"""
import threading
import asyncio
import logging
import ssl
import sys
import time
from pathlib import Path

# Import server and GUI modules
# StreamingServer is in backend/src/streaming/server_new.py
# GUI main is backend/src/receiver_gui.py (main function)

try:
    from backend.src.streaming.server_new import StreamingServer
except Exception:
    # try alternative import path for bundled environment
    try:
        from streaming.server_new import StreamingServer
    except Exception:
        StreamingServer = None

try:
    from backend.src.receiver_gui import main as gui_main
except Exception:
    try:
        from receiver_gui import main as gui_main
    except Exception:
        gui_main = None


def start_server(loop, host='0.0.0.0', port=5000, ssl_context=None):
    """Run the asyncio server in the provided event loop."""
    if StreamingServer is None:
        logging.error('StreamingServer not available; server will not start')
        return

    server = StreamingServer()

    async def runner():
        try:
            await server.run(host=host, port=port, ssl_context=ssl_context)
        except Exception as e:
            logging.error(f'Server error: {e}')

    asyncio.set_event_loop(loop)
    loop.run_until_complete(runner())


def create_ssl_context():
    cert_file = Path(__file__).parent / 'backend' / 'src' / 'server.crt'
    key_file = Path(__file__).parent / 'backend' / 'src' / 'server.key'
    if cert_file.exists() and key_file.exists():
        try:
            ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ctx.load_cert_chain(str(cert_file), str(key_file))
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            logging.info('SSL context prepared')
            return ctx
        except Exception as e:
            logging.warning(f'Unable to create SSL context: {e}')
    return None


def run():
    logging.basicConfig(level=logging.INFO)
    logging.info('NodeFlow bundle starting')

    ssl_ctx = create_ssl_context()

    # Create a new event loop for the server thread
    server_loop = asyncio.new_event_loop()
    server_thread = threading.Thread(target=start_server, args=(server_loop, '0.0.0.0', 5000, ssl_ctx), daemon=True)
    server_thread.start()

    # Give server a moment to start
    time.sleep(0.5)

    # Start GUI in main thread
    if gui_main:
        try:
            sys.exit(gui_main())
        except TypeError:
            # gui_main may not return an exit code
            gui_main()
    else:
        logging.error('GUI main not available. Exiting.')


if __name__ == '__main__':
    run()
