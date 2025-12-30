import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { DraggableSection } from './DraggableSection';
import { SectionPreview } from './SectionPreview';
import type { PageSection } from '@/types';

interface SortableSectionsProps {
  sections: PageSection[];
  selectedSection: PageSection | null;
  onSelect: (section: PageSection) => void;
  onDelete: (sectionId: number) => void;
  onReorder: (sections: PageSection[]) => void;
}

export function SortableSections({
  sections,
  selectedSection,
  onSelect,
  onDelete,
  onReorder,
}: SortableSectionsProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = sections.findIndex((s) => s.id === active.id);
      const newIndex = sections.findIndex((s) => s.id === over.id);

      const newSections = arrayMove(sections, oldIndex, newIndex);
      onReorder(newSections);
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <SortableContext items={sections.map((s) => s.id)} strategy={verticalListSortingStrategy}>
        <div className="space-y-4">
          {sections.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">No sections yet. Add a section to get started.</p>
            </div>
          ) : (
            sections.map((section) => (
              <div key={section.id}>
                <DraggableSection
                  section={section}
                  isSelected={selectedSection?.id === section.id}
                  onSelect={() => onSelect(section)}
                  onDelete={() => onDelete(section.id)}
                />
                {selectedSection?.id === section.id && (
                  <div className="mt-2">
                    <SectionPreview
                      section={section}
                      isSelected={true}
                      onClick={() => {}}
                    />
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </SortableContext>
    </DndContext>
  );
}

