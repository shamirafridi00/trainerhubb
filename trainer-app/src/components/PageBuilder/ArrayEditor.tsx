import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react';

interface Field {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'number' | 'url';
  placeholder?: string;
  rows?: number;
}

interface ArrayEditorProps {
  items: any[];
  fields: Field[];
  itemName: string;
  onChange: (items: any[]) => void;
}

export function ArrayEditor({ items, fields, itemName, onChange }: ArrayEditorProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const addItem = () => {
    const newItem: any = {};
    fields.forEach((field) => {
      newItem[field.name] = field.type === 'number' ? 0 : '';
    });
    onChange([...items, newItem]);
    setExpandedIndex(items.length);
  };

  const updateItem = (index: number, field: string, value: any) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    onChange(newItems);
  };

  const deleteItem = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    onChange(newItems);
    if (expandedIndex === index) {
      setExpandedIndex(null);
    }
  };

  const moveItem = (index: number, direction: 'up' | 'down') => {
    const newItems = [...items];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= items.length) return;
    
    [newItems[index], newItems[targetIndex]] = [newItems[targetIndex], newItems[index]];
    onChange(newItems);
    setExpandedIndex(targetIndex);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label className="text-sm font-medium">{itemName}s</Label>
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={addItem}
        >
          <Plus className="h-3 w-3 mr-1" />
          Add {itemName}
        </Button>
      </div>

      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground py-4 text-center border-2 border-dashed rounded">
          No {itemName.toLowerCase()}s yet. Click "Add {itemName}" to get started.
        </p>
      ) : (
        <div className="space-y-2">
          {items.map((item, index) => (
            <div key={index} className="border rounded-lg">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-t-lg">
                <button
                  type="button"
                  onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
                  className="flex items-center gap-2 flex-1 text-left text-sm font-medium"
                >
                  {expandedIndex === index ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                  {itemName} #{index + 1}
                  {item[fields[0]?.name] && (
                    <span className="text-muted-foreground">
                      - {item[fields[0].name]}
                    </span>
                  )}
                </button>
                <div className="flex items-center gap-1">
                  {index > 0 && (
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => moveItem(index, 'up')}
                    >
                      ↑
                    </Button>
                  )}
                  {index < items.length - 1 && (
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => moveItem(index, 'down')}
                    >
                      ↓
                    </Button>
                  )}
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    onClick={() => deleteItem(index)}
                  >
                    <Trash2 className="h-3 w-3 text-red-500" />
                  </Button>
                </div>
              </div>

              {expandedIndex === index && (
                <div className="p-3 space-y-3">
                  {fields.map((field) => (
                    <div key={field.name}>
                      <Label htmlFor={`${index}-${field.name}`} className="text-sm">
                        {field.label}
                      </Label>
                      {field.type === 'textarea' ? (
                        <Textarea
                          id={`${index}-${field.name}`}
                          value={item[field.name] || ''}
                          onChange={(e) => updateItem(index, field.name, e.target.value)}
                          placeholder={field.placeholder}
                          rows={field.rows || 3}
                          className="mt-1"
                        />
                      ) : (
                        <Input
                          id={`${index}-${field.name}`}
                          type={field.type === 'number' ? 'number' : 'text'}
                          value={item[field.name] || ''}
                          onChange={(e) =>
                            updateItem(
                              index,
                              field.name,
                              field.type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value
                            )
                          }
                          placeholder={field.placeholder}
                          className="mt-1"
                        />
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

