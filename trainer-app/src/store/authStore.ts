import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Trainer, LoginCredentials, RegisterData } from '@/types';
import { authApi } from '@/api';

interface AuthState {
  user: User | null;
  trainer: Trainer | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      trainer: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(credentials);
          set({
            user: response.user,
            trainer: response.trainer || null,
            token: response.token,
            isAuthenticated: true,
            isLoading: false,
          });

          // Redirect to app subdomain after successful login
          const currentHost = window.location.host;
          if (!currentHost.startsWith('app.')) {
            // Handle both production and development environments
            const baseDomain = currentHost.replace('www.', '');
            if (baseDomain.includes('.app') || baseDomain.includes('.local')) {
              // Production or local domain
              window.location.href = `http://app.${baseDomain}/dashboard`;
            } else {
              // Localhost development - use port 3000 for React app
              window.location.href = `http://localhost:3000/dashboard`;
            }
          }
        } catch (error: any) {
          // Handle validation errors from backend
          let errorMessage = 'Login failed';
          if (error.response?.data) {
            const errorData = error.response.data;
            if (errorData.detail) {
              errorMessage = errorData.detail;
            } else if (typeof errorData === 'object') {
              const fieldErrors = Object.entries(errorData)
                .map(([field, errors]: [string, any]) => {
                  const errorList = Array.isArray(errors) ? errors : [errors];
                  return `${field}: ${errorList.join(', ')}`;
                })
                .join('; ');
              errorMessage = fieldErrors || errorMessage;
            } else if (typeof errorData === 'string') {
              errorMessage = errorData;
            }
          }
          set({
            error: errorMessage,
            isLoading: false,
          });
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.register(data);
          set({
            user: response.user,
            trainer: response.trainer || null,
            token: response.token,
            isAuthenticated: true,
            isLoading: false,
          });

          // Redirect to app subdomain after successful registration
          const currentHost = window.location.host;
          if (!currentHost.startsWith('app.')) {
            // Handle both production and development environments
            const baseDomain = currentHost.replace('www.', '');
            if (baseDomain.includes('.app') || baseDomain.includes('.local')) {
              // Production or local domain
              window.location.href = `http://app.${baseDomain}/dashboard`;
            } else {
              // Localhost development - use port 3000 for React app
              window.location.href = `http://localhost:3000/dashboard`;
            }
          }
        } catch (error: any) {
          // Handle validation errors from backend
          let errorMessage = 'Registration failed';
          if (error.response?.data) {
            const errorData = error.response.data;
            if (errorData.detail) {
              errorMessage = errorData.detail;
            } else if (typeof errorData === 'object') {
              // Format field errors
              const fieldErrors = Object.entries(errorData)
                .map(([field, errors]: [string, any]) => {
                  const errorList = Array.isArray(errors) ? errors : [errors];
                  return `${field}: ${errorList.join(', ')}`;
                })
                .join('; ');
              errorMessage = fieldErrors || errorMessage;
            }
          }
          set({
            error: errorMessage,
            isLoading: false,
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await authApi.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          set({
            user: null,
            trainer: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      loadUser: async () => {
        const token = get().token;
        if (!token) {
          set({ isAuthenticated: false });
          return;
        }

        set({ isLoading: true });
        try {
          const response = await authApi.getCurrentUser();
          set({
            user: response.user,
            trainer: response.trainer || null,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            user: null,
            trainer: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        trainer: state.trainer,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

