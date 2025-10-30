import json
import logging
import asyncio
import websockets
from models.device import Device
from utils.security import SecurityManager

class DeviceController:
    def __init__(self, hardware_service, security_manager):
        self.hardware_service = hardware_service
        self.security_manager = security_manager
        self.connected_clients = set()
        self.logger = logging.getLogger(__name__)
        
    async def start_server(self, host='0.0.0.0', port=8765):
        """Start the WebSocket server"""
        self.server = await websockets.serve(
            self.handle_connection,
            host,
            port,
            process_request=self.security_manager.process_request
        )
        self.logger.info(f"WebSocket server started on ws://{host}:{port}")
        await self.server.wait_closed()
        
    async def handle_connection(self, websocket, path):
        """Handle incoming WebSocket connections"""
        try:
            # Add client to connected set
            self.connected_clients.add(websocket)
            self.logger.info("New client connected")
            
            async for message in websocket:
                try:
                    await self.process_message(websocket, message)
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    await self.send_error(websocket, str(e))
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Client disconnected")
        finally:
            self.connected_clients.remove(websocket)
            
    async def process_message(self, websocket, message):
        """Process incoming messages from clients"""
        data = json.loads(message)
        command = data.get('command')
        device_type = data.get('device')
        
        if not self.security_manager.validate_command(command, device_type):
            raise ValueError("Invalid command or unauthorized access")
            
        if command == 'start':
            await self.hardware_service.start_device(device_type)
            await self.send_response(websocket, {
                'status': 'success',
                'message': f'{device_type} started'
            })
        elif command == 'stop':
            await self.hardware_service.stop_device(device_type)
            await self.send_response(websocket, {
                'status': 'success',
                'message': f'{device_type} stopped'
            })
            
    async def send_response(self, websocket, data):
        """Send response to client"""
        await websocket.send(json.dumps(data))
        
    async def send_error(self, websocket, error_message):
        """Send error message to client"""
        await websocket.send(json.dumps({
            'status': 'error',
            'message': error_message
        }))
