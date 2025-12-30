import { create } from 'zustand';
import type { Subscription, FeatureLimits } from '@/types';

interface SubscriptionState {
  subscription: Subscription | null;
  limits: FeatureLimits;
  isLoading: boolean;

  // Actions
  setSubscription: (subscription: Subscription) => void;
  canUse: (feature: keyof FeatureLimits) => boolean;
  hasReachedLimit: (feature: 'clients' | 'pages' | 'workflows', current: number) => boolean;
}

const DEFAULT_LIMITS: Record<string, FeatureLimits> = {
  free: {
    max_clients: 10,
    max_pages: 1,
    max_workflows: 0,
    custom_domain: false,
    white_label: false,
    workflows: false,
  },
  pro: {
    max_clients: -1, // unlimited
    max_pages: 5,
    max_workflows: 3,
    custom_domain: false,
    white_label: false,
    workflows: true,
  },
  business: {
    max_clients: -1, // unlimited
    max_pages: -1, // unlimited
    max_workflows: -1, // unlimited
    custom_domain: true,
    white_label: true,
    workflows: true,
  },
};

export const useSubscriptionStore = create<SubscriptionState>((set, get) => ({
  subscription: null,
  limits: DEFAULT_LIMITS.free,
  isLoading: false,

  setSubscription: (subscription: Subscription) => {
    const limits = DEFAULT_LIMITS[subscription.plan] || DEFAULT_LIMITS.free;
    set({ subscription, limits });
  },

  canUse: (feature: keyof FeatureLimits) => {
    const { limits } = get();
    return !!limits[feature];
  },

  hasReachedLimit: (feature: 'clients' | 'pages' | 'workflows', current: number) => {
    const { limits } = get();
    const limitKey = `max${feature.charAt(0).toUpperCase() + feature.slice(1)}` as keyof FeatureLimits;
    const limit = limits[limitKey] as number;
    
    // -1 means unlimited
    if (limit === -1) return false;
    
    return current >= limit;
  },
}));

