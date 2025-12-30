import { useState, useEffect } from 'react';
import axios from 'axios';
import type { Page, PageSection } from '@/types';

interface WhiteLabelSettings {
  remove_branding: boolean;
  custom_logo: string | null;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  text_color: string;
  background_color: string;
  font_family: string;
  favicon: string | null;
  custom_css: string;
}

interface PublicPageData extends Page {
  white_label?: WhiteLabelSettings;
}

export function usePublicPage(trainerSlug: string, pageSlug: string) {
  const [page, setPage] = useState<PublicPageData | null>(null);
  const [sections, setSections] = useState<PageSection[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPage();
  }, [trainerSlug, pageSlug]);

  const fetchPage = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await axios.get<PublicPageData>(
        `/api/public/${trainerSlug}/pages/${pageSlug}/`
      );
      
      setPage(response.data);
      setSections(response.data.sections || []);
      
      // Apply white-label styles if available
      if (response.data.white_label) {
        applyWhiteLabelStyles(response.data.white_label);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load page');
    } finally {
      setIsLoading(false);
    }
  };

  const applyWhiteLabelStyles = (whiteLabelSettings: WhiteLabelSettings) => {
    const root = document.documentElement;
    
    root.style.setProperty('--primary-color', whiteLabelSettings.primary_color);
    root.style.setProperty('--secondary-color', whiteLabelSettings.secondary_color);
    root.style.setProperty('--accent-color', whiteLabelSettings.accent_color);
    root.style.setProperty('--text-color', whiteLabelSettings.text_color);
    root.style.setProperty('--background-color', whiteLabelSettings.background_color);
    root.style.setProperty('--font-family', whiteLabelSettings.font_family);
    
    // Apply custom CSS if provided
    if (whiteLabelSettings.custom_css) {
      const styleElement = document.createElement('style');
      styleElement.innerHTML = whiteLabelSettings.custom_css;
      document.head.appendChild(styleElement);
    }
    
    // Update favicon if provided
    if (whiteLabelSettings.favicon) {
      const link = document.querySelector("link[rel~='icon']") as HTMLLinkElement;
      if (link) {
        link.href = whiteLabelSettings.favicon;
      } else {
        const newLink = document.createElement('link');
        newLink.rel = 'icon';
        newLink.href = whiteLabelSettings.favicon;
        document.head.appendChild(newLink);
      }
    }
  };

  return {
    page,
    sections,
    isLoading,
    error,
  };
}

