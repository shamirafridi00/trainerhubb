import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users, Calendar, Package, TrendingUp, Plus, ArrowRight, DollarSign } from 'lucide-react';
import { RevenueWidget } from '@/components/RevenueWidget';
import { apiClient } from '@/api/client';
import type { Client, Booking, SessionPackage, ClientPayment } from '@/types';

interface DashboardStats {
  totalClients: number;
  activeClients: number;
  upcomingBookings: number;
  activePackages: number;
  revenueThisMonth: number;
}

function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalClients: 0,
    activeClients: 0,
    upcomingBookings: 0,
    activePackages: 0,
    revenueThisMonth: 0,
  });
  const [recentClients, setRecentClients] = useState<Client[]>([]);
  const [recentPayments, setRecentPayments] = useState<ClientPayment[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);

      // Fetch clients
      const clientsResponse = await apiClient.get<Client[]>('/clients/');
      const clients = Array.isArray(clientsResponse) ? clientsResponse : (clientsResponse as any).results || [];
      const activeClients = clients.filter((c: Client) => c.is_active);

      // Fetch bookings (upcoming this week)
      let upcomingBookings = 0;
      try {
        const bookingsResponse = await apiClient.get<Booking[]>('/bookings/');
        const bookings = Array.isArray(bookingsResponse) ? bookingsResponse : (bookingsResponse as any).results || [];
        const now = new Date();
        const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
        upcomingBookings = bookings.filter((b: Booking) => {
          const startTime = new Date(b.start_time);
          return startTime >= now && startTime <= nextWeek && b.status === 'scheduled';
        }).length;
      } catch (err) {
        // Bookings might not be implemented yet
        console.log('Bookings endpoint not available');
      }

      // Fetch packages
      let activePackages = 0;
      try {
        const packagesResponse = await apiClient.get<SessionPackage[]>('/packages/');
        const packages = Array.isArray(packagesResponse) ? packagesResponse : (packagesResponse as any).results || [];
        activePackages = packages.filter((p: SessionPackage) => p.is_active).length;
      } catch (err) {
        console.log('Packages endpoint not available');
      }

      // Fetch revenue summary
      let revenueThisMonth = 0;
      try {
        const revenueResponse = await apiClient.get<{
          this_month: { total: number };
        }>('/client-payments/revenue-summary/');
        revenueThisMonth = revenueResponse.this_month?.total || 0;
      } catch (err) {
        console.log('Revenue endpoint not available');
      }

      // Fetch recent payments
      try {
        const paymentsResponse = await apiClient.get<ClientPayment[]>('/client-payments/recent/?limit=5');
        setRecentPayments(Array.isArray(paymentsResponse) ? paymentsResponse : []);
      } catch (err) {
        console.log('Recent payments not available');
      }

      setStats({
        totalClients: clients.length,
        activeClients: activeClients.length,
        upcomingBookings,
        activePackages,
        revenueThisMonth,
      });

      // Get recent clients (last 5)
      setRecentClients(clients.slice(0, 5));
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const statsCards = [
    {
      title: 'Total Clients',
      value: stats.totalClients.toString(),
      description: `${stats.activeClients} active`,
      icon: Users,
      link: '/clients',
    },
    {
      title: 'Upcoming Bookings',
      value: stats.upcomingBookings.toString(),
      description: 'This week',
      icon: Calendar,
      link: '/bookings',
    },
    {
      title: 'Active Packages',
      value: stats.activePackages.toString(),
      description: 'Available for purchase',
      icon: Package,
      link: '/packages',
    },
    {
      title: 'Revenue',
      value: formatCurrency(stats.revenueThisMonth),
      description: 'This month',
      icon: TrendingUp,
      link: '/reports',
    },
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to your TrainerHub dashboard
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/clients">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Client
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Link key={stat.title} to={stat.link}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {stat.title}
                  </CardTitle>
                  <Icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {isLoading ? '...' : stat.value}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {stat.description}
                  </p>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      {/* Revenue Widget */}
      <div>
        <RevenueWidget />
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Recent Clients */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Clients</CardTitle>
                <CardDescription>
                  Your latest client additions
                </CardDescription>
              </div>
              <Link to="/clients">
                <Button variant="ghost" size="sm">
                  View all <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                <div className="h-16 bg-gray-100 rounded animate-pulse"></div>
                <div className="h-16 bg-gray-100 rounded animate-pulse"></div>
              </div>
            ) : recentClients.length === 0 ? (
              <div className="text-center py-8">
                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground mb-4">
                  No clients yet
                </p>
                <Link to="/clients">
                  <Button size="sm">
                    <Plus className="mr-2 h-4 w-4" />
                    Add Your First Client
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {recentClients.map((client) => (
                  <div
                    key={client.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div>
                      <p className="font-medium">
                        {client.full_name || `${client.first_name} ${client.last_name}`}
                      </p>
                      <p className="text-sm text-muted-foreground">{client.email}</p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(client.created_at)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Payments */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Payments</CardTitle>
                <CardDescription>
                  Latest payment records
                </CardDescription>
              </div>
              <Link to="/reports">
                <Button variant="ghost" size="sm">
                  View all <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                <div className="h-16 bg-gray-100 rounded animate-pulse"></div>
                <div className="h-16 bg-gray-100 rounded animate-pulse"></div>
              </div>
            ) : recentPayments.length === 0 ? (
              <div className="text-center py-8">
                <DollarSign className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground mb-4">
                  No payments recorded yet
                </p>
                <p className="text-xs text-muted-foreground">
                  Payments will appear here once you mark clients as paid
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentPayments.map((payment) => (
                  <div
                    key={payment.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div>
                      <p className="font-medium">
                        {payment.client_name || `Client #${payment.client}`}
                      </p>
                      <p className="text-sm text-muted-foreground capitalize">
                        {payment.payment_method.replace('_', ' ')}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">
                        {formatCurrency(parseFloat(payment.amount))}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(payment.payment_date)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and shortcuts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link to="/clients">
              <Button variant="outline" className="w-full justify-start">
                <Users className="mr-2 h-4 w-4" />
                Add Client
              </Button>
            </Link>
            <Link to="/bookings">
              <Button variant="outline" className="w-full justify-start">
                <Calendar className="mr-2 h-4 w-4" />
                Create Booking
              </Button>
            </Link>
            <Link to="/packages">
              <Button variant="outline" className="w-full justify-start">
                <Package className="mr-2 h-4 w-4" />
                New Package
              </Button>
            </Link>
            <Link to="/pages/new">
              <Button variant="outline" className="w-full justify-start">
                <Plus className="mr-2 h-4 w-4" />
                Create Page
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default DashboardPage;