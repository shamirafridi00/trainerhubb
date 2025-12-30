import { PageSection } from '@/types';

interface PublicGallerySectionProps {
  section: PageSection;
}

export function PublicGallerySection({ section }: PublicGallerySectionProps) {
  const { content } = section;
  const images = content.images || [];
  const galleryStyle = content.gallery_style || 'grid';

  return (
    <section className="py-20" style={{ backgroundColor: 'var(--background-color, #f9fafb)' }}>
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-12" style={{ color: 'var(--text-color, #111827)' }}>
          {content.title || 'Gallery'}
        </h2>
        
        <div
          className={
            galleryStyle === 'grid'
              ? 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4'
              : galleryStyle === 'masonry'
              ? 'columns-2 md:columns-3 lg:columns-4 gap-4'
              : 'flex overflow-x-auto gap-4 pb-4'
          }
        >
          {images.map((image: any, index: number) => (
            <div
              key={index}
              className={`${galleryStyle === 'masonry' ? 'mb-4' : ''} ${galleryStyle === 'carousel' ? 'flex-shrink-0 w-80' : ''}`}
            >
              <img
                src={image.url}
                alt={image.alt || image.caption || `Gallery image ${index + 1}`}
                className="w-full h-auto rounded-lg shadow-md hover:shadow-xl transition-shadow"
              />
              {image.caption && (
                <p className="text-sm text-gray-600 mt-2 text-center">{image.caption}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

