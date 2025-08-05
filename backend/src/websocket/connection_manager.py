from typing import Dict, List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Store active connections by flow_id
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, flow_id: str):
        await websocket.accept()
        
        if flow_id not in self.active_connections:
            self.active_connections[flow_id] = []
        
        self.active_connections[flow_id].append(websocket)
        logger.info(f"Client connected to flow {flow_id}")

    def disconnect(self, websocket: WebSocket, flow_id: str):
        if flow_id in self.active_connections:
            if websocket in self.active_connections[flow_id]:
                self.active_connections[flow_id].remove(websocket)
            
            # Clean up empty flow connections
            if not self.active_connections[flow_id]:
                del self.active_connections[flow_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")

    async def broadcast_to_flow(self, message: dict, flow_id: str):
        if flow_id in self.active_connections:
            disconnected = []
            
            for connection in self.active_connections[flow_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[flow_id].remove(connection)

    def get_flow_connection_count(self, flow_id: str) -> int:
        return len(self.active_connections.get(flow_id, []))