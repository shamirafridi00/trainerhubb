import { apiClient } from './client';
import type { SessionPackage, ClientPackage, PaginatedResponse } from '@/types';

export const packagesApi = {
  // Session Packages
  listPackages: async (params?: {
    page?: number;
    is_active?: boolean;
  }): Promise<PaginatedResponse<SessionPackage>> => {
    return apiClient.get<PaginatedResponse<SessionPackage>>('/packages/', { params });
  },

  getPackage: async (id: number): Promise<SessionPackage> => {
    return apiClient.get<SessionPackage>(`/packages/${id}/`);
  },

  createPackage: async (data: Partial<SessionPackage>): Promise<SessionPackage> => {
    return apiClient.post<SessionPackage>('/packages/', data);
  },

  updatePackage: async (id: number, data: Partial<SessionPackage>): Promise<SessionPackage> => {
    return apiClient.patch<SessionPackage>(`/packages/${id}/`, data);
  },

  deletePackage: async (id: number): Promise<void> => {
    return apiClient.delete<void>(`/packages/${id}/`);
  },

  // Client Packages
  listClientPackages: async (params?: {
    page?: number;
    client_id?: number;
    status?: string;
  }): Promise<PaginatedResponse<ClientPackage>> => {
    return apiClient.get<PaginatedResponse<ClientPackage>>('/packages/client-packages/', { params });
  },

  getClientPackage: async (id: number): Promise<ClientPackage> => {
    return apiClient.get<ClientPackage>(`/packages/client-packages/${id}/`);
  },

  assignPackage: async (data: {
    client: number;
    package: number;
  }): Promise<ClientPackage> => {
    return apiClient.post<ClientPackage>('/packages/client-packages/', data);
  },
};

