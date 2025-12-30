import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { PageSection } from '@/types';

interface SectionPreviewProps {
  section: PageSection;
  isSelected: boolean;
  onClick: () => void;
}

export function SectionPreview({ section, isSelected, onClick }: SectionPreviewProps) {
  const renderSectionContent = () => {
    switch (section.section_type) {
      case 'hero':
        return (
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-12 rounded-lg text-center">
            <h2 className="text-3xl font-bold mb-4">
              {section.content.title || 'Hero Section'}
            </h2>
            <p className="text-xl mb-6">
              {section.content.subtitle || 'Add your subtitle here'}
            </p>
            {section.content.cta_text && (
              <button className="bg-white text-blue-600 px-6 py-2 rounded-lg font-semibold">
                {section.content.cta_text}
              </button>
            )}
          </div>
        );
      
      case 'services':
        return (
          <div className="p-6">
            <h3 className="text-2xl font-bold mb-4">
              {section.content.title || 'Our Services'}
            </h3>
            <div className="grid grid-cols-3 gap-4">
              {section.content.services && section.content.services.length > 0 ? (
                section.content.services.slice(0, 3).map((service: any, idx: number) => (
                  <div key={idx} className="border rounded p-4">
                    <h4 className="font-semibold">{service.name || 'Service'}</h4>
                    <p className="text-sm text-muted-foreground">{service.description || ''}</p>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground col-span-3">No services added yet</p>
              )}
            </div>
          </div>
        );
      
      case 'about':
        return (
          <div className="p-6">
            <h3 className="text-2xl font-bold mb-4">
              {section.content.heading || 'About Us'}
            </h3>
            <p className="text-muted-foreground">
              {section.content.content || 'Add your about content here...'}
            </p>
          </div>
        );
      
      case 'testimonials':
        return (
          <div className="p-6">
            <h3 className="text-2xl font-bold mb-4">
              {section.content.title || 'Testimonials'}
            </h3>
            {section.content.testimonials && section.content.testimonials.length > 0 ? (
              <div className="space-y-4">
                {section.content.testimonials.slice(0, 2).map((testimonial: any, idx: number) => (
                  <div key={idx} className="border-l-4 border-primary pl-4">
                    <p className="italic mb-2">"{testimonial.text || 'Testimonial text'}"</p>
                    <p className="font-semibold">- {testimonial.name || 'Client Name'}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No testimonials added yet</p>
            )}
          </div>
        );
      
      case 'contact':
        return (
          <div className="p-6 bg-gray-50 rounded-lg">
            <h3 className="text-2xl font-bold mb-4">
              {section.content.title || 'Contact Us'}
            </h3>
            <div className="space-y-2 text-sm">
              <p>Email: {section.content.email || 'your@email.com'}</p>
              <p>Phone: {section.content.phone || '+1 (555) 123-4567'}</p>
              <p>Address: {section.content.address || 'Your address'}</p>
            </div>
          </div>
        );
      
      case 'pricing':
        return (
          <div className="p-6">
            <h3 className="text-2xl font-bold mb-4">
              {section.content.title || 'Pricing'}
            </h3>
            <div className="grid grid-cols-3 gap-4">
              {section.content.packages && section.content.packages.length > 0 ? (
                section.content.packages.slice(0, 3).map((pkg: any, idx: number) => (
                  <div key={idx} className="border rounded p-4 text-center">
                    <h4 className="font-bold text-lg">{pkg.name || 'Plan'}</h4>
                    <p className="text-2xl font-bold my-2">${pkg.price || '0'}</p>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground col-span-3">No packages added yet</p>
              )}
            </div>
          </div>
        );
      
      case 'gallery':
        return (
          <div className="p-6">
            <h3 className="text-2xl font-bold mb-4">
              {section.content.title || 'Gallery'}
            </h3>
            <div className="grid grid-cols-4 gap-2">
              {section.content.images && Array.isArray(section.content.images) && section.content.images.length > 0 ? (
                section.content.images.slice(0, 4).map((_img: any, idx: number) => (
                  <div key={idx} className="aspect-square bg-gray-200 rounded flex items-center justify-center">
                    <span className="text-xs text-muted-foreground">Image {idx + 1}</span>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground col-span-4">No images added yet</p>
              )}
            </div>
          </div>
        );
      
      case 'faq':
        return (
          <div className="p-6">
            <h3 className="text-2xl font-bold mb-4">
              {section.content.title || 'FAQ'}
            </h3>
            {section.content.faqs && section.content.faqs.length > 0 ? (
              <div className="space-y-4">
                {section.content.faqs.slice(0, 3).map((faq: any, idx: number) => (
                  <div key={idx} className="border-b pb-2">
                    <p className="font-semibold">{faq.question || 'Question?'}</p>
                    <p className="text-sm text-muted-foreground">{faq.answer || 'Answer...'}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No FAQs added yet</p>
            )}
          </div>
        );
      
      case 'booking':
        return (
          <div className="p-6 bg-blue-50 rounded-lg">
            <h3 className="text-2xl font-bold mb-4">
              {section.content.title || 'Book a Session'}
            </h3>
            <p className="text-muted-foreground mb-4">
              {section.content.description || 'Select a date and time to book your session'}
            </p>
            <button className="bg-primary text-primary-foreground px-6 py-2 rounded-lg">
              Book Now
            </button>
          </div>
        );
      
      default:
        const sectionType = section.section_type as string;
        return (
          <div className="p-6 text-center text-muted-foreground">
            {sectionType.charAt(0).toUpperCase() + sectionType.slice(1)} Section
          </div>
        );
    }
  };

  return (
    <Card
      className={`cursor-pointer transition-all ${isSelected ? 'ring-2 ring-primary shadow-lg' : 'hover:shadow-md'}`}
      onClick={onClick}
    >
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center justify-between">
          <span>
            {section.section_type.charAt(0).toUpperCase() + section.section_type.slice(1)} Section
          </span>
          {!section.is_visible && (
            <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">Hidden</span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {renderSectionContent()}
      </CardContent>
    </Card>
  );
}

