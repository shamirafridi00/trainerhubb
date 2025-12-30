import { useState, useEffect } from 'react';
import { Plus, Search, Filter, MoreVertical, Edit, Trash, DollarSign } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useSubscription } from '@/hooks/useSubscription';
import { LimitReachedPrompt } from '@/components/LimitReachedPrompt';
import { ClientDialog } from '@/components/ClientDialog';
import { PaymentStatusBadge } from '@/components/PaymentStatusBadge';
import { MarkAsPaidDialog } from '@/components/MarkAsPaidDialog';
import { apiClient } from '@/api/client';
import type { Client } from '@/types';

export default function ClientsManagementPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | undefined>();
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [selectedClientForPayment, setSelectedClientForPayment] = useState<number | null>(null);
  const { hasReachedLimit, getLimit } = useSubscription();

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get<{ results?: Client[]; } | Client[]>('/clients/');
      const data = response as any;
      const clientsList = (data.results || data) as Client[];
      // Add full_name if not present
      const clientsWithFullName = clientsList.map(client => ({
        ...client,
        full_name: client.full_name || `${client.first_name} ${client.last_name}`,
      }));
      setClients(clientsWithFullName);
    } catch (err) {
      console.error('Failed to load clients:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredClients = clients.filter((client) => {
    const fullName = client.full_name || `${client.first_name} ${client.last_name}`;
    return fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      client.email.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const handleAddClient = () => {
    setSelectedClient(undefined);
    setDialogOpen(true);
  };

  const handleEditClient = (client: Client) => {
    setSelectedClient(client);
    setDialogOpen(true);
  };

  const handleDeleteClient = async (clientId: number) => {
    if (!confirm('Are you sure you want to delete this client?')) {
      return;
    }

    try {
      await apiClient.delete(`/clients/${clientId}/`);
      await fetchClients();
    } catch (err) {
      alert('Failed to delete client');
      console.error(err);
    }
  };

  const activeClients = clients.filter(c => c.is_active);
  const limit = getLimit('clients');
  const isLimitReached = hasReachedLimit('clients', activeClients.length);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Clients</h1>
          <p className="text-muted-foreground mt-1">
            {activeClients.length} active client{activeClients.length !== 1 ? 's' : ''}
            {limit !== -1 && ` / ${limit} limit`}
          </p>
        </div>
        <Button onClick={handleAddClient} disabled={isLimitReached}>
          <Plus className="mr-2 h-4 w-4" />
          Add Client
        </Button>
      </div>

      {isLimitReached && (
        <div className="mb-6">
          <LimitReachedPrompt
            resource="clients"
            currentCount={activeClients.length}
            limit={limit}
          />
        </div>
      )}

      {/* Search and Filter */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search clients by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" />
              Filter
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Client List */}
      {isLoading ? (
        <Card>
          <CardContent className="py-12">
            <p className="text-center text-muted-foreground">Loading clients...</p>
          </CardContent>
        </Card>
      ) : filteredClients.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <p className="text-center text-muted-foreground">
              {searchTerm ? 'No clients found matching your search' : 'No clients yet'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredClients.map((client) => (
            <Card key={client.id}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div>
                  <CardTitle className="text-xl">
                    {client.full_name || `${client.first_name} ${client.last_name}`}
                  </CardTitle>
                  <CardDescription>{client.email}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  {client.payment_status && (
                    <PaymentStatusBadge status={client.payment_status} />
                  )}
                  {!client.is_active && (
                    <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                      Inactive
                    </span>
                  )}
                  <Button variant="ghost" size="icon">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Phone</p>
                    <p className="font-medium">{client.phone_number || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Member Since</p>
                    <p className="font-medium">
                      {new Date(client.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  {client.total_paid !== undefined && (
                    <div>
                      <p className="text-muted-foreground">Total Paid</p>
                      <p className="font-medium flex items-center gap-1">
                        <DollarSign className="h-3 w-3" />
                        {parseFloat(client.total_paid).toFixed(2)}
                      </p>
                    </div>
                  )}
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedClientForPayment(client.id);
                        setPaymentDialogOpen(true);
                      }}
                    >
                      <DollarSign className="mr-2 h-3 w-3" />
                      Mark Paid
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleEditClient(client)}>
                      <Edit className="mr-2 h-3 w-3" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleDeleteClient(client.id)}>
                      <Trash className="mr-2 h-3 w-3" />
                      Delete
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Client Dialog */}
      <ClientDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSuccess={fetchClients}
        client={selectedClient}
      />

      {/* Payment Dialog */}
      {selectedClientForPayment && (
        <MarkAsPaidDialog
          open={paymentDialogOpen}
          onOpenChange={setPaymentDialogOpen}
          clientId={selectedClientForPayment}
          onSuccess={() => {
            fetchClients();
            setSelectedClientForPayment(null);
          }}
        />
      )}
    </div>
  );
}

