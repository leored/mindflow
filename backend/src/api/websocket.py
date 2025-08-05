from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websocket.connection_manager import ConnectionManager
from ..websocket.message_handler import MessageHandler
import json
import logging

router = APIRouter()
manager = ConnectionManager()
message_handler = MessageHandler()

logger = logging.getLogger(__name__)


@router.websocket("/flow/{flow_id}")
async def websocket_endpoint(websocket: WebSocket, flow_id: str):
    await manager.connect(websocket, flow_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                response = await message_handler.handle_message(message, flow_id)
                
                if response:
                    await manager.send_personal_message(response, websocket)
                    
            except json.JSONDecodeError:
                error_response = {
                    "type": "error",
                    "message": "Invalid JSON format"
                }
                await manager.send_personal_message(error_response, websocket)
                
            except Exception as e:
                logger.error(f"Error handling message: {str(e)}")
                error_response = {
                    "type": "error", 
                    "message": f"Error processing message: {str(e)}"
                }
                await manager.send_personal_message(error_response, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, flow_id)
        logger.info(f"Client disconnected from flow {flow_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket, flow_id)