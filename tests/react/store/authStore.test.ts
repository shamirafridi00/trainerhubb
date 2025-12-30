import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from '../authStore';
import * as authApi from '@/api/auth';

// Mock the API
vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      validationErrors: null,
    });
    vi.clearAllMocks();
  });

  it('should have initial state', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
  });

  it('should handle successful login', async () => {
    const mockResponse = {
      data: {
        token: 'test-token',
        user: { id: 1, email: 'test@example.com' },
      },
    };
    vi.mocked(authApi.authApi.login).mockResolvedValue(mockResponse);

    const { login } = useAuthStore.getState();
    await login({ email: 'test@example.com', password: 'password' });

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.token).toBe('test-token');
    expect(state.user).toEqual(mockResponse.data.user);
  });

  it('should handle login error', async () => {
    const mockError = {
      response: {
        data: {
          detail: 'Invalid credentials',
        },
      },
    };
    vi.mocked(authApi.authApi.login).mockRejectedValue(mockError);

    const { login } = useAuthStore.getState();
    
    try {
      await login({ email: 'test@example.com', password: 'wrong' });
    } catch (error) {
      // Expected to throw
    }

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.error).toBe('Invalid credentials');
  });

  it('should handle logout', () => {
    // Set authenticated state
    useAuthStore.setState({
      user: { id: 1, email: 'test@example.com' },
      token: 'test-token',
      isAuthenticated: true,
    });

    const { logout } = useAuthStore.getState();
    logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('should clear error', () => {
    useAuthStore.setState({ error: 'Test error' });

    const { clearError } = useAuthStore.getState();
    clearError();

    expect(useAuthStore.getState().error).toBeNull();
  });
});

