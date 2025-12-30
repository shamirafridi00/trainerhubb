import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Crown } from 'lucide-react';
import type { PageTemplate } from '@/types';

interface TemplatePreviewDialogProps {
  open: boolean;
  onClose: () => void;
  template: PageTemplate | null;
  onApply: (template: PageTemplate) => void;
}

export function TemplatePreviewDialog({ open, onClose, template, onApply }: TemplatePreviewDialogProps) {
  if (!template) return null;

  const handleApply = () => {
    onApply(template);
    onClose();
  };

  const sections = template.template_data?.sections || [];

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-2xl">{template.name}</DialogTitle>
            {template.is_premium && (
              <Badge className="bg-yellow-500 text-white">
                <Crown className="h-3 w-3 mr-1" />
                Premium
              </Badge>
            )}
          </div>
          <DialogDescription>{template.description}</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Template Image */}
          {template.thumbnail ? (
            <img
              src={template.thumbnail}
              alt={template.name}
              className="w-full rounded-lg border"
            />
          ) : (
            <div className="w-full h-64 bg-gradient-to-br from-blue-400 to-purple-500 rounded-lg flex items-center justify-center">
              <span className="text-white text-4xl font-bold">{template.name[0]}</span>
            </div>
          )}

          {/* Template Details */}
          <div className="space-y-3">
            <div>
              <h4 className="font-semibold mb-2">Category</h4>
              <Badge variant="outline">{template.category}</Badge>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Available For</h4>
              <div className="flex gap-2">
                {template.available_for_plans.map((plan) => (
                  <Badge key={plan} variant="secondary">
                    {plan}
                  </Badge>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Included Sections</h4>
              <div className="flex flex-wrap gap-2">
                {sections.map((section: any, index: number) => (
                  <Badge key={index} variant="outline">
                    {section.type}
                  </Badge>
                ))}
              </div>
            </div>

            {template.template_data?.styles && (
              <div>
                <h4 className="font-semibold mb-2">Default Styling</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {template.template_data.styles.primary_color && (
                    <div className="flex items-center gap-2">
                      <div
                        className="w-6 h-6 rounded border"
                        style={{ backgroundColor: template.template_data.styles.primary_color }}
                      />
                      <span>Primary: {template.template_data.styles.primary_color}</span>
                    </div>
                  )}
                  {template.template_data.styles.font_family && (
                    <div>
                      <span>Font: {template.template_data.styles.font_family}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleApply}>
            Use This Template
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

