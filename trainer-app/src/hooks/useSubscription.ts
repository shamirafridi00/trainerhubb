import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';
import type { Subscription, FeatureLimits } from '@/types';

interface SubscriptionFeatures {
  plan: string;
  status: string;
  is_active: boolean;
  limits: FeatureLimits;
}

export function useSubscription() {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [features, setFeatures] = useState<SubscriptionFeatures | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      setIsLoading(true);
      
      // Fetch current subscription
      const subResponse = await apiClient.get<Subscription>('/payments/subscriptions/current/');
      setSubscription(subResponse);
      
      // Fetch feature limits
      const featuresResponse = await apiClient.get<SubscriptionFeatures>('/payments/subscriptions/features/');
      setFeatures(featuresResponse);
      
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load subscription');
      console.error('Subscription fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const canUse = (feature: keyof FeatureLimits): boolean => {
    if (!features) return false;
    return !!features.limits[feature];
  };

  const hasReachedLimit = (resource: 'clients' | 'pages' | 'workflows', currentCount: number): boolean => {
    if (!features) return false;
    
    const limitKey = `max_${resource}` as keyof FeatureLimits;
    const limit = features.limits[limitKey] as number;
    
    // -1 means unlimited
    if (limit === -1) return false;
    
    return currentCount >= limit;
  };

  const getLimit = (resource: 'clients' | 'pages' | 'workflows'): number => {
    if (!features) return 0;
    
    const limitKey = `max_${resource}` as keyof FeatureLimits;
    return features.limits[limitKey] as number;
  };

  const getPlan = (): string => {
    return features?.plan || 'free';
  };

  const isActive = (): boolean => {
    return features?.is_active || false;
  };

  return {
    subscription,
    features,
    isLoading,
    error,
    canUse,
    hasReachedLimit,
    getLimit,
    getPlan,
    isActive,
    refresh: fetchSubscription,
  };
}

