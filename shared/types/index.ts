// Shared TypeScript types for MindFlow

export interface Position {
  x: number;
  y: number;
}

export interface NodeInput {
  name: string;
  type: string;
  value?: any;
  required: boolean;
}

export interface NodeOutput {
  name: string;
  type: string;
  value?: any;
}

export interface Node {
  id: string;
  type: string;
  title: string;
  position: Position;
  properties: Record<string, any>;
  inputs: NodeInput[];
  outputs: NodeOutput[];
  flow_id?: string;
}

export interface Connection {
  id: string;
  source_node_id: string;
  source_output: string;
  target_node_id: string;
  target_input: string;
  flow_id?: string;
}

export interface Flow {
  id: string;
  name: string;
  description?: string;
  nodes: Node[];
  connections: Connection[];
  metadata: Record<string, any>;
  version: number;
  created_at: string;
  updated_at: string;
  is_readonly: boolean;
}

export interface FlowCreate {
  name: string;
  description?: string;
  metadata?: Record<string, any>;
}

export interface FlowUpdate {
  name?: string;
  description?: string;
  metadata?: Record<string, any>;
}

// WebSocket message types
export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface NodeUpdateMessage extends WebSocketMessage {
  type: 'node_update';
  node_id: string;
  updates: Partial<Node>;
}

export interface NodeCreateMessage extends WebSocketMessage {
  type: 'node_create';
  node: Omit<Node, 'id' | 'flow_id'>;
}

export interface ConnectionCreateMessage extends WebSocketMessage {
  type: 'connection_create';
  connection: Omit<Connection, 'id' | 'flow_id'>;
}

export interface FlowExecuteMessage extends WebSocketMessage {
  type: 'flow_execute';
}

// Node type definition for plugin system
export interface NodeTypeDefinition {
  type: string;
  title: string;
  description: string;
  category: string;
  inputs: NodeInput[];
  outputs: NodeOutput[];
}