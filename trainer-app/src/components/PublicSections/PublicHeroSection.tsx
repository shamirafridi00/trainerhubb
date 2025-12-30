import { PageSection } from '@/types';

interface PublicHeroSectionProps {
  section: PageSection;
}

export function PublicHeroSection({ section }: PublicHeroSectionProps) {
  const { content } = section;

  return (
    <section
      className="relative min-h-[600px] flex items-center justify-center text-white"
      style={{
        backgroundImage: content.background_image
          ? `linear-gradient(rgba(0, 0, 0, ${content.overlay_opacity || 0.5}), rgba(0, 0, 0, ${content.overlay_opacity || 0.5})), url(${content.background_image})`
          : 'linear-gradient(135deg, var(--primary-color, #3b82f6), var(--secondary-color, #8b5cf6))',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="container mx-auto px-4 text-center z-10">
        <h1 className="text-5xl md:text-6xl font-bold mb-6">
          {content.title || 'Transform Your Fitness'}
        </h1>
        <p className="text-xl md:text-2xl mb-8 max-w-2xl mx-auto">
          {content.subtitle || 'Professional Training Solutions'}
        </p>
        {content.cta_text && (
          <a
            href={content.cta_link || '#booking'}
            className="inline-block bg-white text-gray-900 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-colors"
            style={{ backgroundColor: 'var(--accent-color, white)', color: 'var(--background-color, #000)' }}
          >
            {content.cta_text}
          </a>
        )}
      </div>
    </section>
  );
}

