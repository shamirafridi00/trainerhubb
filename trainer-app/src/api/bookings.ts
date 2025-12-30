import { apiClient } from './client';
import type { Booking, PaginatedResponse } from '@/types';

export const bookingsApi = {
  list: async (params?: {
    page?: number;
    status?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<Booking>> => {
    return apiClient.get<PaginatedResponse<Booking>>('/bookings/', { params });
  },

  get: async (id: number): Promise<Booking> => {
    return apiClient.get<Booking>(`/bookings/${id}/`);
  },

  create: async (data: Partial<Booking>): Promise<Booking> => {
    return apiClient.post<Booking>('/bookings/', data);
  },

  update: async (id: number, data: Partial<Booking>): Promise<Booking> => {
    return apiClient.patch<Booking>(`/bookings/${id}/`, data);
  },

  delete: async (id: number): Promise<void> => {
    return apiClient.delete<void>(`/bookings/${id}/`);
  },

  updateStatus: async (id: number, status: string): Promise<Booking> => {
    return apiClient.post<Booking>(`/bookings/${id}/update-status/`, { status });
  },
};

