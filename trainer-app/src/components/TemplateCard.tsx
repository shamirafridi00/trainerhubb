import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Eye, Crown } from 'lucide-react';
import type { PageTemplate } from '@/types';

interface TemplateCardProps {
  template: PageTemplate;
  onApply: (template: PageTemplate) => void;
  onPreview: (template: PageTemplate) => void;
}

export function TemplateCard({ template, onApply, onPreview }: TemplateCardProps) {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <div className="relative">
        {template.thumbnail ? (
          <img
            src={template.thumbnail}
            alt={template.name}
            className="w-full h-48 object-cover"
          />
        ) : (
          <div className="w-full h-48 bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
            <span className="text-white text-2xl font-bold">{template.name[0]}</span>
          </div>
        )}
        {template.is_premium && (
          <Badge className="absolute top-2 right-2 bg-yellow-500 text-white">
            <Crown className="h-3 w-3 mr-1" />
            Premium
          </Badge>
        )}
      </div>
      
      <CardHeader>
        <CardTitle className="text-lg">{template.name}</CardTitle>
        <CardDescription>{template.description}</CardDescription>
      </CardHeader>
      
      <CardContent>
        <div className="flex flex-wrap gap-1">
          <Badge variant="outline" className="text-xs">
            {template.category}
          </Badge>
          {template.available_for_plans.map((plan) => (
            <Badge key={plan} variant="secondary" className="text-xs">
              {plan}
            </Badge>
          ))}
        </div>
      </CardContent>
      
      <CardFooter className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          className="flex-1"
          onClick={() => onPreview(template)}
        >
          <Eye className="h-3 w-3 mr-1" />
          Preview
        </Button>
        <Button
          size="sm"
          className="flex-1"
          onClick={() => onApply(template)}
        >
          Use Template
        </Button>
      </CardFooter>
    </Card>
  );
}

