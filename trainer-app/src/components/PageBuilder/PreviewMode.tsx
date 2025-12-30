import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SectionPreview } from './SectionPreview';
import type { Page, PageSection } from '@/types';

interface PreviewModeProps {
  page: Page;
  sections: PageSection[];
  onClose: () => void;
}

export function PreviewMode({ page, sections, onClose }: PreviewModeProps) {
  const visibleSections = sections.filter((s) => s.is_visible).sort((a, b) => a.order - b.order);

  return (
    <div className="fixed inset-0 z-50 bg-white flex flex-col">
      {/* Preview Header */}
      <div className="bg-gray-900 text-white px-6 py-3 flex items-center justify-between">
        <div>
          <h2 className="font-semibold">Preview Mode</h2>
          <p className="text-sm text-gray-300">This is how your page will appear to visitors</p>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="text-white hover:bg-gray-800">
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Preview Content */}
      <div className="flex-1 overflow-y-auto bg-gray-50">
        <div className="max-w-6xl mx-auto">
          {visibleSections.length === 0 ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <p className="text-lg text-muted-foreground">No sections added yet</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Add sections to your page to see them in preview
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-0">
              {visibleSections.map((section) => (
                <div key={section.id} className="bg-white border-b">
                  <SectionPreview section={section} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Preview Footer */}
      <div className="bg-gray-100 px-6 py-3 border-t flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Page: <strong>{page.title}</strong> | Slug: <strong>/{page.slug}</strong>
        </p>
        <Button variant="default" onClick={onClose}>
          Close Preview
        </Button>
      </div>
    </div>
  );
}

