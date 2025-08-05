import { useCallback } from 'react'
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  addEdge,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  type Node,
  type Edge,
  type Connection,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Button } from '@/components/ui/button'
import { Plus, Save, FolderOpen, Trash2 } from 'lucide-react'
import CustomNode from './CustomNode'


const nodeTypes = {
  custom: CustomNode,
}

const initialNodes: Node[] = [
  {
    id: 'node-1',
    type: 'custom',
    position: { x: 250, y: 100 },
    data: {
      title: 'Node 1',
      content: '',
    },
  },
]

const initialEdges: Edge[] = []

let nodeId = 1

function FlowEditor() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const addNode = useCallback(() => {
    const newNode: Node = {
      id: `node-${++nodeId}`,
      type: 'custom',
      position: {
        x: Math.random() * 400 + 100,
        y: Math.random() * 300 + 100,
      },
      data: {
        title: `Node ${nodeId}`,
        content: '',
      },
    }
    setNodes((nds) => [...nds, newNode])
  }, [setNodes])


  const saveFlow = useCallback(() => {
    const flowData = {
      nodes,
      edges,
    }
    localStorage.setItem('mindflow-data', JSON.stringify(flowData))
    console.log('Flow saved')
  }, [nodes, edges])

  const loadFlow = useCallback(() => {
    const savedData = localStorage.getItem('mindflow-data')
    if (savedData) {
      const flowData = JSON.parse(savedData)
      setNodes(flowData.nodes || [])
      setEdges(flowData.edges || [])
      console.log('Flow loaded')
    }
  }, [setNodes, setEdges])

  const clearFlow = useCallback(() => {
    setNodes([])
    setEdges([])
  }, [setNodes, setEdges])

  return (
    <div className="flex h-screen flex-col bg-background">
      <header className="border-b bg-card px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-foreground">MindFlow - Flow Editor</h1>
          <div className="flex gap-2">
            <Button onClick={addNode} className="gap-2">
              <Plus className="h-4 w-4" />
              Add Node
            </Button>
            <Button variant="secondary" onClick={saveFlow} className="gap-2">
              <Save className="h-4 w-4" />
              Save Flow
            </Button>
            <Button variant="secondary" onClick={loadFlow} className="gap-2">
              <FolderOpen className="h-4 w-4" />
              Load Flow
            </Button>
            <Button variant="destructive" onClick={clearFlow} className="gap-2">
              <Trash2 className="h-4 w-4" />
              Clear Flow
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-hidden">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          defaultViewport={{ zoom: 1, x: 0, y: 0 }}
          minZoom={0.2}
          maxZoom={4}
          className="h-full w-full"
        >
          <MiniMap />
          <Controls />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </main>
    </div>
  )
}

export default FlowEditor