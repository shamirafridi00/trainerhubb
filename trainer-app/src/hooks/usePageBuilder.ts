import { useState, useCallback } from 'react';
import { apiClient } from '@/api/client';
import type { Page, PageSection } from '@/types';

interface PageBuilderState {
  page: Page | null;
  sections: PageSection[];
  selectedSection: PageSection | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
}

export function usePageBuilder() {
  const [state, setState] = useState<PageBuilderState>({
    page: null,
    sections: [],
    selectedSection: null,
    isLoading: false,
    isSaving: false,
    error: null,
  });

  const loadPage = useCallback(async (id: number) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const page = await apiClient.get<Page>(`/pages/${id}/`);
      let sections: PageSection[] = [];
      try {
        sections = await apiClient.get<PageSection[]>(`/pages/${id}/sections/`) as any;
      } catch (sectionsErr) {
        // Sections endpoint might return empty array or error
        sections = page.sections || [];
      }
      setState(prev => ({
        ...prev,
        page,
        sections: Array.isArray(sections) ? sections : [],
        isLoading: false,
      }));
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        error: err.response?.data?.detail || 'Failed to load page',
        isLoading: false,
      }));
    }
  }, []);

  const savePage = useCallback(async () => {
    if (!state.page) return;

    setState(prev => ({ ...prev, isSaving: true }));
    try {
      const updated = await apiClient.patch<Page>(`/pages/${state.page.id}/`, {
        content: state.page.content,
      });
      setState(prev => ({
        ...prev,
        page: updated,
        isSaving: false,
      }));
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        error: err.response?.data?.detail || 'Failed to save page',
        isSaving: false,
      }));
    }
  }, [state.page]);

  const addSection = useCallback(async (sectionType: string, order?: number) => {
    if (!state.page) return;

    // For new pages (id = 0), add section locally without API call
    if (state.page.id === 0) {
      const newSection: PageSection = {
        id: Date.now(), // Temporary ID for local state
        section_type: sectionType,
        order: order ?? state.sections.length,
        content: {},
        is_visible: true,
        created_at: new Date().toISOString(),
      };
      setState(prev => ({
        ...prev,
        sections: [...prev.sections, newSection],
        selectedSection: newSection,
      }));
      return;
    }

    // For existing pages, add section via API
    try {
      const newSection = await apiClient.post<PageSection>(`/pages/${state.page.id}/sections/`, {
        section_type: sectionType,
        order: order ?? state.sections.length,
        content: {},
        is_visible: true,
      });
      setState(prev => ({
        ...prev,
        sections: [...prev.sections, newSection],
        selectedSection: newSection,
      }));
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        error: err.response?.data?.detail || 'Failed to add section',
      }));
    }
  }, [state.page, state.sections.length]);

  const updateSection = useCallback(async (sectionId: number, updates: Partial<PageSection>) => {
    if (!state.page) return;

    // For new pages (id = 0), update section locally
    if (state.page.id === 0) {
      setState(prev => ({
        ...prev,
        sections: prev.sections.map(s => s.id === sectionId ? { ...s, ...updates } : s),
        selectedSection: prev.selectedSection?.id === sectionId ? { ...prev.selectedSection, ...updates } : prev.selectedSection,
      }));
      return;
    }

    // For existing pages, update section via API
    try {
      const updated = await apiClient.patch<PageSection>(
        `/pages/${state.page.id}/sections/${sectionId}/`,
        updates
      );
      setState(prev => ({
        ...prev,
        sections: prev.sections.map(s => s.id === sectionId ? updated : s),
        selectedSection: prev.selectedSection?.id === sectionId ? updated : prev.selectedSection,
      }));
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        error: err.response?.data?.detail || 'Failed to update section',
      }));
    }
  }, [state.page]);

  const deleteSection = useCallback(async (sectionId: number) => {
    if (!state.page) return;

    // For new pages (id = 0), delete section locally
    if (state.page.id === 0) {
      setState(prev => ({
        ...prev,
        sections: prev.sections.filter(s => s.id !== sectionId),
        selectedSection: prev.selectedSection?.id === sectionId ? null : prev.selectedSection,
      }));
      return;
    }

    // For existing pages, delete section via API
    try {
      await apiClient.delete(`/pages/${state.page.id}/sections/${sectionId}/`);
      setState(prev => ({
        ...prev,
        sections: prev.sections.filter(s => s.id !== sectionId),
        selectedSection: prev.selectedSection?.id === sectionId ? null : prev.selectedSection,
      }));
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        error: err.response?.data?.detail || 'Failed to delete section',
      }));
    }
  }, [state.page]);

  const reorderSections = useCallback(async (newOrder: PageSection[]) => {
    if (!state.page) return;

    // Update order locally first
    setState(prev => ({ ...prev, sections: newOrder }));

    // For new pages (id = 0), skip API call
    if (state.page.id === 0) {
      return;
    }

    // For existing pages, update on backend
    try {
      for (let i = 0; i < newOrder.length; i++) {
        await apiClient.patch(`/pages/${state.page.id}/sections/${newOrder[i].id}/`, {
          order: i,
        });
      }
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        error: err.response?.data?.detail || 'Failed to reorder sections',
      }));
      // Reload to get correct order
      loadPage(state.page.id);
    }
  }, [state.page, loadPage]);

  const selectSection = useCallback((section: PageSection | null) => {
    setState(prev => ({ ...prev, selectedSection: section }));
  }, []);

  const setPageState = useCallback((pageState: Partial<PageBuilderState>) => {
    setState(prev => ({ ...prev, ...pageState }));
  }, []);

  return {
    ...state,
    loadPage,
    savePage,
    addSection,
    updateSection,
    deleteSection,
    reorderSections,
    selectSection,
    setPageState,
  };
}

