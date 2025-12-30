# 🚀 Epic 1.1: React Frontend Setup - Vite + React + TypeScript + shadcn/ui

Complete guide for scaffolding a modern React frontend for the TrainerHub admin dashboard.

**Time: 2-3 hours** | **Code: 500+ lines**

---

## 📋 Overview

Epic 1.1 focuses on setting up the foundation for the React frontend:
- Vite + React + TypeScript project
- shadcn/ui component library
- Zustand state management
- API client configuration
- Base routing and layout

---

## 🎯 Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Django backend running on `http://localhost:8000`
- API endpoints accessible

---

## Step 1.1: Create Vite + React + TypeScript Project

### 1.1.1 Initialize Project

```bash
# Navigate to project root
cd /home/shamir/trainerhubb

# Create frontend directory
mkdir frontend-react
cd frontend-react

# Initialize Vite project with React and TypeScript
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install
```

### 1.1.2 Install Core Dependencies

```bash
# React Router for navigation
npm install react-router-dom

# Zustand for state management
npm install zustand

# Axios for API calls
npm install axios

# Date handling
npm install date-fns

# Form handling
npm install react-hook-form @hookform/resolvers zod

# Icons (Lucide React - compatible with shadcn/ui)
npm install lucide-react

# Tailwind CSS (required for shadcn/ui)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 1.1.3 Install shadcn/ui

```bash
# Initialize shadcn/ui
npx shadcn-ui@latest init

# Follow prompts:
# - Style: Default
# - Base color: Slate
# - CSS variables: Yes
# - Use src directory: Yes (or No, depending on preference)

# Install essential shadcn/ui components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add table
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add select
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add skeleton
```

---

## Step 1.2: Project Structure

### 1.2.1 Create Directory Structure

```
frontend-react/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── layout/          # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   └── common/         # Reusable components
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── Login.tsx
│   │   │   └── Register.tsx
│   │   ├── dashboard/
│   │   │   └── Dashboard.tsx
│   │   └── admin/
│   │       ├── trainers/
│   │       ├── analytics/
│   │       └── domains/
│   ├── store/
│   │   ├── authStore.ts
│   │   ├── userStore.ts
│   │   └── index.ts
│   ├── lib/
│   │   ├── api.ts          # API client
│   │   ├── utils.ts        # Utility functions
│   │   └── constants.ts    # Constants
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   └── useApi.ts
│   ├── types/
│   │   ├── auth.ts
│   │   ├── user.ts
│   │   └── api.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── public/
├── .env
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## Step 1.3: Configuration Files

### 1.3.1 Environment Variables (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=TrainerHub Admin
```

### 1.3.2 Environment Variables Template (.env.example)

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=TrainerHub Admin
```

### 1.3.3 Vite Config (vite.config.ts)

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### 1.3.4 TypeScript Config (tsconfig.json)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 1.3.5 Tailwind Config (tailwind.config.js)

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

---

## Step 1.4: API Client Setup

### 1.4.1 API Client (src/lib/api.ts)

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Token ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.client.post('/users/login/', { email, password })
    return response.data
  }

  async register(data: {
    email: string
    username: string
    first_name: string
    last_name: string
    password: string
    password_confirm: string
  }) {
    const response = await this.client.post('/users/register/', data)
    return response.data
  }

  async logout() {
    await this.client.post('/users/logout/')
    localStorage.removeItem('auth_token')
  }

  async getCurrentUser() {
    const response = await this.client.get('/users/me/')
    return response.data
  }

  // Admin endpoints
  async getDashboardStats() {
    const response = await this.client.get('/admin/dashboard/stats/')
    return response.data
  }

  async getTrainers(params?: { search?: string; status?: string; plan?: string }) {
    const response = await this.client.get('/admin/trainers/', { params })
    return response.data
  }

  async getTrainer(id: number) {
    const response = await this.client.get(`/admin/trainers/${id}/`)
    return response.data
  }

  async getAnalytics(params?: { days?: number; group_by?: 'day' | 'month' }) {
    const response = await this.client.get('/admin/dashboard/analytics/', { params })
    return response.data
  }

  // Generic methods
  get<T = any>(url: string, config?: any) {
    return this.client.get<T>(url, config)
  }

  post<T = any>(url: string, data?: any, config?: any) {
    return this.client.post<T>(url, data, config)
  }

  put<T = any>(url: string, data?: any, config?: any) {
    return this.client.put<T>(url, data, config)
  }

  patch<T = any>(url: string, data?: any, config?: any) {
    return this.client.patch<T>(url, data, config)
  }

  delete<T = any>(url: string, config?: any) {
    return this.client.delete<T>(url, config)
  }
}

export const apiClient = new ApiClient()
export default apiClient
```

---

## Step 1.5: Zustand Store Setup

### 1.5.1 Auth Store (src/store/authStore.ts)

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import apiClient from '@/lib/api'
import type { User } from '@/types/user'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (data: {
    email: string
    username: string
    first_name: string
    last_name: string
    password: string
    password_confirm: string
  }) => Promise<void>
  fetchCurrentUser: () => Promise<void>
  setToken: (token: string) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const data = await apiClient.login(email, password)
          localStorage.setItem('auth_token', data.token)
          set({
            token: data.token,
            user: data,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (data) => {
        set({ isLoading: true })
        try {
          const response = await apiClient.register(data)
          localStorage.setItem('auth_token', response.token)
          set({
            token: response.token,
            user: response,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: async () => {
        try {
          await apiClient.logout()
        } catch (error) {
          // Continue with logout even if API call fails
        } finally {
          localStorage.removeItem('auth_token')
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          })
        }
      },

      fetchCurrentUser: async () => {
        set({ isLoading: true })
        try {
          const user = await apiClient.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          set({ isLoading: false, isAuthenticated: false })
          localStorage.removeItem('auth_token')
        }
      },

      setToken: (token: string) => {
        localStorage.setItem('auth_token', token)
        set({ token, isAuthenticated: true })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
```

### 1.5.2 Install Zustand Persist Middleware

```bash
npm install zustand
# persist middleware is included in zustand
```

---

## Step 1.6: Type Definitions

### 1.6.1 User Types (src/types/user.ts)

```typescript
export interface User {
  id: number
  email: string
  username: string
  first_name: string
  last_name: string
  phone_number?: string
  is_trainer: boolean
  is_client: boolean
  is_verified: boolean
  created_at: string
}

export interface LoginResponse {
  id: number
  email: string
  username: string
  first_name: string
  last_name: string
  token: string
  is_trainer: boolean
  is_client: boolean
}
```

### 1.6.2 API Types (src/types/api.ts)

```typescript
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
```

---

## Step 1.7: Base Layout Components

### 1.7.1 Layout Component (src/components/layout/Layout.tsx)

```typescript
import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

export function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6 lg:ml-64">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
```

### 1.7.2 Header Component (src/components/layout/Header.tsx)

```typescript
import { useAuthStore } from '@/store/authStore'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { LogOut, User, Settings } from 'lucide-react'

export function Header() {
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    await logout()
    window.location.href = '/login'
  }

  const initials = user
    ? `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase()
    : 'U'

  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-50 lg:left-64">
      <div className="h-full px-6 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">
          {import.meta.env.VITE_APP_NAME || 'TrainerHub Admin'}
        </h1>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-2 hover:opacity-80">
              <Avatar>
                <AvatarFallback>{initials}</AvatarFallback>
              </Avatar>
              <span className="hidden sm:block text-sm font-medium">
                {user?.first_name} {user?.last_name}
              </span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
```

### 1.7.3 Sidebar Component (src/components/layout/Sidebar.tsx)

```typescript
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Users, 
  BarChart3, 
  Globe,
  Menu
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Trainers', href: '/admin/trainers', icon: Users },
  { name: 'Analytics', href: '/admin/analytics', icon: BarChart3 },
  { name: 'Domains', href: '/admin/domains', icon: Globe },
]

export function Sidebar() {
  const location = useLocation()
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  return (
    <>
      {/* Mobile menu button */}
      <button
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-md shadow-md"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
      >
        <Menu className="h-6 w-6" />
      </button>

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-40 h-screen w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out lg:translate-x-0',
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="h-full flex flex-col pt-16">
          <nav className="flex-1 px-4 py-4 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setIsMobileOpen(false)}
                  className={cn(
                    'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                    isActive
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  )}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isMobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setIsMobileOpen(false)}
        />
      )}
    </>
  )
}
```

---

## Step 1.8: Routing Setup

### 1.8.1 App Component (src/App.tsx)

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useEffect } from 'react'
import { Layout } from '@/components/layout/Layout'
import { Login } from '@/pages/auth/Login'
import { Dashboard } from '@/pages/dashboard/Dashboard'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, fetchCurrentUser } = useAuthStore()

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (token && !isAuthenticated) {
      fetchCurrentUser()
    }
  }, [isAuthenticated, fetchCurrentUser])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          {/* Add more routes here */}
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

---

## Step 1.9: Basic Pages

### 1.9.1 Login Page (src/pages/auth/Login.tsx)

```typescript
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await login(email, password)
      toast({
        title: 'Success',
        description: 'Logged in successfully',
      })
      navigate('/dashboard')
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Login failed',
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Login to TrainerHub Admin</CardTitle>
          <CardDescription>Enter your credentials to access the admin panel</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="admin@trainerhubb.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Logging in...' : 'Login'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
```

### 1.9.2 Dashboard Page (src/pages/dashboard/Dashboard.tsx)

```typescript
import { useEffect, useState } from 'react'
import apiClient from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

interface DashboardStats {
  total_trainers: number
  active_trainers: number
  total_revenue: number
  monthly_recurring_revenue: number
}

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiClient.getDashboardStats()
        setStats(data)
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-500">Total Trainers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.total_trainers || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-500">Active Trainers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.active_trainers || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-500">Total Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${stats?.total_revenue?.toLocaleString() || '0'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-500">Monthly Recurring Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${stats?.monthly_recurring_revenue?.toLocaleString() || '0'}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

---

## Step 1.10: Utility Functions

### 1.10.1 Utils (src/lib/utils.ts)

```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

Install required dependencies:
```bash
npm install clsx tailwind-merge
```

---

## Step 1.11: CSS Setup

### 1.11.1 Global Styles (src/index.css)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 48%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

---

## Step 1.12: Package.json Scripts

Update `package.json` scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  }
}
```

---

## Step 1.13: Run the Project

```bash
# Start development server
npm run dev

# The app will be available at http://localhost:3000
```

---

## ✅ Epic 1.1 Completion Checklist

- [x] Vite + React + TypeScript project created
- [x] shadcn/ui installed and configured
- [x] Tailwind CSS configured
- [x] Zustand store setup (auth store)
- [x] API client configured with interceptors
- [x] Base layout components (Header, Sidebar, Layout)
- [x] Routing setup with protected routes
- [x] Login page implemented
- [x] Dashboard page with stats
- [x] Environment variables configured
- [x] Type definitions created
- [x] Utility functions added

---

## 🚀 Next Steps (Epic 1.2)

After completing Epic 1.1, proceed to:
- Trainers management page
- Analytics dashboard with charts
- Domain management page
- Enhanced UI components
- Error handling and loading states

---

## 📝 Notes

- Make sure Django backend is running on `http://localhost:8000`
- Update `.env` file with correct API URL
- All API calls use Token authentication
- Zustand persist middleware saves auth state to localStorage
- shadcn/ui components are fully customizable via CSS variables

---

**Epic 1.1 Status: ✅ READY TO IMPLEMENT**

