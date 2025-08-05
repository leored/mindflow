from typing import List, Optional
import uuid
from ..models import Node, NodeCreate, NodeUpdate


class NodeService:
    def __init__(self):
        # In-memory storage for development - replace with database
        self._nodes: dict[str, Node] = {}

    async def create_node(self, node_create: NodeCreate, flow_id: str) -> Node:
        node_id = str(uuid.uuid4())
        node = Node(
            id=node_id,
            flow_id=flow_id,
            **node_create.model_dump()
        )
        self._nodes[node_id] = node
        return node

    async def get_node(self, node_id: str) -> Optional[Node]:
        return self._nodes.get(node_id)

    async def update_node(self, node_id: str, node_update: NodeUpdate) -> Optional[Node]:
        if node_id not in self._nodes:
            return None
        
        node = self._nodes[node_id]
        update_data = node_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(node, field, value)
        
        return node

    async def delete_node(self, node_id: str) -> bool:
        if node_id in self._nodes:
            del self._nodes[node_id]
            return True
        return False

    async def get_available_node_types(self) -> List[dict]:
        # Return available node types from plugin system
        return [
            {
                "type": "input",
                "title": "Input Node",
                "description": "Basic input node",
                "category": "inputs"
            },
            {
                "type": "output", 
                "title": "Output Node",
                "description": "Basic output node",
                "category": "outputs"
            },
            {
                "type": "math_add",
                "title": "Add",
                "description": "Add two numbers",
                "category": "math"
            }
        ]