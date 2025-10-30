import asyncio
import logging
import json
import socket
from aiohttp import web
import aiohttp
import ssl

class StreamingServer:
    def __init__(self):
        self.app = web.Application()
        self.logger = logging.getLogger(__name__)
        
        # Enable CORS
        self.app.on_response_prepare.append(self._on_prepare_response)
        
        # Set up routes
        self.setup_routes()
        
    @web.middleware
    async def _handle_options(self, request, handler):
        if request.method == "OPTIONS":
            return web.Response(
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Access-Control-Max-Age": "3600",
                }
            )
        return await handler(request)

    async def _on_prepare_response(self, request, response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
    def setup_routes(self):
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/test', self.handle_test)
        self.app.router.add_get('/ws', self.handle_websocket)

    async def handle_test(self, request):
        return web.FileResponse('./templates/test.html')
        
    async def handle_index(self, request):
        return web.FileResponse('./templates/index.html')
        
    async def handle_websocket(self, request):
        self.logger.info(f"WebSocket connection attempt from {request.remote}")
        ws = None
        
        try:
            ws = web.WebSocketResponse(heartbeat=30)
            await ws.prepare(request)
            self.logger.info('WebSocket connection established')
            
            await ws.send_json({
                'type': 'connection',
                'status': 'connected',
                'message': 'Connected to NodeFlow'
            })
            
            # Handle incoming messages
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        self.logger.info(f'Received message: {msg.data}')
                        data = json.loads(msg.data)
                        msg_type = data.get('type')
                        msg_data = data.get('data')
                        
                        if msg_type == 'test':
                            await ws.send_json({
                                'type': 'test_response',
                                'message': 'Test successful!'
                            })
                        elif msg_type == 'video' and msg_data:
                            # Process video frame
                            await self.loop.run_in_executor(
                                self.executor,
                                self.video_processor.process_frame,
                                msg_data)
                        elif msg_type == 'audio' and msg_data:
                            # Process audio data
                            await self.loop.run_in_executor(
                                self.executor,
                                self.audio_processor.process_audio,
                                msg_data
                            )
                    except json.JSONDecodeError as e:
                        self.logger.error(f'Invalid JSON message: {e}')
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    self.logger.error(f'WebSocket connection closed with exception {ws.exception()}')
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    self.logger.info('WebSocket connection closed normally')
                    break
                    
        except Exception as e:
            self.logger.error(f'WebSocket error: {e}')
        finally:
            if ws and not ws.closed:
                await ws.close()
            self.logger.info('Cleaning up WebSocket connection')
            self.cleanup()
            self.logger.info('Client disconnected')
            return ws
            
    def cleanup(self):
        """Clean up resources"""
        self.video_processor.clear()
        self.audio_processor.clear()
        self.audio_processor.stop_playback()
        
    def get_local_ip(self):
        """Get the local IP address"""
        try:
            # Create a socket to determine the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))  # Doesn't actually send any packets
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            self.logger.error(f"Error getting local IP: {e}")
            return '127.0.0.1'

    async def run(self, host='0.0.0.0', port=5000, ssl_context=None):
        """Start the streaming server"""
        try:
            self.loop = asyncio.get_event_loop()
            
            # Configure the application
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            # Create the site with SSL if provided
            site = web.TCPSite(runner, host, port, ssl_context=ssl_context)
            
            # Get local IP and log access URL
            local_ip = self.get_local_ip()
            protocol = "https" if ssl_context else "http"
            self.logger.info(f'Starting server on {host}:{port}')
            self.logger.info(f'Access the server at: {protocol}://{local_ip}:{port}')
            
            # Start the site
            await site.start()
            self.logger.info("Server started successfully")
            
            # Keep the server running
            while True:
                await asyncio.sleep(3600)
                
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            if runner:
                await runner.cleanup()
            raise

if __name__ == "__main__":
    import asyncio
    server = StreamingServer()
    asyncio.run(server.run())
