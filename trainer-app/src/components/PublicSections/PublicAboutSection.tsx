import { PageSection } from '@/types';

interface PublicAboutSectionProps {
  section: PageSection;
}

export function PublicAboutSection({ section }: PublicAboutSectionProps) {
  const { content } = section;

  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {content.image && (
            <div>
              <img
                src={content.image}
                alt={content.title || 'About'}
                className="rounded-lg shadow-lg w-full h-auto"
              />
            </div>
          )}
          <div className={!content.image ? 'md:col-span-2 max-w-4xl mx-auto text-center' : ''}>
            <h2 className="text-4xl font-bold mb-6" style={{ color: 'var(--text-color, #111827)' }}>
              {content.title || 'About Us'}
            </h2>
            <div
              className="text-lg text-gray-600 whitespace-pre-line"
              style={{ color: 'var(--text-color, #4b5563)' }}
            >
              {content.content || ''}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

