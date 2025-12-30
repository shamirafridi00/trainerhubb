import { useEffect, useState } from 'react';
import { DollarSign, TrendingUp, Users } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/api/client';

interface RevenueSummary {
  this_month: {
    total: number;
    count: number;
    by_method: Record<string, number>;
  };
  last_month: {
    total: number;
    count: number;
  };
  all_time: {
    total: number;
    count: number;
  };
  unpaid_clients: {
    count: number;
    total_amount: number;
  };
}

export function RevenueWidget() {
  const [summary, setSummary] = useState<RevenueSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.get<RevenueSummary>('/payments/client-payments/revenue-summary/');
      setSummary(data);
    } catch (err) {
      console.error('Failed to load revenue summary:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">Loading revenue data...</p>
        </CardContent>
      </Card>
    );
  }

  if (!summary) {
    return null;
  }

  const thisMonthChange = summary.last_month.total > 0
    ? ((summary.this_month.total - summary.last_month.total) / summary.last_month.total) * 100
    : 0;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">This Month</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(summary.this_month.total)}</div>
          <p className="text-xs text-muted-foreground">
            {summary.this_month.count} payment{summary.this_month.count !== 1 ? 's' : ''}
          </p>
          {thisMonthChange !== 0 && (
            <p className={`text-xs mt-1 ${thisMonthChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {thisMonthChange >= 0 ? '+' : ''}{thisMonthChange.toFixed(1)}% from last month
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">All Time</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(summary.all_time.total)}</div>
          <p className="text-xs text-muted-foreground">
            {summary.all_time.count} total payment{summary.all_time.count !== 1 ? 's' : ''}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Unpaid Clients</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{summary.unpaid_clients.count}</div>
          <p className="text-xs text-muted-foreground">
            {formatCurrency(summary.unpaid_clients.total_amount)} outstanding
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Last Month</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(summary.last_month.total)}</div>
          <p className="text-xs text-muted-foreground">
            {summary.last_month.count} payment{summary.last_month.count !== 1 ? 's' : ''}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

