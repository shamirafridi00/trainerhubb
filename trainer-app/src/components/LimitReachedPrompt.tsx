import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, ArrowRight } from 'lucide-react';

interface LimitReachedPromptProps {
  resource: string;
  currentCount: number;
  limit: number;
  title?: string;
  description?: string;
}

const resourceNames: Record<string, string> = {
  clients: 'Clients',
  pages: 'Pages',
  workflows: 'Workflows',
  emails: 'Emails',
  sms: 'SMS Messages',
};

export function LimitReachedPrompt({ 
  resource, 
  currentCount, 
  limit,
  title, 
  description 
}: LimitReachedPromptProps) {
  const resourceName = resourceNames[resource] || resource;
  const defaultTitle = `${resourceName} Limit Reached`;
  const defaultDescription = `You've reached your limit of ${limit} ${resourceName.toLowerCase()}. Upgrade to add more.`;

  return (
    <Card className="border-2 border-yellow-500/50 bg-yellow-50 dark:bg-yellow-950/10">
      <CardHeader>
        <div className="flex items-center gap-2 mb-2">
          <AlertCircle className="h-5 w-5 text-yellow-600" />
          <CardTitle className="text-lg">{title || defaultTitle}</CardTitle>
        </div>
        <CardDescription className="text-yellow-700 dark:text-yellow-400">
          {description || defaultDescription}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-white dark:bg-gray-900 rounded-lg">
            <span className="text-sm font-medium">Current Usage</span>
            <span className="text-lg font-bold">{currentCount} / {limit}</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Upgrade to Pro or Business plan for:
          </p>
          <ul className="list-disc list-inside text-sm space-y-1">
            <li><strong>Pro Plan:</strong> 
              {resource === 'clients' ? ' Unlimited clients' : ''}
              {resource === 'pages' ? ' Up to 5 pages' : ''}
              {resource === 'workflows' ? ' 3 workflows' : ''}
            </li>
            <li><strong>Business Plan:</strong> 
              {resource === 'clients' ? ' Unlimited clients' : ''}
              {resource === 'pages' ? ' Unlimited pages' : ''}
              {resource === 'workflows' ? ' Unlimited workflows' : ''}
            </li>
          </ul>
        </div>
      </CardContent>
      <CardFooter className="flex gap-2">
        <Link to="/settings/billing" className="flex-1">
          <Button className="w-full">
            View Plans
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}

