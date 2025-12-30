import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Play, Pause, Edit, Trash2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/api/client';

interface Workflow {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  trigger: {
    trigger_type: string;
    delay_minutes: number;
  };
  actions: Array<{
    action_type: string;
    order: number;
  }>;
  created_at: string;
  updated_at: string;
}

export default function WorkflowListPage() {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      const response = await apiClient.get('/workflows/workflows/');
      setWorkflows(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load workflows');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleActive = async (id: number, currentStatus: boolean) => {
    try {
      const endpoint = currentStatus ? 'deactivate' : 'activate';
      await apiClient.post(`/workflows/workflows/${id}/${endpoint}/`);
      fetchWorkflows();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update workflow');
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"? This cannot be undone.`)) {
      return;
    }

    try {
      await apiClient.delete(`/workflows/workflows/${id}/`);
      fetchWorkflows();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete workflow');
    }
  };

  const getTriggerLabel = (triggerType: string) => {
    const labels: Record<string, string> = {
      booking_created: 'Booking Created',
      booking_confirmed: 'Booking Confirmed',
      booking_cancelled: 'Booking Cancelled',
      booking_reminder: 'Booking Reminder',
      payment_received: 'Payment Received',
      client_created: 'Client Created',
      package_purchased: 'Package Purchased',
    };
    return labels[triggerType] || triggerType;
  };

  const getActionLabel = (actionType: string) => {
    const labels: Record<string, string> = {
      send_email: 'Send Email',
      send_sms: 'Send SMS',
      update_status: 'Update Status',
      create_note: 'Create Note',
    };
    return labels[actionType] || actionType;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading workflows...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Workflows</h1>
          <p className="text-gray-600">Automate your business processes</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/workflows/templates')}>
            Browse Templates
          </Button>
          <Button onClick={() => navigate('/workflows/new')}>
            <Plus className="h-4 w-4 mr-2" />
            Create Workflow
          </Button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          {error}
        </div>
      )}

      {/* Workflows List */}
      {workflows.length === 0 ? (
        <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <div className="max-w-md mx-auto">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Play className="h-8 w-8 text-blue-600" />
            </div>
            <h2 className="text-2xl font-semibold mb-2">No workflows yet</h2>
            <p className="text-gray-600 mb-6">
              Automate repetitive tasks like sending booking confirmations, payment reminders, and more.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button variant="outline" onClick={() => navigate('/workflows/templates')}>
                Browse Templates
              </Button>
              <Button onClick={() => navigate('/workflows/new')}>
                <Plus className="h-4 w-4 mr-2" />
                Create From Scratch
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid gap-4">
          {workflows.map((workflow) => (
            <div
              key={workflow.id}
              className="bg-white rounded-lg border hover:shadow-md transition-shadow p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">{workflow.name}</h3>
                    <Badge variant={workflow.is_active ? 'default' : 'secondary'}>
                      {workflow.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>

                  {workflow.description && (
                    <p className="text-gray-600 mb-4">{workflow.description}</p>
                  )}

                  <div className="flex flex-wrap items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-700">When:</span>
                      <Badge variant="outline">{getTriggerLabel(workflow.trigger.trigger_type)}</Badge>
                      {workflow.trigger.delay_minutes > 0 && (
                        <span className="text-gray-500">+{workflow.trigger.delay_minutes}min</span>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-700">Then:</span>
                      {workflow.actions.map((action, idx) => (
                        <Badge key={idx} variant="outline">
                          {getActionLabel(action.action_type)}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="mt-3 text-xs text-gray-500">
                    Last updated: {new Date(workflow.updated_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex items-center gap-2 ml-4">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleToggleActive(workflow.id, workflow.is_active)}
                    title={workflow.is_active ? 'Deactivate' : 'Activate'}
                  >
                    {workflow.is_active ? (
                      <Pause className="h-4 w-4 text-orange-500" />
                    ) : (
                      <Play className="h-4 w-4 text-green-500" />
                    )}
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => navigate(`/workflows/${workflow.id}/edit`)}
                    title="Edit"
                  >
                    <Edit className="h-4 w-4 text-blue-500" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(workflow.id, workflow.name)}
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 bg-blue-50 rounded-lg border border-blue-200 p-6">
        <h3 className="font-semibold mb-2">💡 What are workflows?</h3>
        <p className="text-sm text-gray-700">
          Workflows help you automate repetitive tasks. For example, you can automatically send a confirmation email when a booking is created, or send a reminder SMS 24 hours before a session. Set up once and let it run automatically!
        </p>
      </div>
    </div>
  );
}

