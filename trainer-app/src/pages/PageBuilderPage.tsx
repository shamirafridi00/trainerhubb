import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Save, Eye, Plus, ArrowLeft, Settings, Globe, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { usePageBuilder } from '@/hooks/usePageBuilder';
import { SortableSections } from '@/components/PageBuilder/SortableSections';
import { PropertiesPanel } from '@/components/PageBuilder/PropertiesPanel';
import { SEOSettingsDialog } from '@/components/PageBuilder/SEOSettingsDialog';
import { PreviewMode } from '@/components/PageBuilder/PreviewMode';
import { apiClient } from '@/api/client';
import type { Page } from '@/types';

export default function PageBuilderPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  // Determine if this is a new page based on URL path
  const isNewPage = location.pathname === '/pages/new' || !id;
  const [showSEOSettings, setShowSEOSettings] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const {
    page,
    sections,
    selectedSection,
    isLoading,
    isSaving,
    error,
    loadPage,
    savePage,
    addSection,
    updateSection,
    deleteSection,
    selectSection,
    reorderSections,
    setPageState,
  } = usePageBuilder();

  useEffect(() => {
    if (isNewPage) {
      // For new pages, create a temporary page object
      setPageState({
        page: {
          id: 0,
          title: 'New Page',
          slug: `page-${Date.now()}`,
          content: {},
          is_published: false,
          seo_title: '',
          seo_description: '',
          seo_keywords: '',
          sections: []
        } as Page,
        sections: [],
        isLoading: false,
        error: null,
      });
    } else if (id) {
      loadPage(parseInt(id));
    }
  }, [id, isNewPage, setPageState, loadPage]);


  const handleSave = async () => {
    try {
      if (isNewPage && page && !page.id) {
        // Create new page first
        const newPage = await apiClient.post<Page>('/pages/', {
          title: page.title,
          slug: page.slug,
          content: page.content,
          seo_title: page.seo_title,
          seo_description: page.seo_description,
          seo_keywords: page.seo_keywords,
        });

        // Create sections for the new page
        if (sections.length > 0) {
          const sectionPromises = sections.map(section =>
            apiClient.post<PageSection>(`/pages/${newPage.id}/sections/`, {
              section_type: section.section_type,
              order: section.order,
              content: section.content,
              is_visible: section.is_visible,
            })
          );
          await Promise.all(sectionPromises);
        }

        navigate(`/pages/${newPage.id}/edit`);
        return;
      }

      await savePage();
      // Show success message
      const saveButton = document.querySelector('[data-save-button]') as HTMLElement;
      if (saveButton) {
        const originalText = saveButton.textContent;
        saveButton.textContent = 'Saved!';
        setTimeout(() => {
          if (saveButton) saveButton.textContent = originalText;
        }, 2000);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save page');
    }
  };

  // Auto-save every 30 seconds
  useEffect(() => {
    if (!page || isNewPage) return;

    const autoSaveInterval = setInterval(() => {
      if (sections.length > 0) {
        savePage();
      }
    }, 30000); // 30 seconds

    return () => clearInterval(autoSaveInterval);
  }, [page, sections, savePage, isNewPage]);

  const handleSaveSEOSettings = async (seoData: Partial<Page>) => {
    if (!page) return;
    try {
      if (isNewPage) {
        // For new pages, just update the local state
        setPageState({
          page: { ...page, ...seoData } as Page
        });
      } else {
        const updatedPage = await apiClient.patch<Page>(`/pages/${page.id}/`, seoData);
        // Reload the page to get updated data
        await loadPage(parseInt(id!));
      }
    } catch (err) {
      throw err; // Let the dialog handle the error
    }
  };

  const handlePublish = async () => {
    if (!page) return;
    
    // Check if page has at least one section
    if (sections.length === 0) {
      alert('Please add at least one section to your page before publishing');
      return;
    }

    // Check if page has a hero section
    const hasHero = sections.some((s) => s.section_type === 'hero');
    if (!hasHero) {
      const confirmWithoutHero = confirm(
        'Your page does not have a hero section. It\'s recommended to add one for better first impressions. Publish anyway?'
      );
      if (!confirmWithoutHero) return;
    }

    try {
      await savePage(); // Save before publishing
      await apiClient.post(`/pages/${page.id}/publish/`);
      alert('Page published successfully!');
      if (id) await loadPage(parseInt(id)); // Reload to get updated status
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to publish page');
    }
  };

  const handleUnpublish = async () => {
    if (!page) return;
    const confirmed = confirm('Are you sure you want to unpublish this page? It will no longer be accessible to the public.');
    if (!confirmed) return;

    try {
      await apiClient.post(`/pages/${page.id}/unpublish/`);
      alert('Page unpublished successfully');
      if (id) await loadPage(parseInt(id)); // Reload to get updated status
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to unpublish page');
    }
  };

  if (isLoading && !isNewPage) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p>Loading page...</p>
      </div>
    );
  }

  if (!page && id && !isNewPage) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p>Page not found</p>
        <Button onClick={() => navigate('/pages')} className="mt-4">
          Back to Pages
        </Button>
      </div>
    );
  }

  if (!page) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="border-b bg-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/pages')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-xl font-bold">{page.title}</h1>
            <div className="flex items-center gap-2">
              <p className="text-sm text-muted-foreground">
                {isNewPage ? 'Create New Page' : 'Page Builder'}
              </p>
              {page.is_published && page.id > 0 && (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                  <Globe className="mr-1 h-3 w-3" />
                  Published
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSEOSettings(true)}
          >
            <Settings className="mr-2 h-3 w-3" />
            Settings
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleSave}
            disabled={isSaving}
            data-save-button
          >
            <Save className="mr-2 h-3 w-3" />
            {isSaving ? 'Saving...' : 'Save'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowPreview(true)}
          >
            <Eye className="mr-2 h-3 w-3" />
            Preview
          </Button>
          {page.is_published ? (
            <Button variant="outline" size="sm" onClick={handleUnpublish}>
              <XCircle className="mr-2 h-3 w-3" />
              Unpublish
            </Button>
          ) : (
            <Button size="sm" onClick={handlePublish}>
              <Globe className="mr-2 h-3 w-3" />
              Publish
            </Button>
          )}
        </div>
      </div>

      {/* Builder Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-64 border-r bg-gray-50 overflow-y-auto">
          <div className="p-4">
            <h2 className="font-semibold mb-4">Sections</h2>
            <div className="space-y-2">
              {['hero', 'services', 'about', 'testimonials', 'contact', 'pricing', 'gallery', 'faq', 'booking'].map((type) => (
                <Button
                  key={type}
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => addSection(type)}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1 overflow-y-auto bg-white p-8">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded text-red-700">
              {error}
            </div>
          )}

          {sections.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="max-w-md">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Start Building Your Page
                </h3>
                <p className="text-gray-600 mb-6">
                  Add sections from the sidebar to create your custom landing page.
                  Start with a hero section to make a great first impression.
                </p>
                <div className="space-y-2">
                  <p className="text-sm text-gray-500">Suggested sections:</p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {['hero', 'services', 'about', 'contact'].map((type) => (
                      <button
                        key={type}
                        onClick={() => addSection(type)}
                        className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm hover:bg-blue-100 transition-colors"
                      >
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <SortableSections
              sections={sections}
              selectedSection={selectedSection}
              onSelect={selectSection}
              onDelete={deleteSection}
              onReorder={reorderSections}
            />
          )}
        </div>

        {/* Properties Panel */}
        {selectedSection && (
          <div className="w-80 border-l bg-gray-50 overflow-y-auto p-4">
            <PropertiesPanel
              section={selectedSection}
              onUpdate={updateSection}
            />
          </div>
        )}
      </div>

      {/* SEO Settings Dialog */}
      <SEOSettingsDialog
        open={showSEOSettings}
        onClose={() => setShowSEOSettings(false)}
        page={page}
        onSave={handleSaveSEOSettings}
      />

      {/* Preview Mode */}
      {showPreview && (
        <PreviewMode
          page={page}
          sections={sections}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
}

