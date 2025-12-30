import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';

interface WorkflowAction {
  action_type: string;
  action_data: Record<string, any>;
  order: number;
}

interface ActionFormProps {
  action: WorkflowAction | null;
  onSave: (action: WorkflowAction) => void;
  onCancel: () => void;
  availableVariables: Array<{ name: string; description: string }>;
}

const ACTION_TYPES = [
  { value: 'send_email', label: 'Send Email' },
  { value: 'send_sms', label: 'Send SMS' },
  { value: 'update_status', label: 'Update Status' },
  { value: 'create_note', label: 'Create Note' },
];

export function ActionForm({ action, onSave, onCancel, availableVariables }: ActionFormProps) {
  const [formData, setFormData] = useState<WorkflowAction>(
    action || {
      action_type: 'send_email',
      action_data: {},
      order: 0,
    }
  );

  const insertVariable = (variable: string, field: 'subject' | 'body' | 'message' | 'content') => {
    const currentValue = formData.action_data[field] || '';
    setFormData({
      ...formData,
      action_data: {
        ...formData.action_data,
        [field]: `${currentValue}{{${variable}}}`,
      },
    });
  };

  const renderVariablePicker = (field: 'subject' | 'body' | 'message' | 'content') => (
    <div className="mt-2">
      <p className="text-xs text-gray-600 mb-1">Insert variable:</p>
      <div className="flex flex-wrap gap-1">
        {availableVariables.map((v) => (
          <button
            key={v.name}
            type="button"
            onClick={() => insertVariable(v.name, field)}
            className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded"
            title={v.description}
          >
            {`{{${v.name}}}`}
          </button>
        ))}
      </div>
    </div>
  );

  const renderActionFields = () => {
    switch (formData.action_type) {
      case 'send_email':
        return (
          <>
            <div>
              <Label htmlFor="recipient">Recipient (optional)</Label>
              <Input
                id="recipient"
                value={formData.action_data.recipient || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    action_data: { ...formData.action_data, recipient: e.target.value },
                  })
                }
                placeholder="email@example.com or leave empty for client email"
              />
              <p className="text-xs text-gray-500 mt-1">
                Leave empty to send to the client's email address
              </p>
            </div>

            <div>
              <Label htmlFor="subject">Subject *</Label>
              <Input
                id="subject"
                value={formData.action_data.subject || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    action_data: { ...formData.action_data, subject: e.target.value },
                  })
                }
                placeholder="Your booking is confirmed"
                required
              />
              {renderVariablePicker('subject')}
            </div>

            <div>
              <Label htmlFor="body">Email Body *</Label>
              <Textarea
                id="body"
                value={formData.action_data.body || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    action_data: { ...formData.action_data, body: e.target.value },
                  })
                }
                placeholder="Hi {{client_name}}, your booking for {{booking_date}} is confirmed..."
                rows={8}
                required
              />
              {renderVariablePicker('body')}
            </div>
          </>
        );

      case 'send_sms':
        return (
          <>
            <div>
              <Label htmlFor="recipient">Recipient (optional)</Label>
              <Input
                id="recipient"
                value={formData.action_data.recipient || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    action_data: { ...formData.action_data, recipient: e.target.value },
                  })
                }
                placeholder="+1234567890 or leave empty for client phone"
              />
              <p className="text-xs text-gray-500 mt-1">
                Leave empty to send to the client's phone number
              </p>
            </div>

            <div>
              <Label htmlFor="message">SMS Message * (max 160 characters)</Label>
              <Textarea
                id="message"
                value={formData.action_data.message || ''}
                onChange={(e) => {
                  const value = e.target.value.substring(0, 160);
                  setFormData({
                    ...formData,
                    action_data: { ...formData.action_data, message: value },
                  });
                }}
                placeholder="Hi {{client_name}}, reminder: {{booking_date}} at {{booking_time}}"
                rows={4}
                maxLength={160}
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                {(formData.action_data.message || '').length}/160 characters
              </p>
              {renderVariablePicker('message')}
            </div>
          </>
        );

      case 'update_status':
        return (
          <>
            <div>
              <Label htmlFor="model_type">Update What?</Label>
              <Select
                value={formData.action_data.model_type || 'booking'}
                onValueChange={(value) =>
                  setFormData({
                    ...formData,
                    action_data: { ...formData.action_data, model_type: value },
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="booking">Booking</SelectItem>
                  <SelectItem value="client">Client</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="status">New Status</Label>
              <Input
                id="status"
                value={formData.action_data.status || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    action_data: { ...formData.action_data, status: e.target.value },
                  })
                }
                placeholder="confirmed, completed, etc."
                required
              />
            </div>
          </>
        );

      case 'create_note':
        return (
          <>
            <div>
              <Label htmlFor="model_type">Add Note To</Label>
              <Select
                value={formData.action_data.model_type || 'booking'}
                onValueChange={(value) =>
                  setFormData({
                    ...formData,
                    action_data: { ...formData.action_data, model_type: value },
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="booking">Booking</SelectItem>
                  <SelectItem value="client">Client</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="content">Note Content *</Label>
              <Textarea
                id="content"
                value={formData.action_data.content || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    action_data: { ...formData.action_data, content: e.target.value },
                  })
                }
                placeholder="Automated note: {{client_name}} booking confirmed on {{booking_date}}"
                rows={4}
                required
              />
              {renderVariablePicker('content')}
            </div>
          </>
        );

      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg border-2 border-purple-500 p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <span className="bg-purple-500 text-white w-8 h-8 rounded-full flex items-center justify-center text-sm">
          3
        </span>
        Configure Action
      </h3>

      <div className="space-y-4">
        <div>
          <Label htmlFor="action_type">Action Type</Label>
          <Select
            value={formData.action_type}
            onValueChange={(value) =>
              setFormData({ ...formData, action_type: value, action_data: {} })
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ACTION_TYPES.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {renderActionFields()}

        <div className="flex gap-2 pt-4">
          <Button onClick={onCancel} variant="outline" className="flex-1">
            Cancel
          </Button>
          <Button
            onClick={() => onSave(formData)}
            className="flex-1"
          >
            Save Action
          </Button>
        </div>
      </div>
    </div>
  );
}

