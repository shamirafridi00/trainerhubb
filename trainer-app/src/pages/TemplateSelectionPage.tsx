import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TemplateCard } from '@/components/TemplateCard';
import { TemplatePreviewDialog } from '@/components/TemplatePreviewDialog';
import { apiClient } from '@/api/client';
import { useSubscriptionStore } from '@/store/subscriptionStore';
import type { PageTemplate, Page } from '@/types';

export default function TemplateSelectionPage() {
  const navigate = useNavigate();
  const { subscription } = useSubscriptionStore();
  const [templates, setTemplates] = useState<PageTemplate[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<PageTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [previewTemplate, setPreviewTemplate] = useState<PageTemplate | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    fetchTemplates();
  }, []);

  useEffect(() => {
    filterTemplates();
  }, [templates, searchTerm, categoryFilter, subscription]);

  const fetchTemplates = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.get<PageTemplate[]>('/pages/templates/');
      setTemplates(data);
    } catch (err) {
      console.error('Failed to fetch templates:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filterTemplates = () => {
    let filtered = templates;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter((template) =>
        template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        template.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by category
    if (categoryFilter !== 'all') {
      filtered = filtered.filter((template) => template.category === categoryFilter);
    }

    // Filter by plan availability
    const currentPlan = subscription?.plan || 'free';
    filtered = filtered.filter((template) =>
      template.available_for_plans.includes(currentPlan)
    );

    setFilteredTemplates(filtered);
  };

  const handlePreview = (template: PageTemplate) => {
    setPreviewTemplate(template);
    setShowPreview(true);
  };

  const handleApplyTemplate = async (template: PageTemplate) => {
    try {
      // Create a new page with template data
      const newPage = await apiClient.post<Page>('/pages/', {
        title: template.name,
        slug: `${template.slug}-${Date.now()}`,
        template: template.id,
        content: template.template_data,
      });

      // Navigate to page builder to edit the page
      navigate(`/pages/${newPage.id}/edit`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to apply template');
    }
  };

  // Get unique categories
  const categories = Array.from(new Set(templates.map((t) => t.category)));

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate('/pages')}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Choose a Template</h1>
              <p className="text-muted-foreground mt-1">
                Start with a professional design and customize it to your needs
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map((category) => (
              <SelectItem key={category} value={category}>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Templates Grid */}
      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-gray-200 animate-pulse rounded-lg h-96" />
          ))}
        </div>
      ) : filteredTemplates.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-lg text-muted-foreground">No templates found</p>
          <p className="text-sm text-muted-foreground mt-2">
            Try adjusting your search or filters
          </p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredTemplates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              onApply={handleApplyTemplate}
              onPreview={handlePreview}
            />
          ))}
        </div>
      )}

      {/* Or Start From Scratch */}
      <div className="mt-12 p-6 border-2 border-dashed rounded-lg text-center">
        <h3 className="font-semibold mb-2">Prefer to start from scratch?</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Create a blank page and build it from the ground up
        </p>
        <Button onClick={() => navigate('/pages/new/edit')}>
          Create Blank Page
        </Button>
      </div>

      {/* Template Preview Dialog */}
      <TemplatePreviewDialog
        open={showPreview}
        onClose={() => setShowPreview(false)}
        template={previewTemplate}
        onApply={handleApplyTemplate}
      />
    </div>
  );
}

