import { useState } from 'react';
import { PageSection } from '@/types';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface PublicFAQSectionProps {
  section: PageSection;
}

export function PublicFAQSection({ section }: PublicFAQSectionProps) {
  const { content } = section;
  const faqs = content.faqs || [];
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section className="py-20" style={{ backgroundColor: 'var(--background-color, #ffffff)' }}>
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-12" style={{ color: 'var(--text-color, #111827)' }}>
          {content.title || 'Frequently Asked Questions'}
        </h2>
        
        <div className="max-w-3xl mx-auto space-y-4">
          {faqs.map((faq: any, index: number) => (
            <div key={index} className="border rounded-lg overflow-hidden">
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <span className="font-semibold text-lg" style={{ color: 'var(--text-color, #111827)' }}>
                  {faq.question}
                </span>
                {openIndex === index ? (
                  <ChevronUp className="h-5 w-5" style={{ color: 'var(--primary-color, #3b82f6)' }} />
                ) : (
                  <ChevronDown className="h-5 w-5" style={{ color: 'var(--primary-color, #3b82f6)' }} />
                )}
              </button>
              {openIndex === index && (
                <div className="px-6 py-4 bg-gray-50 border-t">
                  <p className="text-gray-600 whitespace-pre-line">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

