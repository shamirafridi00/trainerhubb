import { apiClient } from './client';
import type { Client, PaginatedResponse } from '@/types';

export const clientsApi = {
  list: async (params?: {
    page?: number;
    search?: string;
    is_active?: boolean;
  }): Promise<PaginatedResponse<Client>> => {
    return apiClient.get<PaginatedResponse<Client>>('/clients/', { params });
  },

  get: async (id: number): Promise<Client> => {
    return apiClient.get<Client>(`/clients/${id}/`);
  },

  create: async (data: Partial<Client>): Promise<Client> => {
    return apiClient.post<Client>('/clients/', data);
  },

  update: async (id: number, data: Partial<Client>): Promise<Client> => {
    return apiClient.patch<Client>(`/clients/${id}/`, data);
  },

  delete: async (id: number): Promise<void> => {
    return apiClient.delete<void>(`/clients/${id}/`);
  },
};

