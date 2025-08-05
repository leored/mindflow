from typing import List
from fastapi import APIRouter, HTTPException, Depends
from ..models import Node, NodeCreate, NodeUpdate
from ..services.node_service import NodeService

router = APIRouter()


def get_node_service() -> NodeService:
    return NodeService()


@router.post("/", response_model=Node)
async def create_node(
    node: NodeCreate,
    flow_id: str,
    service: NodeService = Depends(get_node_service)
) -> Node:
    return await service.create_node(node, flow_id)


@router.get("/{node_id}", response_model=Node)
async def get_node(
    node_id: str,
    service: NodeService = Depends(get_node_service)
) -> Node:
    node = await service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.put("/{node_id}", response_model=Node)
async def update_node(
    node_id: str,
    node_update: NodeUpdate,
    service: NodeService = Depends(get_node_service)
) -> Node:
    node = await service.update_node(node_id, node_update)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.delete("/{node_id}")
async def delete_node(
    node_id: str,
    service: NodeService = Depends(get_node_service)
) -> dict:
    success = await service.delete_node(node_id)
    if not success:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"message": "Node deleted successfully"}


@router.get("/types/", response_model=List[dict])
async def get_node_types(
    service: NodeService = Depends(get_node_service)
) -> List[dict]:
    return await service.get_available_node_types()