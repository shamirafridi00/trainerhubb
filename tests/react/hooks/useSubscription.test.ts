import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useSubscription } from '../useSubscription';
import { useSubscriptionStore } from '@/store/subscriptionStore';
import { apiClient } from '@/api/client';

// Mock the API client
vi.mock('@/api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

// Mock the subscription store
vi.mock('@/store/subscriptionStore', () => ({
  useSubscriptionStore: vi.fn(),
}));

describe('useSubscription', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return subscription data from store', () => {
    const mockSubscription = {
      plan_name: 'pro',
      status: 'active',
    };
    const mockLimits = {
      maxClients: 50,
      maxPages: 5,
      maxWorkflows: 3,
    };

    vi.mocked(useSubscriptionStore).mockReturnValue({
      subscription: mockSubscription,
      limits: mockLimits,
      isLoading: false,
      error: null,
      fetchSubscription: vi.fn(),
      setSubscription: vi.fn(),
      setLimits: vi.fn(),
    } as any);

    const { result } = renderHook(() => useSubscription());

    expect(result.current.subscription).toEqual(mockSubscription);
    expect(result.current.limits).toEqual(mockLimits);
    expect(result.current.isLoading).toBe(false);
  });

  it('should indicate free plan when no subscription', () => {
    vi.mocked(useSubscriptionStore).mockReturnValue({
      subscription: null,
      limits: null,
      isLoading: false,
      error: null,
      fetchSubscription: vi.fn(),
      setSubscription: vi.fn(),
      setLimits: vi.fn(),
    } as any);

    const { result } = renderHook(() => useSubscription());

    expect(result.current.subscription).toBeNull();
    expect(result.current.isFreePlan).toBe(true);
  });

  it('should identify pro plan', () => {
    vi.mocked(useSubscriptionStore).mockReturnValue({
      subscription: { plan_name: 'pro', status: 'active' },
      limits: {},
      isLoading: false,
      error: null,
      fetchSubscription: vi.fn(),
      setSubscription: vi.fn(),
      setLimits: vi.fn(),
    } as any);

    const { result } = renderHook(() => useSubscription());

    expect(result.current.isProPlan).toBe(true);
    expect(result.current.isBusinessPlan).toBe(false);
  });

  it('should identify business plan', () => {
    vi.mocked(useSubscriptionStore).mockReturnValue({
      subscription: { plan_name: 'business', status: 'active' },
      limits: {},
      isLoading: false,
      error: null,
      fetchSubscription: vi.fn(),
      setSubscription: vi.fn(),
      setLimits: vi.fn(),
    } as any);

    const { result } = renderHook(() => useSubscription());

    expect(result.current.isBusinessPlan).toBe(true);
    expect(result.current.isProPlan).toBe(false);
  });

  it('should check feature availability', () => {
    vi.mocked(useSubscriptionStore).mockReturnValue({
      subscription: { plan_name: 'pro', status: 'active' },
      limits: { maxClients: 50 },
      isLoading: false,
      error: null,
      fetchSubscription: vi.fn(),
      setSubscription: vi.fn(),
      setLimits: vi.fn(),
    } as any);

    const { result } = renderHook(() => useSubscription());

    expect(result.current.hasFeature('custom_domain')).toBe(false);
    expect(result.current.hasFeature('white_label')).toBe(true);
  });
});

