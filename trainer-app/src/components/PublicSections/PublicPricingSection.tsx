import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { PageSection } from '@/types';
import { Check, CreditCard, ExternalLink } from 'lucide-react';
import axios from 'axios';

interface PublicPricingSectionProps {
  section: PageSection;
}

interface PaymentMethod {
  type: string;
  label: string;
  url?: string;
  info?: string;
}

export function PublicPricingSection({ section }: PublicPricingSectionProps) {
  const { content } = section;
  const { trainerSlug } = useParams<{ trainerSlug: string }>();
  const packages = content.packages || [];
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [showPaymentMethods, setShowPaymentMethods] = useState(false);

  useEffect(() => {
    fetchPaymentMethods();
  }, [trainerSlug]);

  const fetchPaymentMethods = async () => {
    try {
      const response = await axios.get(`/api/public/${trainerSlug}/payment-methods/`);
      if (response.data.show_on_public_pages && response.data.available_methods.length > 0) {
        setPaymentMethods(response.data.available_methods);
        setShowPaymentMethods(true);
      }
    } catch (error) {
      // Payment methods not configured or error fetching
      console.log('Payment methods not available');
    }
  };

  return (
    <section className="py-20" style={{ backgroundColor: 'var(--background-color, #ffffff)' }}>
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-12" style={{ color: 'var(--text-color, #111827)' }}>
          {content.title || 'Pricing Plans'}
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {packages.map((pkg: any, index: number) => (
            <div
              key={index}
              className="bg-white border-2 rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow"
              style={{ borderColor: 'var(--primary-color, #3b82f6)' }}
            >
              <h3 className="text-2xl font-bold mb-2" style={{ color: 'var(--primary-color, #3b82f6)' }}>
                {pkg.name}
              </h3>
              <div className="text-4xl font-bold mb-4" style={{ color: 'var(--accent-color, #10b981)' }}>
                {pkg.price}
              </div>
              {pkg.description && (
                <p className="text-gray-600 mb-6">{pkg.description}</p>
              )}
              {pkg.features && (
                <ul className="space-y-3 mb-8">
                  {pkg.features.split(',').map((feature: string, i: number) => (
                    <li key={i} className="flex items-start gap-2">
                      <Check className="h-5 w-5 mt-0.5 flex-shrink-0" style={{ color: 'var(--accent-color, #10b981)' }} />
                      <span>{feature.trim()}</span>
                    </li>
                  ))}
                </ul>
              )}
              <button
                className="w-full py-3 rounded-lg text-white font-semibold hover:opacity-90 transition-opacity"
                style={{ backgroundColor: 'var(--primary-color, #3b82f6)' }}
              >
                Get Started
              </button>
            </div>
          ))}
        </div>

        {/* Payment Methods */}
        {showPaymentMethods && paymentMethods.length > 0 && (
          <div className="mt-12 pt-12 border-t">
            <div className="flex items-center justify-center gap-2 mb-6">
              <CreditCard className="h-6 w-6" style={{ color: 'var(--primary-color, #3b82f6)' }} />
              <h3 className="text-2xl font-bold" style={{ color: 'var(--text-color, #111827)' }}>
                Payment Options
              </h3>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
              {paymentMethods.map((method, index) => (
                <div key={index} className="text-center">
                  {method.url ? (
                    <a
                      href={method.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-3 rounded-lg border-2 hover:shadow-md transition-shadow"
                      style={{ borderColor: 'var(--primary-color, #3b82f6)', color: 'var(--text-color, #111827)' }}
                    >
                      <span className="font-medium">{method.label}</span>
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  ) : (
                    <div
                      className="px-4 py-3 rounded-lg border-2"
                      style={{ borderColor: 'var(--primary-color, #3b82f6)' }}
                    >
                      <p className="font-medium">{method.label}</p>
                      {method.info && <p className="text-sm text-gray-600 mt-1">{method.info}</p>}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

