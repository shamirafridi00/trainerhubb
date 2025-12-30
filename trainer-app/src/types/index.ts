// User and Authentication Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  is_trainer: boolean;
  is_client: boolean;
  is_verified: boolean;
}

export interface Trainer {
  id: number;
  user: User;
  business_name: string;
  bio?: string;
  expertise?: string;
  location?: string;
  timezone?: string;
  rating?: number;
  total_sessions: number;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  token: string;
  user: User;
  trainer?: Trainer;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm?: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  business_name?: string;
  username?: string;
}

// Client Types
export interface Client {
  id: number;
  trainer: number;
  user?: User;
  first_name: string;
  last_name: string;
  email: string;
  phone_number?: string;
  date_of_birth?: string;
  emergency_contact?: string;
  notes?: string;
  is_active: boolean;
  total_paid?: string;
  last_payment_date?: string;
  payment_status?: 'unpaid' | 'partial' | 'paid';
  created_at: string;
  updated_at: string;
  // Computed fields
  full_name?: string;
}

// Booking Types
export interface Booking {
  id: number;
  trainer: number;
  client: number;
  client_name?: string;
  start_time: string;
  end_time: string;
  status: 'scheduled' | 'completed' | 'cancelled' | 'no_show';
  notes?: string;
  created_at: string;
  updated_at: string;
}

// Package Types
export interface SessionPackage {
  id: number;
  trainer: number;
  name: string;
  description?: string;
  session_count: number;
  price: string;
  validity_days?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientPackage {
  id: number;
  client: number;
  package: SessionPackage;
  sessions_remaining: number;
  purchased_date: string;
  expiry_date?: string;
  status: 'active' | 'expired' | 'completed';
}

// Subscription Types
export interface Subscription {
  id: number;
  trainer: number;
  plan: 'free' | 'pro' | 'business';
  status: 'active' | 'past_due' | 'cancelled' | 'paused';
  paddleSubscriptionId?: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

// Feature Limits
export interface FeatureLimits {
  max_clients: number;
  max_pages: number;
  max_workflows?: number;
  custom_domain: boolean;
  white_label: boolean;
  workflows: boolean;
  [key: string]: any;
}

// API Response Types
export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Page Builder Types
export interface PageTemplate {
  id: number;
  name: string;
  slug: string;
  description: string;
  thumbnail?: string;
  category: string;
  is_premium: boolean;
  template_data: Record<string, any>;
  available_for_plans: string[];
  created_at: string;
}

export interface PageSection {
  id: number;
  section_type: 'hero' | 'services' | 'about' | 'testimonials' | 'contact' | 'pricing' | 'gallery' | 'faq' | 'booking';
  order: number;
  content: Record<string, any>;
  is_visible: boolean;
  created_at?: string;
}

export interface Page {
  id: number;
  trainer: number;
  title: string;
  slug: string;
  template?: number;
  template_name?: string;
  content: Record<string, any>;
  is_published: boolean;
  published_at?: string;
  seo_title?: string;
  seo_description?: string;
  seo_keywords?: string;
  custom_domain?: number;
  public_url?: string;
  sections?: PageSection[];
  created_at: string;
  updated_at: string;
}

// Payment Tracking Types
export interface ClientPayment {
  id: number;
  client: number;
  client_name?: string;
  amount: string;
  currency: string;
  payment_method: 'stripe' | 'paypal' | 'bank_transfer' | 'cash' | 'venmo' | 'zelle' | 'other';
  payment_date: string;
  reference_id?: string;
  notes?: string;
  recorded_by?: number;
  recorded_by_name?: string;
  package?: number;
  booking?: number;
  created_at: string;
  updated_at: string;
}

