import { useState, useCallback } from 'react'
import { Handle, Position, type NodeProps } from '@xyflow/react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { X } from 'lucide-react'

interface NodeData extends Record<string, unknown> {
  title: string
  content: string
}

function CustomNode({ id, data }: NodeProps) {
  const nodeData = data as NodeData
  const [title, setTitle] = useState(nodeData.title)
  const [content, setContent] = useState(nodeData.content)

  const handleTitleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newTitle = event.target.value
    setTitle(newTitle)
    // In a real app, you'd want to update the node data in the parent component
    // For now, we'll just update local state
  }, [])

  const handleContentChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = event.target.value
    setContent(newContent)
    // In a real app, you'd want to update the node data in the parent component
    // For now, we'll just update local state
  }, [])

  const handleRemoveNode = useCallback(() => {
    // In a real app, you'd want to call a function from the parent to remove the node
    console.log('Remove node:', id)
  }, [id])

  return (
    <>
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-green-500 !border-green-600"
      />
      
      <Card className="min-w-[200px] max-w-[300px] shadow-lg hover:shadow-xl transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <Input
            value={title}
            onChange={handleTitleChange}
            className="border-none p-0 font-semibold text-sm bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0"
            placeholder="Node title"
          />
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRemoveNode}
            className="h-6 w-6 text-muted-foreground hover:text-destructive"
          >
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        
        <CardContent className="pt-0">
          <Textarea
            value={content}
            onChange={handleContentChange}
            className="min-h-[80px] resize-y text-sm"
            placeholder="Enter your thoughts..."
          />
        </CardContent>
      </Card>
      
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-blue-500 !border-blue-600"
      />
    </>
  )
}

export default CustomNode