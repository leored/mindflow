from typing import Optional
from pydantic import BaseModel, Field


class ConnectionBase(BaseModel):
    source_node_id: str = Field(..., description="Source node ID")
    source_output: str = Field(..., description="Source output name")
    target_node_id: str = Field(..., description="Target node ID")
    target_input: str = Field(..., description="Target input name")


class ConnectionCreate(ConnectionBase):
    pass


class Connection(ConnectionBase):
    id: str = Field(..., description="Unique connection identifier")
    flow_id: str = Field(..., description="Parent flow ID")

    class Config:
        from_attributes = True