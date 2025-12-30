import { useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { usePublicPage } from '@/hooks/usePublicPage';
import { PublicHeroSection } from '@/components/PublicSections/PublicHeroSection';
import { PublicServicesSection } from '@/components/PublicSections/PublicServicesSection';
import { PublicAboutSection } from '@/components/PublicSections/PublicAboutSection';
import { PublicTestimonialsSection } from '@/components/PublicSections/PublicTestimonialsSection';
import { PublicContactSection } from '@/components/PublicSections/PublicContactSection';
import { PublicPricingSection } from '@/components/PublicSections/PublicPricingSection';
import { PublicGallerySection } from '@/components/PublicSections/PublicGallerySection';
import { PublicFAQSection } from '@/components/PublicSections/PublicFAQSection';
import { PublicBookingSection } from '@/components/PublicSections/PublicBookingSection';
import type { PageSection } from '@/types';

export default function PublicPageView() {
  const { trainerSlug, pageSlug } = useParams<{ trainerSlug: string; pageSlug: string }>();
  const { page, sections, isLoading, error } = usePublicPage(trainerSlug || '', pageSlug || '');

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading page...</p>
        </div>
      </div>
    );
  }

  if (error || !page) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">Page Not Found</h1>
          <p className="text-gray-600 mb-8">{error || 'The page you are looking for does not exist.'}</p>
          <a
            href="/"
            className="inline-block px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Go Home
          </a>
        </div>
      </div>
    );
  }

  const renderSection = (section: PageSection) => {
    switch (section.section_type) {
      case 'hero':
        return <PublicHeroSection key={section.id} section={section} />;
      case 'services':
        return <PublicServicesSection key={section.id} section={section} />;
      case 'about':
        return <PublicAboutSection key={section.id} section={section} />;
      case 'testimonials':
        return <PublicTestimonialsSection key={section.id} section={section} />;
      case 'contact':
        return <PublicContactSection key={section.id} section={section} />;
      case 'pricing':
        return <PublicPricingSection key={section.id} section={section} />;
      case 'gallery':
        return <PublicGallerySection key={section.id} section={section} />;
      case 'faq':
        return <PublicFAQSection key={section.id} section={section} />;
      case 'booking':
        return <PublicBookingSection key={section.id} section={section} />;
      default:
        return null;
    }
  };

  const visibleSections = sections
    .filter((s) => s.is_visible)
    .sort((a, b) => a.order - b.order);

  return (
    <>
      <Helmet>
        <title>{page.seo_title || page.title}</title>
        {page.seo_description && <meta name="description" content={page.seo_description} />}
        {page.seo_keywords && <meta name="keywords" content={page.seo_keywords} />}
        <meta property="og:title" content={page.seo_title || page.title} />
        {page.seo_description && <meta property="og:description" content={page.seo_description} />}
        <meta property="og:type" content="website" />
      </Helmet>

      <div
        className="min-h-screen"
        style={{
          fontFamily: 'var(--font-family, sans-serif)',
          color: 'var(--text-color, #111827)',
          backgroundColor: 'var(--background-color, #ffffff)',
        }}
      >
        {visibleSections.map((section) => renderSection(section))}

        {/* Footer with branding */}
        {!page.white_label?.remove_branding && (
          <footer className="py-8 border-t">
            <div className="container mx-auto px-4 text-center text-gray-600">
              <p className="text-sm">
                Powered by{' '}
                <a
                  href="https://trainerhubb.app"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  TrainerHub
                </a>
              </p>
            </div>
          </footer>
        )}
      </div>
    </>
  );
}

