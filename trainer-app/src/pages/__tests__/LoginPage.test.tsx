import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../LoginPage';
import { useAuthStore } from '@/store/authStore';

// Mock the auth store
vi.mock('@/store/authStore', () => ({
  useAuthStore: vi.fn(),
}));

// Mock react-router-dom's useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('LoginPage', () => {
  const mockLogin = vi.fn();
  const mockClearError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuthStore).mockReturnValue({
      login: mockLogin,
      clearError: mockClearError,
      isLoading: false,
      error: null,
      validationErrors: null,
      user: null,
      token: null,
      isAuthenticated: false,
      register: vi.fn(),
      logout: vi.fn(),
      loadUser: vi.fn(),
    } as any);
  });

  it('renders login form', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/sign in/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('handles form submission', async () => {
    mockLogin.mockResolvedValue({});
    
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('displays error message on login failure', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      login: mockLogin,
      clearError: mockClearError,
      isLoading: false,
      error: 'Invalid credentials',
      validationErrors: null,
      user: null,
      token: null,
      isAuthenticated: false,
      register: vi.fn(),
      logout: vi.fn(),
      loadUser: vi.fn(),
    } as any);

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
  });

  it('disables submit button while loading', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      login: mockLogin,
      clearError: mockClearError,
      isLoading: true,
      error: null,
      validationErrors: null,
      user: null,
      token: null,
      isAuthenticated: false,
      register: vi.fn(),
      logout: vi.fn(),
      loadUser: vi.fn(),
    } as any);

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    const submitButton = screen.getByRole('button', { name: /signing in/i });
    expect(submitButton).toBeDisabled();
  });
});

