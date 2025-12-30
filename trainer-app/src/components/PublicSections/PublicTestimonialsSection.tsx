import { PageSection } from '@/types';
import { Star } from 'lucide-react';

interface PublicTestimonialsSectionProps {
  section: PageSection;
}

export function PublicTestimonialsSection({ section }: PublicTestimonialsSectionProps) {
  const { content } = section;
  const testimonials = content.testimonials || [];

  return (
    <section className="py-20" style={{ backgroundColor: 'var(--background-color, #ffffff)' }}>
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-12" style={{ color: 'var(--text-color, #111827)' }}>
          {content.title || 'What Our Clients Say'}
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {testimonials.map((testimonial: any, index: number) => (
            <div key={index} className="bg-gray-50 rounded-lg shadow p-6">
              {testimonial.image && (
                <img
                  src={testimonial.image}
                  alt={testimonial.name}
                  className="w-16 h-16 rounded-full mx-auto mb-4 object-cover"
                />
              )}
              <div className="flex justify-center mb-3">
                {[...Array(testimonial.rating || 5)].map((_, i) => (
                  <Star key={i} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-600 italic mb-4">"{testimonial.text}"</p>
              <p className="font-semibold text-center" style={{ color: 'var(--primary-color, #3b82f6)' }}>
                {testimonial.name}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

