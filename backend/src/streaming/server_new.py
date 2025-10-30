import asyncio
import logging
import json
import socket
import os
from aiohttp import web
import aiohttp
import ssl

class StreamingServer:
    def __init__(self):
        self.app = web.Application()
        self.logger = logging.getLogger(__name__)
        self.app.on_response_prepare.append(self._on_prepare_response)
        self.setup_routes()
        
    async def _on_prepare_response(self, request, response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '86400'
        response.headers['Upgrade'] = request.headers.get('Upgrade', '')
        response.headers['Connection'] = request.headers.get('Connection', '')
        
    def setup_routes(self):
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/test', self.handle_test)
        self.app.router.add_get('/ws', self.handle_websocket)
        self.app.router.add_options('/ws', self.handle_options)
        
    async def handle_options(self, request):
        response = web.Response(status=204)  # No content
        return response
        
    async def handle_index(self, request):
        try:
            index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'index.html')
            if os.path.exists(index_path):
                return web.FileResponse(index_path)
            else:
                self.logger.error(f"File not found: {index_path}")
                return web.Response(text="File not found", status=404)
        except Exception as e:
            self.logger.error(f"Error serving index.html: {e}")
            return web.Response(text="Internal server error", status=500)
        
    async def handle_test(self, request):
        try:
            test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'test.html')
            if os.path.exists(test_path):
                return web.FileResponse(test_path)
            else:
                self.logger.error(f"File not found: {test_path}")
                return web.Response(text="File not found", status=404)
        except Exception as e:
            self.logger.error(f"Error serving test.html: {e}")
            return web.Response(text="Internal server error", status=500)
        
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
            
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        self.logger.info(f'Received: {data}')
                        
                        msg_type = data.get('type')
                        if msg_type == 'test':
                            await ws.send_json({
                                'type': 'test_response',
                                'message': 'Test successful!'
                            })
                    except json.JSONDecodeError as e:
                        self.logger.error(f'Invalid JSON: {e}')
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
                    break
        except Exception as e:
            self.logger.error(f'Error: {e}')
        finally:
            if ws and not ws.closed:
                await ws.close()
            return ws
            
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'
            
    async def run(self, host='0.0.0.0', port=5000, ssl_context=None):
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, host, port, ssl_context=ssl_context)
            
            local_ip = self.get_local_ip()
            protocol = "https" if ssl_context else "http"
            self.logger.info(f'Starting server on {host}:{port}')
            self.logger.info(f'Access at: {protocol}://{local_ip}:{port}')
            self.logger.info(f'Test page: {protocol}://{local_ip}:{port}/test')
            
            await site.start()
            
            while True:
                await asyncio.sleep(3600)
                
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise
