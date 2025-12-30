import { useState, useEffect } from 'react';
import { Trash, DollarSign } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/api/client';
import type { ClientPayment } from '@/types';

interface PaymentHistoryProps {
  clientId: number;
  onRefresh?: () => void;
}

const PAYMENT_METHOD_LABELS: Record<ClientPayment['payment_method'], string> = {
  stripe: 'Stripe',
  paypal: 'PayPal',
  bank_transfer: 'Bank Transfer',
  cash: 'Cash',
  venmo: 'Venmo',
  zelle: 'Zelle',
  other: 'Other',
};

export function PaymentHistory({ clientId, onRefresh }: PaymentHistoryProps) {
  const [payments, setPayments] = useState<ClientPayment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [totalPaid, setTotalPaid] = useState(0);

  useEffect(() => {
    fetchPayments();
  }, [clientId]);

  const fetchPayments = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.get<ClientPayment[]>(`/clients/${clientId}/payments/`);
      setPayments(data as any);
      
      // Calculate total
      const total = data.reduce((sum, payment) => sum + parseFloat(payment.amount), 0);
      setTotalPaid(total);
    } catch (err) {
      console.error('Failed to load payments:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (paymentId: number) => {
    if (!confirm('Are you sure you want to delete this payment record?')) {
      return;
    }

    try {
      await apiClient.delete(`/payments/client-payments/${paymentId}/`);
      await fetchPayments();
      onRefresh?.();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete payment');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: string, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(parseFloat(amount));
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">Loading payment history...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Payment History</CardTitle>
            <div className="flex items-center gap-2 text-lg font-semibold">
              <DollarSign className="h-5 w-5" />
              <span>Total Paid: {formatCurrency(totalPaid.toString(), payments[0]?.currency || 'USD')}</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {payments.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No payments recorded yet.
            </p>
          ) : (
            <div className="space-y-2">
              {payments.map((payment) => (
                <div
                  key={payment.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-4">
                      <div>
                        <p className="font-medium">
                          {formatCurrency(payment.amount, payment.currency)}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {PAYMENT_METHOD_LABELS[payment.payment_method]}
                        </p>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        <p>{formatDate(payment.payment_date)}</p>
                        {payment.reference_id && (
                          <p className="text-xs">Ref: {payment.reference_id}</p>
                        )}
                      </div>
                      {payment.notes && (
                        <div className="flex-1 text-sm text-muted-foreground">
                          <p className="truncate">{payment.notes}</p>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(payment.id)}
                    >
                      <Trash className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

