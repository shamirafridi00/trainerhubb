import { apiClient } from './client';
import type { AuthResponse, LoginCredentials, RegisterData } from '@/types';

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/users/login/', credentials);
    if (response.token) {
      apiClient.setAuthToken(response.token);
    }
    return response;
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/users/register/', data);
    if (response.token) {
      apiClient.setAuthToken(response.token);
    }
    return response;
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/users/logout/');
    } finally {
      apiClient.clearAuthToken();
    }
  },

  getCurrentUser: async (): Promise<AuthResponse> => {
    return apiClient.get<AuthResponse>('/users/me/');
  },

  refreshToken: async (): Promise<AuthResponse> => {
    return apiClient.post<AuthResponse>('/users/refresh-token/');
  },
};

