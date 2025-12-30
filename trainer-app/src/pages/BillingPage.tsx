import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useSubscription } from '@/hooks/useSubscription';
import { CreditCard, ExternalLink, AlertCircle } from 'lucide-react';
import { apiClient } from '@/api/client';

interface Payment {
  id: number;
  amount: string;
  currency: string;
  status: string;
  paddle_transaction_id: string;
  receipt_url?: string;
  created_at: string;
}

export default function BillingPage() {
  const { subscription, features, isLoading, error } = useSubscription();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loadingPayments, setLoadingPayments] = useState(true);

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      setLoadingPayments(true);
      const response = await apiClient.get<{ results?: Payment[]; } | Payment[]>('/payments/');
      const data = response as any;
      setPayments(data.results || data);
    } catch (err) {
      console.error('Failed to load payments:', err);
    } finally {
      setLoadingPayments(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will retain access until the end of your billing period.')) {
      return;
    }

    try {
      await apiClient.post(`/payments/subscriptions/${subscription?.id}/cancel/`);
      alert('Subscription cancelled successfully');
      window.location.reload();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel subscription');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p>Loading billing information...</p>
      </div>
    );
  }

  const planNames: Record<string, string> = {
    free: 'Free',
    pro: 'Pro',
    business: 'Business',
  };

  const currentPlan = features?.plan || 'free';

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">Billing & Subscription</h1>

      {error && (
        <Card className="mb-6 border-red-500">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <CardTitle>Error</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Current Plan */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Current Plan</CardTitle>
          <CardDescription>Manage your subscription</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
            <div>
              <h3 className="font-semibold text-lg">{planNames[currentPlan]}</h3>
              {subscription?.status && (
                <p className="text-sm text-muted-foreground capitalize">
                  Status: {subscription.status}
                </p>
              )}
            </div>
            {currentPlan !== 'free' && subscription?.current_period_end && (
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Renews on</p>
                <p className="font-semibold">{formatDate(subscription.current_period_end)}</p>
              </div>
            )}
          </div>

          {subscription?.cancel_at_period_end && (
            <div className="p-4 bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-500 rounded-lg">
              <p className="text-sm text-yellow-700 dark:text-yellow-400">
                Your subscription is set to cancel on {formatDate(subscription.current_period_end)}.
                You will retain access until then.
              </p>
            </div>
          )}

          {/* Feature Limits */}
          {features && (
            <div className="space-y-2">
              <h4 className="font-semibold">Your Plan Includes:</h4>
              <ul className="space-y-1 text-sm">
                <li>• Clients: {features.limits.max_clients === -1 ? 'Unlimited' : features.limits.max_clients}</li>
                <li>• Pages: {features.limits.max_pages === -1 ? 'Unlimited' : features.limits.max_pages}</li>
                <li>• Custom Domain: {features.limits.custom_domain ? 'Yes' : 'No'}</li>
                <li>• White Label: {features.limits.white_label ? 'Yes' : 'No'}</li>
                <li>• Workflows: {features.limits.workflows ? 'Yes' : 'No'}</li>
              </ul>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex gap-2">
          {currentPlan !== 'business' && (
            <Link to="/pricing" className="flex-1">
              <Button className="w-full">
                Upgrade Plan
              </Button>
            </Link>
          )}
          {currentPlan !== 'free' && !subscription?.cancel_at_period_end && (
            <Button
              variant="outline"
              onClick={handleCancelSubscription}
              className="flex-1"
            >
              Cancel Subscription
            </Button>
          )}
        </CardFooter>
      </Card>

      {/* Payment History */}
      <Card>
        <CardHeader>
          <CardTitle>Payment History</CardTitle>
          <CardDescription>View your past payments and invoices</CardDescription>
        </CardHeader>
        <CardContent>
          {loadingPayments ? (
            <p className="text-muted-foreground">Loading payments...</p>
          ) : payments.length === 0 ? (
            <p className="text-muted-foreground">No payments yet</p>
          ) : (
            <div className="space-y-3">
              {payments.map((payment) => (
                <div
                  key={payment.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <CreditCard className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="font-semibold">
                        {payment.currency} {payment.amount}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(payment.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`text-sm px-2 py-1 rounded ${
                        payment.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {payment.status}
                    </span>
                    {payment.receipt_url && (
                      <a
                        href={payment.receipt_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline flex items-center gap-1"
                      >
                        Invoice
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Paddle Customer Portal */}
      {currentPlan !== 'free' && subscription?.paddleSubscriptionId && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Manage Payment Methods</CardTitle>
            <CardDescription>
              Update your payment method or billing address
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Click below to access Paddle's secure billing portal to manage your payment methods.
            </p>
          </CardContent>
          <CardFooter>
            <Button variant="outline" className="w-full">
              <ExternalLink className="mr-2 h-4 w-4" />
              Open Billing Portal
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  );
}

