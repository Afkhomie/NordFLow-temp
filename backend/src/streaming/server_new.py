import asyncio
import logging
import json
import socket
import os
from aiohttp import web
import aiohttp
import ssl

from services.hardware_service import HardwareService
from utils.security import SecurityManager


class StreamingServer:
    def __init__(self, hardware_service: HardwareService = None, security_manager: SecurityManager = None):
        self.app = web.Application()
        self.logger = logging.getLogger(__name__)
        self.app.on_response_prepare.append(self._on_prepare_response)
        
        # Track all connected clients
        self.connected_clients = set()
        self.clients_lock = asyncio.Lock()

        # Add middleware to log incoming HTTP requests
        @web.middleware
        async def request_logger_middleware(request, handler):
            try:
                self.logger.info(f"HTTP {request.remote} {request.method} {request.path}")
            except Exception:
                self.logger.info(f"HTTP {request.method} {request.path}")
            resp = await handler(request)
            try:
                self.logger.info(f"HTTP Response: {resp.status} for {request.path}")
            except Exception:
                pass
            return resp

        self.app.middlewares.append(request_logger_middleware)

        # Inject or create services
        self.hardware_service = hardware_service or HardwareService()
        self.security_manager = security_manager or SecurityManager()

        # If running locally with no explicit permissions, grant short-lived permissions
        try:
            for _dev in ("webcam", "microphone", "speaker"):
                if not self.security_manager.check_permission(_dev):
                    self.security_manager.grant_permission(_dev, duration_hours=24)
        except Exception:
            # If permission storage fails, continue without blocking server startup
            self.logger.warning("Could not pre-grant device permissions; continuing")

        self.setup_routes()

    async def _on_prepare_response(self, request, response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With"
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"
        response.headers["Upgrade"] = request.headers.get("Upgrade", "")
        response.headers["Connection"] = request.headers.get("Connection", "")

    def setup_routes(self):
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/ws", self.handle_websocket)
        self.app.router.add_options("/ws", self.handle_options)
        # REST endpoint for device control (used by frontend)
        self.app.router.add_post("/api/device/{device}", self.handle_device_control)

    async def handle_options(self, request):
        response = web.Response(status=204)  # No content
        return response

    async def handle_index(self, request):
        try:
            index_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "templates", "index.html"
            )
            if os.path.exists(index_path):
                return web.FileResponse(index_path)
            else:
                self.logger.error(f"File not found: {index_path}")
                return web.Response(text="File not found", status=404)
        except Exception as e:
            self.logger.error(f"Error serving index.html: {e}")
            return web.Response(text="Internal server error", status=500)

    async def handle_device_control(self, request):
        """REST endpoint to start/stop devices from frontend"""
        device = request.match_info.get("device")
        try:
            data = await request.json()
        except Exception:
            data = {}

        command = data.get("command")
        if not command:
            return web.json_response({"status": "error", "message": "missing command"}, status=400)

        if not self.security_manager.validate_command(command, device):
            return web.json_response({"status": "error", "message": "unauthorized"}, status=403)

        loop = asyncio.get_event_loop()
        try:
            if command == "start":
                await loop.run_in_executor(None, self.hardware_service.start_device, device)
                return web.json_response({"status": "success", "message": f"{device} started"})
            elif command == "stop":
                await loop.run_in_executor(None, self.hardware_service.stop_device, device)
                return web.json_response({"status": "success", "message": f"{device} stopped"})
            else:
                return web.json_response({"status": "error", "message": "unknown command"}, status=400)
        except Exception as e:
            self.logger.error(f"Device control error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_websocket(self, request):
        self.logger.info(f"WebSocket connection attempt from {request.remote}")
        ws = None
        client_id = f"{request.remote}-{id(request)}"

        try:
            ws = web.WebSocketResponse(heartbeat=30)
            await ws.prepare(request)
            self.logger.info("WebSocket connection established")
            
            # Add to connected clients
            async with self.clients_lock:
                self.connected_clients.add(ws)

            await ws.send_json(
                {
                    "type": "connection",
                    "status": "connected",
                    "message": "Connected to NodeFlow",
                }
            )

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        msg_type = data.get("type")

                        # Log message type (not full data to avoid spam)
                        if msg_type in ("video", "audio"):
                            self.logger.debug(f"Received {msg_type} frame from {request.remote}")
                        else:
                            self.logger.info(f"Received {msg_type} message from {request.remote}")

                        # Handle test messages
                        if msg_type == "test":
                            await ws.send_json({"type": "test_response", "message": "Test successful!"})

                        # Handle hello/connection init
                        elif msg_type == "hello":
                            client_type = data.get('receiver', data.get('client', 'unknown'))
                            self.logger.info(f"Client identified: {client_type}")
                            await ws.send_json({
                                "type": "connection",
                                "status": "ready",
                                "message": "Ready to receive streams"
                            })

                        # Handle video stream (base64 encoded JPEG)
                        elif msg_type == "video":
                            video_data = data.get("data")
                            if video_data:
                                self.logger.debug(f"Video frame size: {len(video_data)} bytes")
                                # Broadcast to all other connected clients (desktop receivers)
                                await self._broadcast_to_receivers(data, request.remote)

                        # Handle audio stream
                        elif msg_type == "audio":
                            audio_data = data.get("data")
                            sample_rate = data.get("sampleRate", 16000)
                            if audio_data:
                                self.logger.debug(f"Audio frame: sample rate {sample_rate}Hz")
                                # Broadcast to all other connected clients
                                await self._broadcast_to_receivers(data, request.remote)

                        # Handle device control via websocket
                        elif msg_type == "device":
                            command = data.get("command")
                            device = data.get("device")
                            if not self.security_manager.validate_command(command, device):
                                await ws.send_json({"status": "error", "message": "unauthorized"})
                            else:
                                loop = asyncio.get_event_loop()
                                if command == "start":
                                    await loop.run_in_executor(None, self.hardware_service.start_device, device)
                                    await ws.send_json({"status": "success", "message": f"{device} started"})
                                elif command == "stop":
                                    await loop.run_in_executor(None, self.hardware_service.stop_device, device)
                                    await ws.send_json({"status": "success", "message": f"{device} stopped"})

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON from {request.remote}: {e}")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    self.logger.error(f"WebSocket error from {request.remote}: {ws.exception()}")
                    break
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            # Remove from connected clients
            async with self.clients_lock:
                self.connected_clients.discard(ws)
            if ws and not ws.closed:
                await ws.close()
            return ws
    
    async def _broadcast_to_receivers(self, data, sender_ip):
        """Broadcast video/audio to all connected receiver clients"""
        async with self.clients_lock:
            dead_clients = []
            for client_ws in self.connected_clients:
                # Don't send back to sender
                if client_ws.get_extra_info('peername')[0] == sender_ip:
                    continue
                
                try:
                    await client_ws.send_json(data)
                except Exception as e:
                    self.logger.debug(f"Failed to send to client: {e}")
                    dead_clients.append(client_ws)
            
            # Remove dead clients
            for client in dead_clients:
                self.connected_clients.discard(client)

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    async def run(self, host="0.0.0.0", port=5000, ssl_context=None):
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, host, port, ssl_context=ssl_context)

            local_ip = self.get_local_ip()
            protocol = "https" if ssl_context else "http"
            self.logger.info(f"Starting server on {host}:{port}")
            self.logger.info(f"Access at: {protocol}://{local_ip}:{port}")

            await site.start()

            while True:
                await asyncio.sleep(3600)

        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise
