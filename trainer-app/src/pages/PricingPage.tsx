import { useState } from 'react';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuthStore } from '@/store/authStore';

interface PricingPlan {
  id: string;
  name: string;
  price: string;
  priceAnnual: string;
  description: string;
  features: string[];
  popular?: boolean;
  paddleProductId?: string;
}

const plans: PricingPlan[] = [
  {
    id: 'free',
    name: 'Free',
    price: '$0',
    priceAnnual: '$0',
    description: 'Perfect for getting started',
    features: [
      '10 clients',
      '1 page',
      '3 basic templates',
      'Custom subdomain',
      '100 emails/month',
      'Basic analytics',
    ],
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$29',
    priceAnnual: '$290',
    description: 'For growing training businesses',
    popular: true,
    paddleProductId: 'pro_plan_id',
    features: [
      'Unlimited clients',
      'Up to 5 pages',
      'All 10 templates',
      'Custom subdomain',
      '3 workflow automations',
      '1,000 emails/month',
      '100 SMS/month',
      'Advanced analytics',
      'Email support',
    ],
  },
  {
    id: 'business',
    name: 'Business',
    price: '$79',
    priceAnnual: '$790',
    description: 'For established businesses',
    paddleProductId: 'business_plan_id',
    features: [
      'Everything in Pro',
      'Unlimited pages',
      'Custom domain support',
      'White-label branding',
      'Unlimited workflows',
      'Unlimited emails',
      '500 SMS/month',
      'Priority support',
      'Export analytics',
    ],
  },
];

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  const { user } = useAuthStore();

  const handleSelectPlan = (plan: PricingPlan) => {
    if (plan.id === 'free') {
      // Downgrade to free
      alert('Downgrade functionality coming soon');
      return;
    }

    // TODO: Integrate Paddle Checkout
    alert(`Paddle checkout for ${plan.name} plan (${billingCycle}) coming soon`);
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
        <p className="text-xl text-muted-foreground mb-8">
          Select the plan that's right for your training business
        </p>
        
        {/* Billing cycle toggle */}
        <div className="inline-flex items-center gap-4 p-1 bg-muted rounded-lg">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-6 py-2 rounded-md transition-colors ${
              billingCycle === 'monthly'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle('annual')}
            className={`px-6 py-2 rounded-md transition-colors ${
              billingCycle === 'annual'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Annual
            <span className="ml-2 text-xs bg-green-500 text-white px-2 py-1 rounded">
              Save 20%
            </span>
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        {plans.map((plan) => (
          <Card
            key={plan.id}
            className={`relative ${
              plan.popular ? 'border-primary shadow-lg scale-105' : ''
            }`}
          >
            {plan.popular && (
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground px-4 py-1 rounded-full text-sm font-semibold">
                Most Popular
              </div>
            )}
            
            <CardHeader>
              <CardTitle className="text-2xl">{plan.name}</CardTitle>
              <CardDescription>{plan.description}</CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-6">
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-bold">
                    {billingCycle === 'monthly' ? plan.price : plan.priceAnnual}
                  </span>
                  {plan.id !== 'free' && (
                    <span className="text-muted-foreground">
                      /{billingCycle === 'monthly' ? 'month' : 'year'}
                    </span>
                  )}
                </div>
                {billingCycle === 'annual' && plan.id !== 'free' && (
                  <p className="text-sm text-muted-foreground mt-1">
                    Billed annually
                  </p>
                )}
              </div>

              <ul className="space-y-3">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
            
            <CardFooter>
              <Button
                className="w-full"
                variant={plan.popular ? 'default' : 'outline'}
                onClick={() => handleSelectPlan(plan)}
              >
                {plan.id === 'free' ? 'Get Started' : `Choose ${plan.name}`}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      {user && (
        <div className="text-center mt-12">
          <p className="text-muted-foreground">
            Need help choosing? <a href="mailto:support@trainerhubb.app" className="text-primary hover:underline">Contact us</a>
          </p>
        </div>
      )}
    </div>
  );
}

