import { useState, useEffect } from 'react';
import { Save, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { apiClient } from '@/api/client';

interface CustomLink {
  label: string;
  url: string;
}

interface PaymentLinksData {
  id?: number;
  stripe_link: string;
  paypal_link: string;
  venmo_username: string;
  zelle_email: string;
  cashapp_username: string;
  bank_name: string;
  account_holder_name: string;
  account_number_last4: string;
  routing_number: string;
  custom_links: CustomLink[];
  show_on_public_pages: boolean;
  payment_instructions: string;
}

export default function PaymentLinksSettings() {
  const [formData, setFormData] = useState<PaymentLinksData>({
    stripe_link: '',
    paypal_link: '',
    venmo_username: '',
    zelle_email: '',
    cashapp_username: '',
    bank_name: '',
    account_holder_name: '',
    account_number_last4: '',
    routing_number: '',
    custom_links: [],
    show_on_public_pages: true,
    payment_instructions: '',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchPaymentLinks();
  }, []);

  const fetchPaymentLinks = async () => {
    try {
      const response = await apiClient.get<PaymentLinksData>('/trainers/payment-links/current/');
      setFormData(response.data);
    } catch (error: any) {
      if (error.response?.status !== 404) {
        console.error('Failed to fetch payment links:', error);
      }
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setMessage(null);

    try {
      await apiClient.put('/trainers/payment-links/current/', formData);
      setMessage({ type: 'success', text: 'Payment links saved successfully!' });
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to save payment links',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const addCustomLink = () => {
    setFormData({
      ...formData,
      custom_links: [...formData.custom_links, { label: '', url: '' }],
    });
  };

  const removeCustomLink = (index: number) => {
    const newLinks = formData.custom_links.filter((_, i) => i !== index);
    setFormData({ ...formData, custom_links: newLinks });
  };

  const updateCustomLink = (index: number, field: 'label' | 'url', value: string) => {
    const newLinks = [...formData.custom_links];
    newLinks[index][field] = value;
    setFormData({ ...formData, custom_links: newLinks });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Payment Links</h1>
        <p className="text-gray-600">
          Configure payment methods to display on your public pages. Clients will see these options when they want to pay you.
        </p>
      </div>

      {message && (
        <div
          className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}
        >
          {message.text}
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Popular Payment Methods */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Popular Payment Methods</h2>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="stripe_link">Stripe Payment Link</Label>
              <Input
                id="stripe_link"
                value={formData.stripe_link}
                onChange={(e) => setFormData({ ...formData, stripe_link: e.target.value })}
                placeholder="https://buy.stripe.com/..."
              />
            </div>

            <div>
              <Label htmlFor="paypal_link">PayPal Link</Label>
              <Input
                id="paypal_link"
                value={formData.paypal_link}
                onChange={(e) => setFormData({ ...formData, paypal_link: e.target.value })}
                placeholder="https://paypal.me/..."
              />
            </div>

            <div>
              <Label htmlFor="venmo_username">Venmo Username</Label>
              <Input
                id="venmo_username"
                value={formData.venmo_username}
                onChange={(e) => setFormData({ ...formData, venmo_username: e.target.value })}
                placeholder="username (without @)"
              />
            </div>

            <div>
              <Label htmlFor="zelle_email">Zelle Email/Phone</Label>
              <Input
                id="zelle_email"
                value={formData.zelle_email}
                onChange={(e) => setFormData({ ...formData, zelle_email: e.target.value })}
                placeholder="email@example.com or phone"
              />
            </div>

            <div>
              <Label htmlFor="cashapp_username">Cash App $Cashtag</Label>
              <Input
                id="cashapp_username"
                value={formData.cashapp_username}
                onChange={(e) => setFormData({ ...formData, cashapp_username: e.target.value })}
                placeholder="cashtag (without $)"
              />
            </div>
          </div>
        </div>

        {/* Bank Transfer Info */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Bank Transfer Information</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="bank_name">Bank Name</Label>
              <Input
                id="bank_name"
                value={formData.bank_name}
                onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                placeholder="Bank of America"
              />
            </div>

            <div>
              <Label htmlFor="account_holder_name">Account Holder Name</Label>
              <Input
                id="account_holder_name"
                value={formData.account_holder_name}
                onChange={(e) => setFormData({ ...formData, account_holder_name: e.target.value })}
                placeholder="John Doe"
              />
            </div>

            <div>
              <Label htmlFor="account_number_last4">Last 4 Digits of Account</Label>
              <Input
                id="account_number_last4"
                value={formData.account_number_last4}
                onChange={(e) => setFormData({ ...formData, account_number_last4: e.target.value })}
                placeholder="1234"
                maxLength={4}
              />
            </div>

            <div>
              <Label htmlFor="routing_number">Routing Number</Label>
              <Input
                id="routing_number"
                value={formData.routing_number}
                onChange={(e) => setFormData({ ...formData, routing_number: e.target.value })}
                placeholder="021000021"
              />
            </div>
          </div>
        </div>

        {/* Custom Links */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Custom Payment Links</h2>
            <Button onClick={addCustomLink} variant="outline" size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Add Custom Link
            </Button>
          </div>

          {formData.custom_links.map((link, index) => (
            <div key={index} className="flex gap-2 mb-2">
              <Input
                value={link.label}
                onChange={(e) => updateCustomLink(index, 'label', e.target.value)}
                placeholder="Label (e.g., 'Buy Me A Coffee')"
              />
              <Input
                value={link.url}
                onChange={(e) => updateCustomLink(index, 'url', e.target.value)}
                placeholder="https://..."
              />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeCustomLink(index)}
              >
                <Trash2 className="h-4 w-4 text-red-500" />
              </Button>
            </div>
          ))}
        </div>

        {/* Payment Instructions */}
        <div>
          <Label htmlFor="payment_instructions">Payment Instructions (Optional)</Label>
          <Textarea
            id="payment_instructions"
            value={formData.payment_instructions}
            onChange={(e) => setFormData({ ...formData, payment_instructions: e.target.value })}
            placeholder="Add any special instructions for clients..."
            rows={3}
          />
        </div>

        {/* Display Toggle */}
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="show_on_public_pages"
            checked={formData.show_on_public_pages}
            onChange={(e) => setFormData({ ...formData, show_on_public_pages: e.target.checked })}
            className="h-4 w-4"
          />
          <Label htmlFor="show_on_public_pages" className="cursor-pointer">
            Show payment links on public pages
          </Label>
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-4">
          <Button onClick={handleSave} disabled={isSaving}>
            <Save className="h-4 w-4 mr-2" />
            {isSaving ? 'Saving...' : 'Save Payment Links'}
          </Button>
        </div>
      </div>
    </div>
  );
}

