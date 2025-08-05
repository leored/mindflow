from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from .node import Node
from .connection import Connection


class FlowBase(BaseModel):
    name: str = Field(..., description="Flow name")
    description: Optional[str] = Field(None, description="Flow description")
    metadata: dict = Field(default_factory=dict, description="Flow metadata")


class FlowCreate(FlowBase):
    pass


class FlowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class Flow(FlowBase):
    id: str = Field(..., description="Unique flow identifier")
    nodes: List[Node] = Field(default_factory=list, description="Flow nodes")
    connections: List[Connection] = Field(default_factory=list, description="Node connections")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, description="Flow version")
    is_readonly: bool = Field(default=False, description="Read-only flag")

    class Config:
        from_attributes = True