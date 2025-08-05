from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self):
        self.handlers: Dict[str, callable] = {
            "node_update": self._handle_node_update,
            "node_create": self._handle_node_create,
            "node_delete": self._handle_node_delete,
            "connection_create": self._handle_connection_create,
            "connection_delete": self._handle_connection_delete,
            "flow_execute": self._handle_flow_execute,
            "ping": self._handle_ping
        }

    async def handle_message(self, message: Dict[str, Any], flow_id: str) -> Optional[Dict[str, Any]]:
        message_type = message.get("type")
        
        if not message_type:
            return {"type": "error", "message": "Missing message type"}
        
        handler = self.handlers.get(message_type)
        if not handler:
            return {"type": "error", "message": f"Unknown message type: {message_type}"}
        
        try:
            return await handler(message, flow_id)
        except Exception as e:
            logger.error(f"Error handling {message_type}: {str(e)}")
            return {"type": "error", "message": f"Error processing {message_type}"}

    async def _handle_node_update(self, message: Dict[str, Any], flow_id: str) -> Dict[str, Any]:
        node_id = message.get("node_id")
        updates = message.get("updates", {})
        
        # TODO: Update node in database/storage
        logger.info(f"Node {node_id} updated in flow {flow_id}: {updates}")
        
        return {
            "type": "node_updated",
            "node_id": node_id,
            "updates": updates
        }

    async def _handle_node_create(self, message: Dict[str, Any], flow_id: str) -> Dict[str, Any]:
        node_data = message.get("node", {})
        
        # TODO: Create node in database/storage
        logger.info(f"Node created in flow {flow_id}: {node_data}")
        
        return {
            "type": "node_created",
            "node": node_data
        }

    async def _handle_node_delete(self, message: Dict[str, Any], flow_id: str) -> Dict[str, Any]:
        node_id = message.get("node_id")
        
        # TODO: Delete node from database/storage
        logger.info(f"Node {node_id} deleted from flow {flow_id}")
        
        return {
            "type": "node_deleted",
            "node_id": node_id
        }

    async def _handle_connection_create(self, message: Dict[str, Any], flow_id: str) -> Dict[str, Any]:
        connection_data = message.get("connection", {})
        
        # TODO: Create connection in database/storage
        logger.info(f"Connection created in flow {flow_id}: {connection_data}")
        
        return {
            "type": "connection_created",
            "connection": connection_data
        }

    async def _handle_connection_delete(self, message: Dict[str, Any], flow_id: str) -> Dict[str, Any]:
        connection_id = message.get("connection_id")
        
        # TODO: Delete connection from database/storage
        logger.info(f"Connection {connection_id} deleted from flow {flow_id}")
        
        return {
            "type": "connection_deleted",
            "connection_id": connection_id
        }

    async def _handle_flow_execute(self, message: Dict[str, Any], flow_id: str) -> Dict[str, Any]:
        # TODO: Execute flow nodes
        logger.info(f"Flow {flow_id} execution requested")
        
        return {
            "type": "flow_execution_started",
            "flow_id": flow_id
        }

    async def _handle_ping(self, message: Dict[str, Any], flow_id: str) -> Dict[str, Any]:
        return {"type": "pong", "timestamp": message.get("timestamp")}