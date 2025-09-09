import { Label } from '@/components/ui/label'
import { SmartValueEditor } from "./smart-value-editor"

interface CreateMemoryData {
  context_key: string
  context_value: unknown
  description?: string
}

type OnCreateMemory = (data: {
  context_key: string
  context_value: unknown
  description?: string
}) => Promise<void>

export function CreateMemoryModal({
  onClose,
  onMemoryCreated,
}: {
  onClose: () => void
  onMemoryCreated: OnCreateMemory
}) {
  const [formData, setFormData] = useState({
    context_key: '',
    context_value: '' as unknown,
    description: ''
  })

  const handleValueChange = (value: unknown) => {
    setFormData(prev => ({ ...prev, context_value: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onMemoryCreated({
      context_key: formData.context_key,
      context_value: formData.context_value,
      description: formData.description
    })
    onClose()
  }

  return (
    <Modal onClose={onClose}>
      <ModalHeader>
        <ModalTitle>Create New Memory</ModalTitle>
      </ModalHeader>
      <ModalBody>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="context_key" className="text-right">
                Context Key
              </Label>
              <Input
                id="context_key"
                value={formData.context_key}
                onChange={(e) => setFormData(prev => ({ ...prev, context_key: e.target.value }))}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="context_value" className="text-right">
                Context Value
              </Label>
              <SmartValueEditor
                value={formData.context_value}
                onChange={handleValueChange}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">
                Description
              </Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="col-span-3"
              />
            </div>
          </div>
          <ModalFooter>
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">Create Memory</Button>
          </ModalFooter>
        </form>
      </ModalBody>
    </Modal>
  )
}
