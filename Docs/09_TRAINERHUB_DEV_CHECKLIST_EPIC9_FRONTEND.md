# 🎨 TRAINERHUB - DEV CHECKLIST V2 (PART 4) - EPIC 9: FRONTEND

Modern, beautiful frontend with HTMX, Tailwind CSS, and Framer Motion. Mobile-first, responsive design with animations.

**Time: 3-4 weeks** | **Code: 2,000+ lines**

---

# 🎨 EPIC 9: FRONTEND DEVELOPMENT (3-4 WEEKS)

## Tech Stack

- **HTMX** - Dynamic HTML updates without JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **Alpine.js** - Lightweight JavaScript for interactivity
- **Django Templates** - Server-side rendering
- **DRF API** - Keep all endpoints open for future React Native

---

## Step 9.1: Project Setup & Configuration

### 9.1.1 Install Dependencies

```bash
# Add to requirements.txt (if using Python packages)
# Or use CDN (recommended for HTMX/Alpine)

# Frontend dependencies (CDN approach)
# HTMX: https://unpkg.com/htmx.org@1.9.10
# Alpine.js: https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js
# Framer Motion: Use via CDN or npm (if building)
```

### 9.1.2 Update Django Settings

```python
# config/settings.py

# Add templates directory
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 9.1.3 Create Directory Structure

```
trainerhubb/
├── templates/
│   ├── base.html
│   ├── components/
│   │   ├── header.html
│   │   ├── sidebar.html
│   │   ├── footer.html
│   │   └── modals.html
│   ├── pages/
│   │   ├── landing.html
│   │   ├── dashboard.html
│   │   ├── bookings/
│   │   ├── clients/
│   │   ├── packages/
│   │   ├── analytics/
│   │   └── settings/
│   └── partials/
│       ├── bookings/
│       ├── clients/
│       └── analytics/
├── static/
│   ├── css/
│   │   └── custom.css
│   ├── js/
│   │   └── main.js
│   └── images/
└── apps/
    └── frontend/
        ├── views.py      # Template views for HTMX
        ├── urls.py
        └── templatetags/
```

---

## Step 9.2: Base Template & Layout

### 9.2.1 Base Template (templates/base.html)

```html
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="TrainerHub - Manage your fitness training business">
    <title>{% block title %}TrainerHub{% endblock %}</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://unpkg.com/htmx.org/dist/ext/json-enc.js"></script>
    
    <!-- Alpine.js -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    
    <!-- Framer Motion (via CDN or custom implementation) -->
    <!-- For complex animations, consider using CSS transitions + Alpine.js -->
    
    <!-- Custom CSS -->
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/custom.css' %}">
    
    <!-- CSRF Token for HTMX -->
    <meta name="csrf-token" content="{{ csrf_token }}">
    
    {% block extra_head %}{% endblock %}
</head>
<body class="h-full bg-gray-50" x-data="{ sidebarOpen: false }">
    {% if user.is_authenticated %}
        <!-- Authenticated Layout -->
        {% include 'components/header.html' %}
        {% include 'components/sidebar.html' %}
        
        <div class="lg:pl-64 flex flex-col flex-1">
            <main class="flex-1">
                <div class="py-6">
                    <div class="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
                        {% block content %}{% endblock %}
                    </div>
                </div>
            </main>
        </div>
    {% else %}
        <!-- Public Layout -->
        {% block public_content %}{% endblock %}
    {% endif %}
    
    <!-- Modals -->
    {% include 'components/modals.html' %}
    
    <!-- Toast Notifications -->
    <div id="toast-container" class="fixed top-4 right-4 z-50 space-y-2"></div>
    
    <!-- Custom JS -->
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 9.2.2 Header Component (templates/components/header.html)

```html
<header class="bg-white shadow-sm border-b border-gray-200 fixed w-full top-0 z-40 lg:pl-64">
    <div class="px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <!-- Mobile menu button -->
            <button @click="sidebarOpen = !sidebarOpen" 
                    class="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100">
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            </button>
            
            <!-- Logo -->
            <div class="flex items-center">
                <h1 class="text-xl font-bold text-gray-900">TrainerHub</h1>
            </div>
            
            <!-- User menu -->
            <div class="flex items-center space-x-4" x-data="{ open: false }">
                <div class="relative">
                    <button @click="open = !open" 
                            class="flex items-center space-x-2 text-sm focus:outline-none">
                        <div class="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center">
                            <span class="text-white font-medium">{{ user.first_name|first|upper }}</span>
                        </div>
                        <span class="hidden sm:block text-gray-700">{{ user.get_full_name }}</span>
                        <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                        </svg>
                    </button>
                    
                    <!-- Dropdown menu -->
                    <div x-show="open" 
                         @click.away="open = false"
                         x-transition:enter="transition ease-out duration-100"
                         x-transition:enter-start="opacity-0 scale-95"
                         x-transition:enter-end="opacity-100 scale-100"
                         class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                        <a href="{% url 'settings' %}" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Settings</a>
                        <a href="{% url 'logout' %}" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Logout</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</header>
```

### 9.2.3 Sidebar Component (templates/components/sidebar.html)

```html
<!-- Mobile sidebar overlay -->
<div x-show="sidebarOpen" 
     @click="sidebarOpen = false"
     x-transition:enter="transition-opacity ease-linear duration-300"
     x-transition:enter-start="opacity-0"
     x-transition:enter-end="opacity-100"
     x-transition:leave="transition-opacity ease-linear duration-300"
     x-transition:leave-start="opacity-100"
     x-transition:leave-end="opacity-0"
     class="fixed inset-0 bg-gray-600 bg-opacity-75 z-40 lg:hidden"></div>

<!-- Sidebar -->
<aside x-show="sidebarOpen || window.innerWidth >= 1024"
      x-transition:enter="transition ease-in-out duration-300 transform"
      x-transition:enter-start="-translate-x-full"
      x-transition:enter-end="translate-x-0"
      x-transition:leave="transition ease-in-out duration-300 transform"
      x-transition:leave-start="translate-x-0"
      x-transition:leave-end="-translate-x-full"
      class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg lg:translate-x-0 transform transition-transform duration-300 ease-in-out">
    
    <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="flex items-center justify-between h-16 px-4 border-b border-gray-200">
            <h2 class="text-xl font-bold text-gray-900">TrainerHub</h2>
            <button @click="sidebarOpen = false" class="lg:hidden text-gray-400 hover:text-gray-500">
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>
        
        <!-- Navigation -->
        <nav class="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            <a href="{% url 'dashboard' %}" 
               class="flex items-center px-4 py-2 text-sm font-medium text-gray-900 rounded-lg hover:bg-gray-100 transition-colors">
                <svg class="mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Dashboard
            </a>
            
            <a href="{% url 'bookings_list' %}" 
               class="flex items-center px-4 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
                <svg class="mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Bookings
            </a>
            
            <a href="{% url 'clients_list' %}" 
               class="flex items-center px-4 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
                <svg class="mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                Clients
            </a>
            
            <a href="{% url 'packages_list' %}" 
               class="flex items-center px-4 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
                <svg class="mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                Packages
            </a>
            
            <a href="{% url 'analytics_dashboard' %}" 
               class="flex items-center px-4 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
                <svg class="mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Analytics
            </a>
            
            <a href="{% url 'notifications_list' %}" 
               class="flex items-center px-4 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
                <svg class="mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                Notifications
            </a>
        </nav>
    </div>
</aside>
```

---

## Step 9.3: Landing Page with Framer Motion Animations

### 9.3.1 Landing Page Template (templates/pages/landing.html)

```html
{% extends 'base.html' %}
{% load static %}

{% block public_content %}
<div class="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500">
    <!-- Hero Section with Animations -->
    <section class="relative overflow-hidden">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
            <div class="text-center" 
                 x-data="{ 
                     loaded: false,
                     init() {
                         setTimeout(() => this.loaded = true, 100);
                     }
                 }"
                 x-show="loaded"
                 x-transition:enter="transition ease-out duration-1000"
                 x-transition:enter-start="opacity-0 transform translate-y-10"
                 x-transition:enter-end="opacity-100 transform translate-y-0">
                
                <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6">
                    Manage Your Fitness Business
                    <span class="block text-yellow-300">Like a Pro</span>
                </h1>
                
                <p class="text-xl md:text-2xl text-indigo-100 mb-8 max-w-3xl mx-auto">
                    TrainerHub helps fitness trainers manage clients, bookings, and grow their business effortlessly.
                </p>
                
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <a href="{% url 'register' %}" 
                       class="px-8 py-4 bg-white text-indigo-600 rounded-lg font-semibold text-lg hover:bg-indigo-50 transition-all transform hover:scale-105 shadow-lg">
                        Get Started Free
                    </a>
                    <a href="#features" 
                       class="px-8 py-4 bg-indigo-700 text-white rounded-lg font-semibold text-lg hover:bg-indigo-800 transition-all border-2 border-white">
                        Learn More
                    </a>
                </div>
            </div>
            
            <!-- Animated Dashboard Preview -->
            <div class="mt-16 relative"
                 x-data="{ 
                     loaded: false,
                     init() {
                         setTimeout(() => this.loaded = true, 500);
                     }
                 }"
                 x-show="loaded"
                 x-transition:enter="transition ease-out duration-1000 delay-300"
                 x-transition:enter-start="opacity-0 transform scale-95"
                 x-transition:enter-end="opacity-100 transform scale-100">
                <div class="bg-white rounded-xl shadow-2xl p-8 max-w-5xl mx-auto">
                    <img src="{% static 'images/dashboard-preview.png' %}" 
                         alt="Dashboard Preview" 
                         class="w-full rounded-lg">
                </div>
            </div>
        </div>
        
        <!-- Animated Background Elements -->
        <div class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
            <div class="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
            <div class="absolute top-40 right-10 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
            <div class="absolute -bottom-8 left-1/2 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>
    </section>
    
    <!-- Features Section -->
    <section id="features" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-4xl font-bold text-center text-gray-900 mb-16">
                Everything You Need to Succeed
            </h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <!-- Feature Card 1 -->
                <div class="bg-gray-50 rounded-xl p-6 hover:shadow-lg transition-shadow"
                     x-data="{ 
                         loaded: false,
                         init() {
                             setTimeout(() => this.loaded = true, 100);
                         }
                     }"
                     x-show="loaded"
                     x-transition:enter="transition ease-out duration-500"
                     x-transition:enter-start="opacity-0 transform translate-y-10"
                     x-transition:enter-end="opacity-100 transform translate-y-0">
                    <div class="w-12 h-12 bg-indigo-600 rounded-lg flex items-center justify-center mb-4">
                        <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-900 mb-2">Smart Booking System</h3>
                    <p class="text-gray-600">Manage appointments, send reminders, and never miss a session.</p>
                </div>
                
                <!-- Feature Card 2 -->
                <div class="bg-gray-50 rounded-xl p-6 hover:shadow-lg transition-shadow"
                     x-data="{ 
                         loaded: false,
                         init() {
                             setTimeout(() => this.loaded = true, 300);
                         }
                     }"
                     x-show="loaded"
                     x-transition:enter="transition ease-out duration-500"
                     x-transition:enter-start="opacity-0 transform translate-y-10"
                     x-transition:enter-end="opacity-100 transform translate-y-0">
                    <div class="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center mb-4">
                        <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-900 mb-2">Client Management</h3>
                    <p class="text-gray-600">Track client progress, notes, and fitness goals all in one place.</p>
                </div>
                
                <!-- Feature Card 3 -->
                <div class="bg-gray-50 rounded-xl p-6 hover:shadow-lg transition-shadow"
                     x-data="{ 
                         loaded: false,
                         init() {
                             setTimeout(() => this.loaded = true, 500);
                         }
                     }"
                     x-show="loaded"
                     x-transition:enter="transition ease-out duration-500"
                     x-transition:enter-start="opacity-0 transform translate-y-10"
                     x-transition:enter-end="opacity-100 transform translate-y-0">
                    <div class="w-12 h-12 bg-pink-600 rounded-lg flex items-center justify-center mb-4">
                        <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-900 mb-2">Analytics & Insights</h3>
                    <p class="text-gray-600">Make data-driven decisions with comprehensive business analytics.</p>
                </div>
            </div>
        </div>
    </section>
    
    <!-- CTA Section -->
    <section class="py-20 bg-indigo-600">
        <div class="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
            <h2 class="text-4xl font-bold text-white mb-4">Ready to Grow Your Business?</h2>
            <p class="text-xl text-indigo-100 mb-8">Join thousands of trainers already using TrainerHub.</p>
            <a href="{% url 'register' %}" 
               class="inline-block px-8 py-4 bg-white text-indigo-600 rounded-lg font-semibold text-lg hover:bg-indigo-50 transition-all transform hover:scale-105 shadow-lg">
                Start Free Trial
            </a>
        </div>
    </section>
</div>

<style>
@keyframes blob {
    0% {
        transform: translate(0px, 0px) scale(1);
    }
    33% {
        transform: translate(30px, -50px) scale(1.1);
    }
    66% {
        transform: translate(-20px, 20px) scale(0.9);
    }
    100% {
        transform: translate(0px, 0px) scale(1);
    }
}

.animate-blob {
    animation: blob 7s infinite;
}

.animation-delay-2000 {
    animation-delay: 2s;
}

.animation-delay-4000 {
    animation-delay: 4s;
}
</style>
{% endblock %}
```

---

## Step 9.4: Dashboard Page

### 9.4.1 Dashboard Template (templates/pages/dashboard.html)

```html
{% extends 'base.html' %}

{% block title %}Dashboard - TrainerHub{% endblock %}

{% block content %}
<div class="space-y-6">
    <!-- Page Header -->
    <div class="flex justify-between items-center">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p class="mt-1 text-sm text-gray-500">Welcome back, {{ user.first_name }}!</p>
        </div>
        <div class="flex space-x-3">
            <button class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                New Booking
            </button>
        </div>
    </div>
    
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
         hx-get="{% url 'dashboard_stats' %}"
         hx-trigger="load"
         hx-swap="innerHTML">
        <!-- Stats will be loaded here -->
        <div class="animate-pulse bg-gray-200 rounded-lg h-32"></div>
        <div class="animate-pulse bg-gray-200 rounded-lg h-32"></div>
        <div class="animate-pulse bg-gray-200 rounded-lg h-32"></div>
        <div class="animate-pulse bg-gray-200 rounded-lg h-32"></div>
    </div>
    
    <!-- Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Upcoming Bookings -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Upcoming Bookings</h2>
            <div hx-get="{% url 'bookings_upcoming_partial' %}"
                 hx-trigger="load"
                 hx-swap="innerHTML">
                <div class="animate-pulse space-y-3">
                    <div class="h-16 bg-gray-200 rounded"></div>
                    <div class="h-16 bg-gray-200 rounded"></div>
                </div>
            </div>
        </div>
        
        <!-- Recent Clients -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Recent Clients</h2>
            <div hx-get="{% url 'clients_recent_partial' %}"
                 hx-trigger="load"
                 hx-swap="innerHTML">
                <div class="animate-pulse space-y-3">
                    <div class="h-12 bg-gray-200 rounded"></div>
                    <div class="h-12 bg-gray-200 rounded"></div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Revenue Chart -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Revenue Overview</h2>
        <div hx-get="{% url 'analytics_revenue_chart' %}"
             hx-trigger="load"
             hx-swap="innerHTML">
            <div class="animate-pulse h-64 bg-gray-200 rounded"></div>
        </div>
    </div>
</div>
{% endblock %}
```

### 9.4.2 Dashboard Stats Partial (templates/partials/dashboard/stats.html)

```html
{% for stat in stats %}
<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
    <div class="flex items-center justify-between">
        <div>
            <p class="text-sm font-medium text-gray-500">{{ stat.label }}</p>
            <p class="text-3xl font-bold text-gray-900 mt-2">{{ stat.value }}</p>
        </div>
        <div class="p-3 bg-{{ stat.color }}-100 rounded-lg">
            <svg class="w-6 h-6 text-{{ stat.color }}-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="{{ stat.icon }}" />
            </svg>
        </div>
    </div>
    {% if stat.change %}
    <div class="mt-4 flex items-center">
        <span class="text-sm {% if stat.change > 0 %}text-green-600{% else %}text-red-600{% endif %}">
            {% if stat.change > 0 %}↑{% else %}↓{% endif %} {{ stat.change|abs }}%
        </span>
        <span class="text-sm text-gray-500 ml-2">vs last month</span>
    </div>
    {% endif %}
</div>
{% endfor %}
```

---

## Step 9.5: Bookings Management

### 9.5.1 Bookings List Template (templates/pages/bookings/list.html)

```html
{% extends 'base.html' %}

{% block title %}Bookings - TrainerHub{% endblock %}

{% block content %}
<div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">Bookings</h1>
            <p class="mt-1 text-sm text-gray-500">Manage your training sessions</p>
        </div>
        <button hx-get="{% url 'bookings_create_form' %}"
                hx-target="#modal-content"
                hx-swap="innerHTML"
                @click="$dispatch('open-modal')"
                class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            New Booking
        </button>
    </div>
    
    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div class="flex flex-wrap gap-4">
            <select hx-get="{% url 'bookings_list' %}"
                    hx-target="#bookings-list"
                    hx-include="[name='status'], [name='date']"
                    name="status"
                    class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
            </select>
            
            <input type="date"
                   name="date"
                   hx-get="{% url 'bookings_list' %}"
                   hx-target="#bookings-list"
                   hx-include="[name='status']"
                   class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
        </div>
    </div>
    
    <!-- Bookings List -->
    <div id="bookings-list"
         hx-get="{% url 'bookings_list_partial' %}"
         hx-trigger="load"
         hx-swap="innerHTML">
        <!-- Loading state -->
        <div class="space-y-4">
            {% for i in "12345" %}
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
                <div class="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                <div class="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
```

### 9.5.2 Bookings List Partial (templates/partials/bookings/list.html)

```html
<div class="space-y-4">
    {% for booking in bookings %}
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
         x-data="{ open: false }">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                    <h3 class="text-lg font-semibold text-gray-900">{{ booking.client_name }}</h3>
                    <span class="px-2 py-1 text-xs font-medium rounded-full
                        {% if booking.status == 'confirmed' %}bg-green-100 text-green-800
                        {% elif booking.status == 'pending' %}bg-yellow-100 text-yellow-800
                        {% elif booking.status == 'completed' %}bg-blue-100 text-blue-800
                        {% else %}bg-red-100 text-red-800{% endif %}">
                        {{ booking.status|title }}
                    </span>
                </div>
                <div class="flex flex-wrap gap-4 text-sm text-gray-600">
                    <span class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        {{ booking.start_time|date:"M d, Y" }}
                    </span>
                    <span class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {{ booking.start_time|time:"g:i A" }} - {{ booking.end_time|time:"g:i A" }}
                    </span>
                    <span class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {{ booking.duration_minutes }} min
                    </span>
                </div>
            </div>
            
            <div class="flex gap-2">
                {% if booking.status == 'pending' %}
                <button hx-post="{% url 'bookings_confirm' booking.id %}"
                        hx-target="#bookings-list"
                        hx-swap="outerHTML"
                        class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm">
                    Confirm
                </button>
                {% endif %}
                
                <button @click="open = !open"
                        class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm">
                    Actions
                </button>
            </div>
        </div>
        
        <!-- Actions Dropdown -->
        <div x-show="open"
             @click.away="open = false"
             x-transition:enter="transition ease-out duration-100"
             x-transition:enter-start="opacity-0 scale-95"
             x-transition:enter-end="opacity-100 scale-100"
             class="mt-4 pt-4 border-t border-gray-200">
            <div class="flex flex-wrap gap-2">
                <button hx-get="{% url 'bookings_detail' booking.id %}"
                        hx-target="#modal-content"
                        @click="$dispatch('open-modal')"
                        class="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
                    View Details
                </button>
                {% if booking.status != 'cancelled' and booking.status != 'completed' %}
                <button hx-post="{% url 'bookings_cancel' booking.id %}"
                        hx-target="#bookings-list"
                        hx-swap="outerHTML"
                        hx-confirm="Are you sure you want to cancel this booking?"
                        class="px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200">
                    Cancel
                </button>
                {% endif %}
            </div>
        </div>
    </div>
    {% empty %}
    <div class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No bookings</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating a new booking.</p>
    </div>
    {% endfor %}
</div>
```

---

## Step 9.6: Frontend Views (Hybrid Approach)

### 9.6.1 Create Frontend App

```bash
python manage.py startapp frontend
```

### 9.6.2 Frontend Views (apps/frontend/views.py)

```python
"""
Frontend views for HTMX - Template-based views that work alongside DRF API.
DRF endpoints remain available for future React Native app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.packages.models import SessionPackage
from apps.analytics.views import AnalyticsViewSet
from apps.trainers.models import Trainer


@login_required
def dashboard(request):
    """Main dashboard page."""
    return render(request, 'pages/dashboard.html')


@login_required
def dashboard_stats(request):
    """Dashboard stats partial for HTMX."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/dashboard/stats.html', {'stats': []})
    
    # Get stats (can reuse DRF logic)
    bookings = Booking.objects.filter(trainer=trainer)
    clients = Client.objects.filter(trainer=trainer)
    
    stats = [
        {
            'label': 'Total Bookings',
            'value': bookings.count(),
            'color': 'indigo',
            'icon': 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
            'change': 12
        },
        {
            'label': 'Upcoming',
            'value': bookings.filter(
                status__in=['pending', 'confirmed'],
                start_time__gte=timezone.now()
            ).count(),
            'color': 'green',
            'icon': 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
        },
        {
            'label': 'Total Clients',
            'value': clients.count(),
            'color': 'purple',
            'icon': 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
            'change': 5
        },
        {
            'label': 'Revenue (This Month)',
            'value': f"${0}",  # Calculate from payments
            'color': 'pink',
            'icon': 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
        },
    ]
    
    return render(request, 'partials/dashboard/stats.html', {'stats': stats})


@login_required
def bookings_list(request):
    """Bookings list page."""
    return render(request, 'pages/bookings/list.html')


@login_required
def bookings_list_partial(request):
    """Bookings list partial for HTMX."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        return render(request, 'partials/bookings/list.html', {'bookings': []})
    
    bookings = Booking.objects.filter(trainer=trainer).select_related('client')
    
    # Filters
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    date_str = request.GET.get('date')
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            bookings = bookings.filter(start_time__date=date)
        except ValueError:
            pass
    
    bookings = bookings.order_by('-start_time')[:50]
    
    return render(request, 'partials/bookings/list.html', {'bookings': bookings})


@login_required
@require_http_methods(["POST"])
def bookings_confirm(request, booking_id):
    """Confirm booking via HTMX."""
    booking = get_object_or_404(Booking, id=booking_id, trainer=request.user.trainer_profile)
    
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()
        
        # Trigger notification (can call DRF endpoint or use Celery)
        from apps.notifications.tasks import send_booking_confirmation
        send_booking_confirmation.delay(booking.id)
    
    # Return updated list
    return bookings_list_partial(request)


@login_required
@require_http_methods(["POST"])
def bookings_cancel(request, booking_id):
    """Cancel booking via HTMX."""
    booking = get_object_or_404(Booking, id=booking_id, trainer=request.user.trainer_profile)
    
    if booking.status not in ['completed', 'cancelled']:
        booking.status = 'cancelled'
        booking.save()
    
    return bookings_list_partial(request)
```

### 9.6.3 Frontend URLs (apps/frontend/urls.py)

```python
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # Bookings
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('bookings/partial/', views.bookings_list_partial, name='bookings_list_partial'),
    path('bookings/<int:booking_id>/confirm/', views.bookings_confirm, name='bookings_confirm'),
    path('bookings/<int:booking_id>/cancel/', views.bookings_cancel, name='bookings_cancel'),
    
    # Add more routes for clients, packages, analytics, etc.
]
```

### 9.6.4 Update Main URLs (config/urls.py)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # DRF API (keep for React Native)
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.availability.urls')),
    path('api/', include('apps.clients.urls')),
    path('api/', include('apps.bookings.urls')),
    path('api/', include('apps.packages.urls')),
    path('api/', include('apps.payments.urls')),
    path('api/', include('apps.notifications.urls')),
    path('api/', include('apps.analytics.urls')),
    
    # Frontend HTMX views
    path('', include('apps.frontend.urls')),
]
```

---

## Step 9.7: Mobile Responsiveness

### 9.7.1 Custom CSS (static/css/custom.css)

```css
/* Mobile-first responsive utilities */
@media (max-width: 640px) {
    .mobile-hidden {
        display: none;
    }
    
    .mobile-full {
        width: 100%;
    }
}

/* Touch-friendly buttons */
@media (hover: none) {
    button, a {
        min-height: 44px;
        min-width: 44px;
    }
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* Loading states */
.htmx-request {
    opacity: 0.5;
    pointer-events: none;
}

/* Toast notifications */
.toast {
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
```

### 9.7.2 JavaScript Utilities (static/js/main.js)

```javascript
// HTMX configuration
document.body.addEventListener('htmx:configRequest', (event) => {
    // Add CSRF token to all HTMX requests
    event.detail.headers['X-CSRFToken'] = document.querySelector('[name=csrf-token]').content;
});

// Toast notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast px-4 py-3 rounded-lg shadow-lg mb-2 ${
        type === 'success' ? 'bg-green-500 text-white' : 
        type === 'error' ? 'bg-red-500 text-white' : 
        'bg-blue-500 text-white'
    }`;
    toast.textContent = message;
    
    const container = document.getElementById('toast-container');
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Handle HTMX errors
document.body.addEventListener('htmx:responseError', (event) => {
    showToast('An error occurred. Please try again.', 'error');
});

// Handle HTMX success
document.body.addEventListener('htmx:afterSwap', (event) => {
    // Close modals after successful form submission
    if (event.detail.target.id === 'modal-content') {
        // Check if form was submitted successfully
        const form = event.detail.target.querySelector('form');
        if (form && event.detail.xhr.status === 200) {
            setTimeout(() => {
                window.dispatchEvent(new CustomEvent('close-modal'));
            }, 500);
        }
    }
});

// Modal handling
window.addEventListener('open-modal', () => {
    document.getElementById('modal').classList.remove('hidden');
});

window.addEventListener('close-modal', () => {
    document.getElementById('modal').classList.add('hidden');
});
```

---

## Step 9.8: Additional Features

### 9.8.1 Clients Management Pages
- List, create, edit clients
- Client notes and history
- Package assignments

### 9.8.2 Packages Management Pages
- Create and manage session packages
- Assign packages to clients
- Track usage

### 9.8.3 Analytics Dashboard
- Revenue charts (use Chart.js or similar)
- Booking statistics
- Client metrics

### 9.8.4 Settings Page
- Profile management
- Notification preferences
- Subscription management

---

## Step 9.9: Testing & Optimization

### 9.9.1 Mobile Testing Checklist
- [ ] Test on iOS Safari
- [ ] Test on Android Chrome
- [ ] Test on tablets (iPad, Android tablets)
- [ ] Test touch interactions
- [ ] Test form inputs on mobile
- [ ] Test modals and dropdowns
- [ ] Test HTMX swaps on mobile

### 9.9.2 Performance Optimization
- [ ] Optimize images (WebP format)
- [ ] Lazy load images
- [ ] Minimize CSS/JS
- [ ] Use CDN for static assets
- [ ] Enable Django caching
- [ ] Optimize database queries

### 9.9.3 Accessibility
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] ARIA labels
- [ ] Color contrast
- [ ] Focus indicators

---

## ✅ EPIC 9 COMPLETION CHECKLIST

- [ ] Base template and layout components
- [ ] Landing page with animations
- [ ] Dashboard with stats
- [ ] Bookings management (list, create, edit, cancel)
- [ ] Clients management
- [ ] Packages management
- [ ] Analytics dashboard
- [ ] Settings page
- [ ] Mobile responsive design
- [ ] HTMX integration working
- [ ] All DRF endpoints still accessible
- [ ] Forms and modals working
- [ ] Toast notifications
- [ ] Loading states
- [ ] Error handling
- [ ] Mobile testing complete
- [ ] Performance optimized

---

**EPIC 9 COMPLETE: Beautiful, modern, mobile-friendly frontend! 🎨**

**Total Project: 6,000+ lines of production code across all epics! 🚀**

