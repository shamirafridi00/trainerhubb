import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { PageSection } from '@/types';
import { Mail, Phone, MapPin, CheckCircle } from 'lucide-react';
import axios from 'axios';

interface PublicContactSectionProps {
  section: PageSection;
}

export function PublicContactSection({ section }: PublicContactSectionProps) {
  const { content } = section;
  const { trainerSlug } = useParams<{ trainerSlug: string }>();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await axios.post(`/api/public/${trainerSlug}/contact/`, formData);
      setSuccess(true);
      setFormData({ name: '', email: '', phone: '', subject: '', message: '' });
      setTimeout(() => setSuccess(false), 5000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send message. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="py-20" style={{ backgroundColor: 'var(--background-color, #f9fafb)' }}>
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-12" style={{ color: 'var(--text-color, #111827)' }}>
          {content.title || 'Contact Us'}
        </h2>
        
        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-12">
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold mb-4" style={{ color: 'var(--primary-color, #3b82f6)' }}>
              Get In Touch
            </h3>
            {content.email && (
              <div className="flex items-start gap-4">
                <Mail className="h-6 w-6 mt-1" style={{ color: 'var(--primary-color, #3b82f6)' }} />
                <div>
                  <p className="font-semibold">Email</p>
                  <a href={`mailto:${content.email}`} className="text-gray-600 hover:underline">
                    {content.email}
                  </a>
                </div>
              </div>
            )}
            {content.phone && (
              <div className="flex items-start gap-4">
                <Phone className="h-6 w-6 mt-1" style={{ color: 'var(--primary-color, #3b82f6)' }} />
                <div>
                  <p className="font-semibold">Phone</p>
                  <a href={`tel:${content.phone}`} className="text-gray-600 hover:underline">
                    {content.phone}
                  </a>
                </div>
              </div>
            )}
            {content.address && (
              <div className="flex items-start gap-4">
                <MapPin className="h-6 w-6 mt-1" style={{ color: 'var(--primary-color, #3b82f6)' }} />
                <div>
                  <p className="font-semibold">Address</p>
                  <p className="text-gray-600 whitespace-pre-line">{content.address}</p>
                </div>
              </div>
            )}
          </div>
          
          <div>
            {success && (
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-700">
                <CheckCircle className="h-5 w-5" />
                <span>Message sent successfully!</span>
              </div>
            )}
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                  style={{ borderColor: 'var(--primary-color, #3b82f6)' }}
                  placeholder="Your name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Email *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                  style={{ borderColor: 'var(--primary-color, #3b82f6)' }}
                  placeholder="your@email.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Phone</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                  style={{ borderColor: 'var(--primary-color, #3b82f6)' }}
                  placeholder="+1 (555) 123-4567"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Subject *</label>
                <input
                  type="text"
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  required
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                  style={{ borderColor: 'var(--primary-color, #3b82f6)' }}
                  placeholder="What is this about?"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Message *</label>
                <textarea
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  required
                  rows={4}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                  style={{ borderColor: 'var(--primary-color, #3b82f6)' }}
                  placeholder="Your message..."
                />
              </div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3 rounded-lg text-white font-semibold hover:opacity-90 transition-opacity disabled:opacity-50"
                style={{ backgroundColor: 'var(--primary-color, #3b82f6)' }}
              >
                {isSubmitting ? 'Sending...' : 'Send Message'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}

