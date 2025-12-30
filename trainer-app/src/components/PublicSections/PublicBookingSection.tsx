import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { PageSection } from '@/types';
import { Calendar, CheckCircle } from 'lucide-react';
import { PublicBookingForm } from '../PublicBookingForm';

interface PublicBookingSectionProps {
  section: PageSection;
}

export function PublicBookingSection({ section }: PublicBookingSectionProps) {
  const { content } = section;
  const { trainerSlug } = useParams<{ trainerSlug: string }>();
  const [showBookingForm, setShowBookingForm] = useState(false);
  const [bookingSuccess, setBookingSuccess] = useState(false);

  const handleBookingSuccess = () => {
    setShowBookingForm(false);
    setBookingSuccess(true);
    setTimeout(() => setBookingSuccess(false), 5000);
  };

  return (
    <section className="py-20" style={{ backgroundColor: 'var(--background-color, #f9fafb)' }}>
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto text-center">
          {bookingSuccess ? (
            <>
              <CheckCircle className="h-16 w-16 mx-auto mb-6 text-green-500" />
              <h2 className="text-4xl font-bold mb-6 text-green-600">
                Booking Confirmed!
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                You will receive a confirmation email shortly with all the details.
              </p>
            </>
          ) : (
            <>
              <Calendar className="h-16 w-16 mx-auto mb-6" style={{ color: 'var(--primary-color, #3b82f6)' }} />
              <h2 className="text-4xl font-bold mb-6" style={{ color: 'var(--text-color, #111827)' }}>
                {content.title || 'Book a Session'}
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                {content.description || 'Select a date and time to book your session with us.'}
              </p>
              <button
                onClick={() => setShowBookingForm(true)}
                className="px-8 py-4 rounded-lg text-white text-lg font-semibold hover:opacity-90 transition-opacity"
                style={{ backgroundColor: 'var(--primary-color, #3b82f6)' }}
              >
                Check Availability
              </button>
            </>
          )}
        </div>
      </div>

      {showBookingForm && trainerSlug && (
        <PublicBookingForm
          trainerSlug={trainerSlug}
          onClose={() => setShowBookingForm(false)}
          onSuccess={handleBookingSuccess}
        />
      )}
    </section>
  );
}

