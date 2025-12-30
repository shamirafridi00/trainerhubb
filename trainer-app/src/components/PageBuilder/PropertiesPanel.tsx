import { useState, useEffect } from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrayEditor } from './ArrayEditor';
import type { PageSection } from '@/types';

interface PropertiesPanelProps {
  section: PageSection | null;
  onUpdate: (sectionId: number, updates: Partial<PageSection>) => void;
}

export function PropertiesPanel({ section, onUpdate }: PropertiesPanelProps) {
  const [formData, setFormData] = useState<Record<string, any>>({});

  useEffect(() => {
    if (section) {
      setFormData(section.content || {});
    }
  }, [section]);

  if (!section) {
    return (
      <div className="p-4 text-center text-muted-foreground">
        <p>Select a section to edit its properties</p>
      </div>
    );
  }

  const handleFieldChange = (field: string, value: any) => {
    const newFormData = { ...formData, [field]: value };
    setFormData(newFormData);
    onUpdate(section.id, { content: newFormData });
  };

  const renderSectionForm = () => {
    switch (section.section_type) {
      case 'hero':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={(e) => handleFieldChange('title', e.target.value)}
                placeholder="Transform Your Fitness"
              />
            </div>
            <div>
              <Label htmlFor="subtitle">Subtitle</Label>
              <Input
                id="subtitle"
                value={formData.subtitle || ''}
                onChange={(e) => handleFieldChange('subtitle', e.target.value)}
                placeholder="Professional Training Solutions"
              />
            </div>
            <div>
              <Label htmlFor="cta_text">CTA Button Text</Label>
              <Input
                id="cta_text"
                value={formData.cta_text || ''}
                onChange={(e) => handleFieldChange('cta_text', e.target.value)}
                placeholder="Get Started"
              />
            </div>
            <div>
              <Label htmlFor="cta_link">CTA Button Link</Label>
              <Input
                id="cta_link"
                value={formData.cta_link || ''}
                onChange={(e) => handleFieldChange('cta_link', e.target.value)}
                placeholder="#booking"
              />
            </div>
            <div>
              <Label htmlFor="background_image">Background Image URL</Label>
              <Input
                id="background_image"
                value={formData.background_image || ''}
                onChange={(e) => handleFieldChange('background_image', e.target.value)}
                placeholder="https://example.com/image.jpg"
              />
            </div>
            <div>
              <Label htmlFor="overlay_opacity">Overlay Opacity (0-1)</Label>
              <Input
                id="overlay_opacity"
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={formData.overlay_opacity || 0.5}
                onChange={(e) => handleFieldChange('overlay_opacity', parseFloat(e.target.value) || 0.5)}
                placeholder="0.5"
              />
            </div>
          </div>
        );

      case 'services':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Section Title</Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={(e) => handleFieldChange('title', e.target.value)}
                placeholder="Our Services"
              />
            </div>
            <ArrayEditor
              items={formData.services || []}
              fields={[
                { name: 'name', label: 'Service Name', type: 'text', placeholder: 'Personal Training' },
                { name: 'description', label: 'Description', type: 'textarea', placeholder: 'One-on-one personalized training sessions', rows: 3 },
                { name: 'price', label: 'Price', type: 'text', placeholder: '$50/session' },
                { name: 'image', label: 'Image URL', type: 'url', placeholder: 'https://example.com/image.jpg' },
              ]}
              itemName="Service"
              onChange={(services) => handleFieldChange('services', services)}
            />
          </div>
        );

      case 'about':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={(e) => handleFieldChange('title', e.target.value)}
                placeholder="About Us"
              />
            </div>
            <div>
              <Label htmlFor="content">Content</Label>
              <Textarea
                id="content"
                value={formData.content || ''}
                onChange={(e) => handleFieldChange('content', e.target.value)}
                placeholder="Tell your story..."
                rows={6}
              />
            </div>
            <div>
              <Label htmlFor="image">Image URL</Label>
              <Input
                id="image"
                value={formData.image || ''}
                onChange={(e) => handleFieldChange('image', e.target.value)}
                placeholder="https://example.com/image.jpg"
              />
            </div>
          </div>
        );

      case 'testimonials':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Section Title</Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={(e) => handleFieldChange('title', e.target.value)}
                placeholder="What Our Clients Say"
              />
            </div>
            <ArrayEditor
              items={formData.testimonials || []}
              fields={[
                { name: 'name', label: 'Client Name', type: 'text', placeholder: 'John Doe' },
                { name: 'text', label: 'Testimonial', type: 'textarea', placeholder: 'Working with this trainer changed my life...', rows: 4 },
                { name: 'rating', label: 'Rating (1-5)', type: 'number', placeholder: '5' },
                { name: 'image', label: 'Client Image URL', type: 'url', placeholder: 'https://example.com/client.jpg' },
              ]}
              itemName="Testimonial"
              onChange={(testimonials) => handleFieldChange('testimonials', testimonials)}
            />
          </div>
        );

      case 'contact':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Section Title</Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={(e) => handleFieldChange('title', e.target.value)}
                placeholder="Contact Us"
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email || ''}
                onChange={(e) => handleFieldChange('email', e.target.value)}
                placeholder="your@email.com"
              />
            </div>
            <div>
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                value={formData.phone || ''}
                onChange={(e) => handleFieldChange('phone', e.target.value)}
                placeholder="+1 (555) 123-4567"
              />
            </div>
            <div>
              <Label htmlFor="address">Address</Label>
              <Textarea
                id="address"
                value={formData.address || ''}
                onChange={(e) => handleFieldChange('address', e.target.value)}
                placeholder="Your address"
                rows={2}
              />
            </div>
          </div>
        );

      case 'pricing':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Section Title</Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={(e) => handleFieldChange('title', e.target.value)}
                placeholder="Pricing Plans"
              />
            </div>
            <ArrayEditor
              items={formData.packages || []}
              fields={[
                { name: 'name', label: 'Package Name', type: 'text', placeholder: 'Basic Plan' },
                { name: 'price', label: 'Price', type: 'text', placeholder: '$99/month' },
                { name: 'description', label: 'Description', type: 'textarea', placeholder: 'Perfect for beginners', rows: 2 },
                { name: 'features', label: 'Features (comma separated)', type: 'textarea', placeholder: '3 sessions per week, Nutrition guide, Progress tracking', rows: 3 },
              ]}
              itemName="Package"
              onChange={(packages) => handleFieldChange('packages', packages)}
            />
          </div>
        );

      case 'gallery':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Section Title</Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={(e) => handleFieldChange('title', e.target.value)}
                placeholder="Gallery"
              />
            </div>
            <div>
              <Label htmlFor="gallery_style">Gallery Style</Label>
              <Select
                value={formData.gallery_style || 'grid'}
                onValueChange={(value) => handleFieldChange('gallery_style', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select style" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="grid">Grid</SelectItem>
                  <SelectItem value="masonry">Masonry</SelectItem>
                  <SelectItem value="carousel">Carousel</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <ArrayEditor
              items={formData.images || []}
              fields={[
                { name: 'url', label: 'Image URL', type: 'url', placeholder: 'https://example.com/image.jpg' },
                { name: 'caption', label: 'Caption', type: 'text', placeholder: 'Optional image caption' },
                { name: 'alt', label: 'Alt Text', type: 'text', placeholder: 'Image description' },
              ]}
              itemName="Image"
              onChange={(images) => handleFieldChange('images', images)}
            />
          </div>
        );

      case 'faq':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Section Title</Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={(e) => handleFieldChange('title', e.target.value)}
                placeholder="Frequently Asked Questions"
              />
            </div>
            <ArrayEditor
              items={formData.faqs || []}
              fields={[
                { name: 'question', label: 'Question', type: 'text', placeholder: 'What are your hours?' },
                { name: 'answer', label: 'Answer', type: 'textarea', placeholder: 'We are open Monday-Friday from 6am to 9pm...', rows: 4 },
              ]}
              itemName="FAQ"
              onChange={(faqs) => handleFieldChange('faqs', faqs)}
            />
          </div>
        );

      case 'booking':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Section Title</Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={(e) => handleFieldChange('title', e.target.value)}
                placeholder="Book a Session"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description || ''}
                onChange={(e) => handleFieldChange('description', e.target.value)}
                placeholder="Select a date and time to book your session"
                rows={3}
              />
            </div>
          </div>
        );

      default:
        return (
          <div className="text-sm text-muted-foreground">
            Properties for this section type will be available in Epic 5.4
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-semibold mb-4">Section Properties</h3>
        <div className="space-y-2 mb-4">
          <div>
            <Label>Section Type</Label>
            <p className="text-sm text-muted-foreground capitalize">{section.section_type}</p>
          </div>
          <div>
            <Label>Order</Label>
            <Input
              type="number"
              value={section.order}
              onChange={(e) => onUpdate(section.id, { order: parseInt(e.target.value) || 0 })}
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_visible"
              checked={section.is_visible}
              onChange={(e) => onUpdate(section.id, { is_visible: e.target.checked })}
            />
            <Label htmlFor="is_visible">Visible</Label>
          </div>
        </div>
      </div>

      <div className="border-t pt-4">
        <h4 className="font-medium mb-4">Content</h4>
        {renderSectionForm()}
      </div>
    </div>
  );
}

