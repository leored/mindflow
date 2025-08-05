from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class NodeInput(BaseModel):
    name: str
    type: str
    value: Optional[Any] = None
    required: bool = True


class NodeOutput(BaseModel):
    name: str
    type: str
    value: Optional[Any] = None


class NodeBase(BaseModel):
    type: str = Field(..., description="Node type identifier")
    title: str = Field(..., description="Node display title")
    position: Dict[str, float] = Field(..., description="Node position {x, y}")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")


class NodeCreate(NodeBase):
    pass


class NodeUpdate(BaseModel):
    title: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    properties: Optional[Dict[str, Any]] = None


class Node(NodeBase):
    id: str = Field(..., description="Unique node identifier")
    inputs: List[NodeInput] = Field(default_factory=list, description="Node inputs")
    outputs: List[NodeOutput] = Field(default_factory=list, description="Node outputs")
    flow_id: str = Field(..., description="Parent flow ID")

    class Config:
        from_attributes = True