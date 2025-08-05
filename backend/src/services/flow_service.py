from typing import List, Optional
import uuid
from datetime import datetime
from ..models import Flow, FlowCreate, FlowUpdate


class FlowService:
    def __init__(self):
        # In-memory storage for development - replace with database
        self._flows: dict[str, Flow] = {}

    async def create_flow(self, flow_create: FlowCreate) -> Flow:
        flow_id = str(uuid.uuid4())
        flow = Flow(
            id=flow_id,
            **flow_create.model_dump(),
            nodes=[],
            connections=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self._flows[flow_id] = flow
        return flow

    async def get_flow(self, flow_id: str) -> Optional[Flow]:
        return self._flows.get(flow_id)

    async def list_flows(self) -> List[Flow]:
        return list(self._flows.values())

    async def update_flow(self, flow_id: str, flow_update: FlowUpdate) -> Optional[Flow]:
        if flow_id not in self._flows:
            return None
        
        flow = self._flows[flow_id]
        update_data = flow_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(flow, field, value)
        
        flow.updated_at = datetime.utcnow()
        flow.version += 1
        
        return flow

    async def delete_flow(self, flow_id: str) -> bool:
        if flow_id in self._flows:
            del self._flows[flow_id]
            return True
        return False