import { Plus, Trash2, GripVertical, Mail, MessageSquare, Edit, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface WorkflowAction {
  id?: string;
  action_type: string;
  action_data: Record<string, any>;
  order: number;
}

interface ActionListProps {
  actions: WorkflowAction[];
  selectedActionIndex: number | null;
  onActionsChange: (actions: WorkflowAction[]) => void;
  onSelectAction: (index: number) => void;
  onAddAction: () => void;
  onDeleteAction: (index: number) => void;
}

function SortableAction({
  action,
  index,
  isSelected,
  onSelect,
  onDelete,
}: {
  action: WorkflowAction;
  index: number;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: action.id || `action-${index}` });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'send_email':
        return <Mail className="h-5 w-5" />;
      case 'send_sms':
        return <MessageSquare className="h-5 w-5" />;
      case 'update_status':
        return <Edit className="h-5 w-5" />;
      case 'create_note':
        return <FileText className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  const getActionLabel = (type: string) => {
    switch (type) {
      case 'send_email':
        return 'Send Email';
      case 'send_sms':
        return 'Send SMS';
      case 'update_status':
        return 'Update Status';
      case 'create_note':
        return 'Create Note';
      default:
        return 'Action';
    }
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
        isSelected ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={onSelect}
    >
      <div className="flex items-center gap-3">
        <div {...attributes} {...listeners} className="cursor-grab active:cursor-grabbing">
          <GripVertical className="h-5 w-5 text-gray-400" />
        </div>
        
        <div className="flex-1 flex items-center gap-3">
          <div className="bg-green-100 p-2 rounded-lg text-green-600">
            {getActionIcon(action.action_type)}
          </div>
          <div>
            <p className="font-medium">{getActionLabel(action.action_type)}</p>
            {action.action_data.subject && (
              <p className="text-sm text-gray-500">Subject: {action.action_data.subject}</p>
            )}
            {action.action_data.message && (
              <p className="text-sm text-gray-500">Message: {action.action_data.message.substring(0, 50)}...</p>
            )}
          </div>
        </div>

        <Button
          variant="ghost"
          size="icon"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
        >
          <Trash2 className="h-4 w-4 text-red-500" />
        </Button>
      </div>
    </div>
  );
}

export function ActionList({
  actions,
  selectedActionIndex,
  onActionsChange,
  onSelectAction,
  onAddAction,
  onDeleteAction,
}: ActionListProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = actions.findIndex((a) => (a.id || `action-${actions.indexOf(a)}`) === active.id);
      const newIndex = actions.findIndex((a) => (a.id || `action-${actions.indexOf(a)}`) === over.id);

      const reorderedActions = arrayMove(actions, oldIndex, newIndex).map((action, index) => ({
        ...action,
        order: index,
      }));

      onActionsChange(reorderedActions);
    }
  };

  const actionsWithIds = actions.map((action, index) => ({
    ...action,
    id: action.id || `action-${index}`,
  }));

  return (
    <div className="bg-white rounded-lg border-2 border-green-500 p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <span className="bg-green-500 text-white w-8 h-8 rounded-full flex items-center justify-center text-sm">
          2
        </span>
        What should happen?
      </h3>

      {actions.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p className="mb-4">No actions configured yet.</p>
          <Button onClick={onAddAction}>
            <Plus className="h-4 w-4 mr-2" />
            Add First Action
          </Button>
        </div>
      ) : (
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={actionsWithIds.map(a => a.id!)} strategy={verticalListSortingStrategy}>
            <div className="space-y-3 mb-4">
              {actionsWithIds.map((action, index) => (
                <SortableAction
                  key={action.id}
                  action={action}
                  index={index}
                  isSelected={selectedActionIndex === index}
                  onSelect={() => onSelectAction(index)}
                  onDelete={() => onDeleteAction(index)}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>
      )}

      {actions.length > 0 && (
        <Button onClick={onAddAction} variant="outline" className="w-full">
          <Plus className="h-4 w-4 mr-2" />
          Add Another Action
        </Button>
      )}
    </div>
  );
}

