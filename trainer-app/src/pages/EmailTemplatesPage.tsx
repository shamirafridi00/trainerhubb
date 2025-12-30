import { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { apiClient } from '@/api/client';

interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  body: string;
  variables: string[];
  created_at: string;
}

export default function EmailTemplatesPage() {
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    body: '',
  });

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await apiClient.get('/workflows/email-templates/');
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to fetch email templates:', error);
    }
  };

  const handleSave = async () => {
    try {
      if (editingTemplate) {
        await apiClient.put(`/workflows/email-templates/${editingTemplate.id}/`, formData);
      } else {
        await apiClient.post('/workflows/email-templates/', formData);
      }
      setIsDialogOpen(false);
      setEditingTemplate(null);
      setFormData({ name: '', subject: '', body: '' });
      fetchTemplates();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to save template');
    }
  };

  const handleEdit = (template: EmailTemplate) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      subject: template.subject,
      body: template.body,
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Delete template "${name}"?`)) return;

    try {
      await apiClient.delete(`/workflows/email-templates/${id}/`);
      fetchTemplates();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete template');
    }
  };

  const handleNew = () => {
    setEditingTemplate(null);
    setFormData({ name: '', subject: '', body: '' });
    setIsDialogOpen(true);
  };

  const AVAILABLE_VARIABLES = [
    'client_name', 'client_email', 'trainer_name', 'trainer_email',
    'booking_date', 'booking_time', 'booking_service', 'booking_location',
    'payment_amount', 'package_name'
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Email Templates</h1>
          <p className="text-gray-600">Create reusable email templates for workflows</p>
        </div>
        <Button onClick={handleNew}>
          <Plus className="h-4 w-4 mr-2" />
          New Template
        </Button>
      </div>

      {templates.length === 0 ? (
        <div className="bg-white rounded-lg border-2 border-dashed p-12 text-center">
          <Mail className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No templates yet</h2>
          <p className="text-gray-600 mb-4">Create your first email template</p>
          <Button onClick={handleNew}>
            <Plus className="h-4 w-4 mr-2" />
            Create Template
          </Button>
        </div>
      ) : (
        <div className="grid gap-4">
          {templates.map((template) => (
            <div key={template.id} className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">{template.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Subject:</strong> {template.subject}
                  </p>
                  <p className="text-sm text-gray-600 line-clamp-2">{template.body}</p>
                </div>
                <div className="flex gap-2 ml-4">
                  <Button variant="ghost" size="icon" onClick={() => handleEdit(template)}>
                    <Edit className="h-4 w-4 text-blue-500" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => handleDelete(template.id, template.name)}>
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingTemplate ? 'Edit' : 'Create'} Email Template</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Template Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Booking Confirmation"
              />
            </div>
            <div>
              <Label htmlFor="subject">Subject</Label>
              <Input
                id="subject"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                placeholder="Your booking is confirmed"
              />
            </div>
            <div>
              <Label htmlFor="body">Email Body</Label>
              <Textarea
                id="body"
                value={formData.body}
                onChange={(e) => setFormData({ ...formData, body: e.target.value })}
                placeholder="Hi {{client_name}}, your booking for {{booking_date}} is confirmed..."
                rows={10}
              />
              <div className="mt-2">
                <p className="text-xs text-gray-600 mb-1">Available variables:</p>
                <div className="flex flex-wrap gap-1">
                  {AVAILABLE_VARIABLES.map((v) => (
                    <code key={v} className="text-xs px-2 py-1 bg-gray-100 rounded">{`{{${v}}}`}</code>
                  ))}
                </div>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSave}>Save Template</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

