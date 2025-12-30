import { Badge } from '@/components/ui/badge';
import type { Client } from '@/types';

interface PaymentStatusBadgeProps {
  status: Client['payment_status'];
}

export function PaymentStatusBadge({ status }: PaymentStatusBadgeProps) {
  const variants: Record<NonNullable<Client['payment_status']>, 'default' | 'secondary' | 'destructive'> = {
    paid: 'default',
    partial: 'secondary',
    unpaid: 'destructive',
  };

  const labels: Record<NonNullable<Client['payment_status']>, string> = {
    paid: 'Paid',
    partial: 'Partial',
    unpaid: 'Unpaid',
  };

  if (!status) return null;

  return (
    <Badge variant={variants[status]}>
      {labels[status]}
    </Badge>
  );
}

