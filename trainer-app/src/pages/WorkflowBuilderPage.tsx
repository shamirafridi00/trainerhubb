import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Save, ArrowLeft, Play, PlayCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { TriggerSelector } from '@/components/WorkflowBuilder/TriggerSelector';
import { ActionList } from '@/components/WorkflowBuilder/ActionList';
import { ActionForm } from '@/components/WorkflowBuilder/ActionForm';
import { apiClient } from '@/api/client';

interface WorkflowAction {
  id?: string;
  action_type: string;
  action_data: Record<string, any>;
  order: number;
}

interface TriggerConfig {
  trigger_type: string;
  conditions: Record<string, any>;
  delay_minutes: number;
}

interface WorkflowData {
  id?: number;
  name: string;
  description: string;
  is_active: boolean;
  trigger: TriggerConfig;
  actions: WorkflowAction[];
}

// Available variables that can be used in email/SMS templates
const AVAILABLE_VARIABLES = [
  { name: 'client_name', description: 'Client full name' },
  { name: 'client_email', description: 'Client email address' },
  { name: 'client_phone', description: 'Client phone number' },
  { name: 'trainer_name', description: 'Your business name' },
  { name: 'trainer_email', description: 'Your email address' },
  { name: 'trainer_phone', description: 'Your phone number' },
  { name: 'booking_date', description: 'Booking date' },
  { name: 'booking_time', description: 'Booking start time' },
  { name: 'booking_end_time', description: 'Booking end time' },
  { name: 'booking_service', description: 'Service name' },
  { name: 'booking_location', description: 'Booking location' },
  { name: 'payment_amount', description: 'Payment amount' },
  { name: 'payment_method', description: 'Payment method' },
  { name: 'package_name', description: 'Package name' },
  { name: 'package_sessions', description: 'Number of sessions' },
];

export default function WorkflowBuilderPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [workflow, setWorkflow] = useState<WorkflowData>({
    name: '',
    description: '',
    is_active: true,
    trigger: {
      trigger_type: 'booking_created',
      conditions: {},
      delay_minutes: 0,
    },
    actions: [],
  });

  const [selectedActionIndex, setSelectedActionIndex] = useState<number | null>(null);
  const [isAddingAction, setIsAddingAction] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchWorkflow();
    }
  }, [id]);

  const fetchWorkflow = async () => {
    try {
      const response = await apiClient.get(`/workflows/workflows/${id}/`);
      setWorkflow(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load workflow');
    }
  };

  const handleSave = async () => {
    if (!workflow.name) {
      setError('Workflow name is required');
      return;
    }

    if (!workflow.trigger.trigger_type) {
      setError('Please select a trigger');
      return;
    }

    if (workflow.actions.length === 0) {
      setError('Please add at least one action');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      if (isEditing) {
        await apiClient.put(`/workflows/workflows/${id}/`, workflow);
      } else {
        await apiClient.post('/workflows/workflows/', workflow);
      }
      navigate('/workflows');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save workflow');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddAction = () => {
    setIsAddingAction(true);
    setSelectedActionIndex(null);
  };

  const handleSaveAction = (action: WorkflowAction) => {
    if (selectedActionIndex !== null) {
      // Edit existing action
      const updatedActions = [...workflow.actions];
      updatedActions[selectedActionIndex] = action;
      setWorkflow({ ...workflow, actions: updatedActions });
    } else {
      // Add new action
      setWorkflow({
        ...workflow,
        actions: [...workflow.actions, { ...action, order: workflow.actions.length }],
      });
    }
    setIsAddingAction(false);
    setSelectedActionIndex(null);
  };

  const handleDeleteAction = (index: number) => {
    const updatedActions = workflow.actions
      .filter((_, i) => i !== index)
      .map((action, i) => ({ ...action, order: i }));
    setWorkflow({ ...workflow, actions: updatedActions });
    setSelectedActionIndex(null);
  };

  const handleSelectAction = (index: number) => {
    setSelectedActionIndex(index);
    setIsAddingAction(false);
  };

  const handleTestWorkflow = async () => {
    alert('Test workflow feature coming soon! This will simulate the workflow execution.');
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/workflows')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">
              {isEditing ? 'Edit Workflow' : 'Create Workflow'}
            </h1>
            <p className="text-gray-600">Automate your business processes</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleTestWorkflow}>
            <PlayCircle className="h-4 w-4 mr-2" />
            Test
          </Button>
          <Button onClick={handleSave} disabled={isSaving}>
            <Save className="h-4 w-4 mr-2" />
            {isSaving ? 'Saving...' : 'Save Workflow'}
          </Button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Workflow Info */}
      <div className="bg-white rounded-lg border p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Workflow Details</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="name">Workflow Name *</Label>
            <Input
              id="name"
              value={workflow.name}
              onChange={(e) => setWorkflow({ ...workflow, name: e.target.value })}
              placeholder="e.g., Send booking confirmation"
              required
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={workflow.is_active}
              onChange={(e) => setWorkflow({ ...workflow, is_active: e.target.checked })}
              className="h-4 w-4"
            />
            <Label htmlFor="is_active" className="cursor-pointer">
              Active (workflow will run automatically)
            </Label>
          </div>
        </div>
        <div className="mt-4">
          <Label htmlFor="description">Description (optional)</Label>
          <Textarea
            id="description"
            value={workflow.description}
            onChange={(e) => setWorkflow({ ...workflow, description: e.target.value })}
            placeholder="Describe what this workflow does..."
            rows={2}
          />
        </div>
      </div>

      {/* Workflow Builder */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Column - Trigger & Actions */}
        <div className="space-y-6">
          {/* Step 1: Trigger */}
          <TriggerSelector
            trigger={workflow.trigger}
            onChange={(trigger) => setWorkflow({ ...workflow, trigger })}
          />

          {/* Step 2: Actions */}
          <ActionList
            actions={workflow.actions}
            selectedActionIndex={selectedActionIndex}
            onActionsChange={(actions) => setWorkflow({ ...workflow, actions })}
            onSelectAction={handleSelectAction}
            onAddAction={handleAddAction}
            onDeleteAction={handleDeleteAction}
          />
        </div>

        {/* Right Column - Action Form */}
        <div className="lg:sticky lg:top-6 h-fit">
          {(isAddingAction || selectedActionIndex !== null) && (
            <ActionForm
              action={selectedActionIndex !== null ? workflow.actions[selectedActionIndex] : null}
              onSave={handleSaveAction}
              onCancel={() => {
                setIsAddingAction(false);
                setSelectedActionIndex(null);
              }}
              availableVariables={AVAILABLE_VARIABLES}
            />
          )}

          {!isAddingAction && selectedActionIndex === null && (
            <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
              <p className="text-gray-500 mb-4">
                Select an action to edit it, or add a new action to get started.
              </p>
              <Button onClick={handleAddAction} variant="outline">
                Add Action
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Available Variables Reference */}
      <div className="mt-8 bg-blue-50 rounded-lg border border-blue-200 p-6">
        <h3 className="font-semibold mb-3">💡 Available Variables</h3>
        <p className="text-sm text-gray-700 mb-3">
          You can use these variables in your email subjects, email bodies, and SMS messages. They will be automatically replaced with actual values when the workflow runs.
        </p>
        <div className="grid md:grid-cols-3 gap-2 text-sm">
          {AVAILABLE_VARIABLES.map((v) => (
            <div key={v.name} className="bg-white p-2 rounded">
              <code className="text-blue-600">{`{{${v.name}}}`}</code>
              <p className="text-xs text-gray-600 mt-1">{v.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

