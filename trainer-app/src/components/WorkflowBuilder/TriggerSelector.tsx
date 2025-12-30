import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';

interface TriggerConfig {
  trigger_type: string;
  conditions: Record<string, any>;
  delay_minutes: number;
}

interface TriggerSelectorProps {
  trigger: TriggerConfig;
  onChange: (trigger: TriggerConfig) => void;
}

const TRIGGER_TYPES = [
  { value: 'booking_created', label: 'Booking Created', description: 'When a new booking is created' },
  { value: 'booking_confirmed', label: 'Booking Confirmed', description: 'When a booking is confirmed' },
  { value: 'booking_cancelled', label: 'Booking Cancelled', description: 'When a booking is cancelled' },
  { value: 'booking_reminder', label: 'Booking Reminder', description: 'Send reminder before booking' },
  { value: 'payment_received', label: 'Payment Received', description: 'When payment is recorded' },
  { value: 'client_created', label: 'Client Created', description: 'When a new client is added' },
  { value: 'package_purchased', label: 'Package Purchased', description: 'When client buys a package' },
];

export function TriggerSelector({ trigger, onChange }: TriggerSelectorProps) {
  const selectedTrigger = TRIGGER_TYPES.find(t => t.value === trigger.trigger_type);

  return (
    <div className="bg-white rounded-lg border-2 border-blue-500 p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <span className="bg-blue-500 text-white w-8 h-8 rounded-full flex items-center justify-center text-sm">
          1
        </span>
        When should this workflow run?
      </h3>

      <div className="space-y-4">
        <div>
          <Label htmlFor="trigger_type">Trigger Event</Label>
          <Select
            value={trigger.trigger_type}
            onValueChange={(value) => onChange({ ...trigger, trigger_type: value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select a trigger..." />
            </SelectTrigger>
            <SelectContent>
              {TRIGGER_TYPES.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  <div>
                    <div className="font-medium">{type.label}</div>
                    <div className="text-xs text-gray-500">{type.description}</div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {selectedTrigger && (
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-700">
              <strong>When:</strong> {selectedTrigger.description}
            </p>
          </div>
        )}

        <div>
          <Label htmlFor="delay_minutes">Delay (optional)</Label>
          <div className="flex items-center gap-2">
            <Input
              id="delay_minutes"
              type="number"
              min="0"
              value={trigger.delay_minutes}
              onChange={(e) => onChange({ ...trigger, delay_minutes: parseInt(e.target.value) || 0 })}
              className="w-24"
            />
            <span className="text-sm text-gray-600">minutes after trigger</span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Leave at 0 to run immediately, or set a delay (e.g., 60 for 1 hour before)
          </p>
        </div>

        {trigger.trigger_type === 'booking_reminder' && (
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              <strong>Tip:</strong> For booking reminders, set delay to a negative number (e.g., -1440 for 24 hours before the booking)
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

