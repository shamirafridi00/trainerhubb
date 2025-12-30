import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import type { Page } from '@/types';

interface SEOSettingsDialogProps {
  open: boolean;
  onClose: () => void;
  page: Page;
  onSave: (seoData: Partial<Page>) => Promise<void>;
}

export function SEOSettingsDialog({ open, onClose, page, onSave }: SEOSettingsDialogProps) {
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    seo_title: '',
    seo_description: '',
    seo_keywords: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (open && page) {
      setFormData({
        title: page.title || '',
        slug: page.slug || '',
        seo_title: page.seo_title || '',
        seo_description: page.seo_description || '',
        seo_keywords: page.seo_keywords || '',
      });
      setErrors({});
    }
  }, [open, page]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrors({});

    // Validate slug (alphanumeric + hyphens only)
    const slugRegex = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
    if (!slugRegex.test(formData.slug)) {
      setErrors({ slug: 'Slug must contain only lowercase letters, numbers, and hyphens' });
      setIsSubmitting(false);
      return;
    }

    try {
      await onSave(formData);
      onClose();
    } catch (err: any) {
      if (err.response?.data) {
        setErrors(err.response.data);
      } else {
        setErrors({ general: 'Failed to save SEO settings' });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Page Settings & SEO</DialogTitle>
          <DialogDescription>
            Configure page title, URL slug, and SEO meta tags for better search visibility
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            {errors.general && (
              <div className="text-sm text-red-600 bg-red-50 p-3 rounded">
                {errors.general}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="title">Page Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="My Training Services"
                required
              />
              <p className="text-xs text-muted-foreground">
                The main title of your page
              </p>
              {errors.title && (
                <p className="text-sm text-red-600">{errors.title}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="slug">URL Slug *</Label>
              <Input
                id="slug"
                value={formData.slug}
                onChange={(e) => setFormData({ ...formData, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') })}
                placeholder="my-training-services"
                required
              />
              <p className="text-xs text-muted-foreground">
                Your page will be available at: yoursite.com/<strong>{formData.slug || 'slug'}</strong>
              </p>
              {errors.slug && (
                <p className="text-sm text-red-600">{errors.slug}</p>
              )}
            </div>

            <div className="border-t pt-4">
              <h4 className="font-medium mb-3">SEO Settings (Optional)</h4>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="seo_title">SEO Title</Label>
                  <Input
                    id="seo_title"
                    value={formData.seo_title}
                    onChange={(e) => setFormData({ ...formData, seo_title: e.target.value })}
                    placeholder="Professional Training Services | Your Business"
                    maxLength={60}
                  />
                  <p className="text-xs text-muted-foreground">
                    {formData.seo_title.length}/60 characters (appears in search results)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="seo_description">SEO Description</Label>
                  <Textarea
                    id="seo_description"
                    value={formData.seo_description}
                    onChange={(e) => setFormData({ ...formData, seo_description: e.target.value })}
                    placeholder="Comprehensive description of your training services and what makes you unique..."
                    rows={3}
                    maxLength={160}
                  />
                  <p className="text-xs text-muted-foreground">
                    {formData.seo_description.length}/160 characters (appears in search results)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="seo_keywords">SEO Keywords</Label>
                  <Input
                    id="seo_keywords"
                    value={formData.seo_keywords}
                    onChange={(e) => setFormData({ ...formData, seo_keywords: e.target.value })}
                    placeholder="personal training, fitness, wellness, nutrition"
                  />
                  <p className="text-xs text-muted-foreground">
                    Comma-separated keywords for search engines
                  </p>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save Settings'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

