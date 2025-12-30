import { PageSection } from '@/types';

interface PublicServicesSectionProps {
  section: PageSection;
}

export function PublicServicesSection({ section }: PublicServicesSectionProps) {
  const { content } = section;
  const services = content.services || [];

  return (
    <section className="py-20" style={{ backgroundColor: 'var(--background-color, #f9fafb)' }}>
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-12" style={{ color: 'var(--text-color, #111827)' }}>
          {content.title || 'Our Services'}
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service: any, index: number) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              {service.image && (
                <img
                  src={service.image}
                  alt={service.name}
                  className="w-full h-48 object-cover rounded-lg mb-4"
                />
              )}
              <h3 className="text-2xl font-semibold mb-2" style={{ color: 'var(--primary-color, #3b82f6)' }}>
                {service.name}
              </h3>
              <p className="text-gray-600 mb-4">{service.description}</p>
              {service.price && (
                <p className="text-xl font-bold" style={{ color: 'var(--accent-color, #10b981)' }}>
                  {service.price}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

