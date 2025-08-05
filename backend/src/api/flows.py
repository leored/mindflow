from typing import List
from fastapi import APIRouter, HTTPException, Depends
from ..models import Flow, FlowCreate, FlowUpdate
from ..services.flow_service import FlowService

router = APIRouter()


def get_flow_service() -> FlowService:
    return FlowService()


@router.post("/", response_model=Flow)
async def create_flow(
    flow: FlowCreate,
    service: FlowService = Depends(get_flow_service)
) -> Flow:
    return await service.create_flow(flow)


@router.get("/", response_model=List[Flow])
async def list_flows(
    service: FlowService = Depends(get_flow_service)
) -> List[Flow]:
    return await service.list_flows()


@router.get("/{flow_id}", response_model=Flow)
async def get_flow(
    flow_id: str,
    service: FlowService = Depends(get_flow_service)
) -> Flow:
    flow = await service.get_flow(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow


@router.put("/{flow_id}", response_model=Flow)
async def update_flow(
    flow_id: str,
    flow_update: FlowUpdate,
    service: FlowService = Depends(get_flow_service)
) -> Flow:
    flow = await service.update_flow(flow_id, flow_update)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow


@router.delete("/{flow_id}")
async def delete_flow(
    flow_id: str,
    service: FlowService = Depends(get_flow_service)
) -> dict:
    success = await service.delete_flow(flow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Flow not found")
    return {"message": "Flow deleted successfully"}