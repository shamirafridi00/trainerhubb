import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Zap, Calendar, DollarSign, User, Bell, Package, CheckSquare, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/api/client';

interface WorkflowTemplate {
  id: number;
  name: string;
  description: string;
  category: string;
  category_display: string;
  icon: string;
  trigger_type: string;
  trigger_delay_minutes: number;
  actions_config: Array<{
    action_type: string;
    action_data: any;
    order: number;
  }>;
  times_used: number;
}

export default function WorkflowTemplatesPage() {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await apiClient.get('/workflows/templates/');
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUseTemplate = async (templateId: number, templateName: string) => {
    if (!confirm(`Create a new workflow from "${templateName}"? You can customize it after creation.`)) {
      return;
    }

    try {
      const response = await apiClient.post(`/workflows/templates/${templateId}/use_template/`);
      navigate(`/workflows/${response.data.id}/edit`);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to use template');
    }
  };

  const getIcon = (iconName: string) => {
    const icons: Record<string, any> = {
      'calendar-check': Calendar,
      'bell': Bell,
      'dollar-sign': DollarSign,
      'user-plus': User,
      'x-circle': Calendar,
      'package': Package,
      'message-square': MessageSquare,
      'check-square': CheckSquare,
    };
    const Icon = icons[iconName] || Zap;
    return <Icon className="h-6 w-6" />;
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      booking: 'bg-blue-100 text-blue-700',
      payment: 'bg-green-100 text-green-700',
      client: 'bg-purple-100 text-purple-700',
      reminder: 'bg-orange-100 text-orange-700',
      general: 'bg-gray-100 text-gray-700',
    };
    return colors[category] || colors.general;
  };

  const categories = [
    { value: 'all', label: 'All Templates' },
    { value: 'booking', label: 'Booking Management' },
    { value: 'payment', label: 'Payment & Billing' },
    { value: 'client', label: 'Client Communication' },
    { value: 'reminder', label: 'Reminders' },
  ];

  const filteredTemplates = selectedCategory === 'all'
    ? templates
    : templates.filter(t => t.category === selectedCategory);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading templates...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Button variant="ghost" size="icon" onClick={() => navigate('/workflows')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold mb-2">Workflow Templates</h1>
          <p className="text-gray-600">Start with a pre-built workflow and customize it to your needs</p>
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map((cat) => (
          <Button
            key={cat.value}
            variant={selectedCategory === cat.value ? 'default' : 'outline'}
            onClick={() => setSelectedCategory(cat.value)}
          >
            {cat.label}
          </Button>
        ))}
      </div>

      {/* Templates Grid */}
      {filteredTemplates.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p>No templates found in this category.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <div
              key={template.id}
              className="bg-white rounded-lg border hover:shadow-lg transition-shadow p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-lg ${getCategoryColor(template.category)}`}>
                  {getIcon(template.icon)}
                </div>
                <Badge variant="outline">{template.category_display}</Badge>
              </div>

              <h3 className="text-xl font-semibold mb-2">{template.name}</h3>
              <p className="text-gray-600 text-sm mb-4">{template.description}</p>

              <div className="space-y-2 mb-4">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Zap className="h-4 w-4" />
                  <span>
                    {template.actions_config.length} action{template.actions_config.length !== 1 ? 's' : ''}
                  </span>
                </div>
                {template.times_used > 0 && (
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <CheckSquare className="h-4 w-4" />
                    <span>Used by {template.times_used} trainer{template.times_used !== 1 ? 's' : ''}</span>
                  </div>
                )}
              </div>

              <Button
                onClick={() => handleUseTemplate(template.id, template.name)}
                className="w-full"
              >
                Use This Template
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div className="mt-12 bg-blue-50 rounded-lg border border-blue-200 p-6">
        <h3 className="font-semibold mb-2">💡 How to use templates</h3>
        <ol className="text-sm text-gray-700 space-y-2 list-decimal list-inside">
          <li>Choose a template that matches your needs</li>
          <li>Click "Use This Template" to create a new workflow</li>
          <li>Customize the workflow settings, email content, and timing</li>
          <li>Activate the workflow when you're ready to use it</li>
        </ol>
      </div>
    </div>
  );
}

