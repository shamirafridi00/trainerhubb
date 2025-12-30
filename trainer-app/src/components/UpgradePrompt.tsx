import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Lock, ArrowRight } from 'lucide-react';

interface UpgradePromptProps {
  feature: string;
  requiredPlan: 'pro' | 'business';
  title?: string;
  description?: string;
}

const featureNames: Record<string, string> = {
  custom_domain: 'Custom Domain',
  white_label: 'White Label Branding',
  workflows: 'Workflow Automation',
  advanced_analytics: 'Advanced Analytics',
};

const planPrices: Record<string, string> = {
  pro: '$29/month',
  business: '$79/month',
};

export function UpgradePrompt({ 
  feature, 
  requiredPlan, 
  title, 
  description 
}: UpgradePromptProps) {
  const featureName = featureNames[feature] || feature;
  const defaultTitle = `Upgrade to ${requiredPlan.charAt(0).toUpperCase() + requiredPlan.slice(1)} to unlock ${featureName}`;
  const defaultDescription = `This feature is available on the ${requiredPlan.charAt(0).toUpperCase() + requiredPlan.slice(1)} plan (${planPrices[requiredPlan]}).`;

  return (
    <Card className="border-2 border-dashed">
      <CardHeader>
        <div className="flex items-center gap-2 mb-2">
          <Lock className="h-5 w-5 text-muted-foreground" />
          <CardTitle className="text-lg">{title || defaultTitle}</CardTitle>
        </div>
        <CardDescription>
          {description || defaultDescription}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Upgrade your plan to access:
          </p>
          <ul className="list-disc list-inside text-sm space-y-1">
            {requiredPlan === 'pro' && (
              <>
                <li>Unlimited clients</li>
                <li>Up to 5 pages</li>
                <li>All 10 templates</li>
                <li>3 workflow automations</li>
                <li>1,000 emails/month</li>
                <li>100 SMS/month</li>
              </>
            )}
            {requiredPlan === 'business' && (
              <>
                <li>Everything in Pro</li>
                <li>Unlimited pages</li>
                <li>Custom domain support</li>
                <li>White-label branding</li>
                <li>Unlimited workflows</li>
                <li>Unlimited emails</li>
                <li>500 SMS/month</li>
              </>
            )}
          </ul>
        </div>
      </CardContent>
      <CardFooter>
        <Link to="/settings/billing" className="w-full">
          <Button className="w-full">
            Upgrade to {requiredPlan.charAt(0).toUpperCase() + requiredPlan.slice(1)}
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}

