# TrainerHub Performance Optimization Guide

## Overview

This document outlines optimization strategies implemented and recommended for TrainerHub.

## Database Optimizations

### Query Optimization

**select_related** for foreign keys (SQL JOIN):
```python
# apps/bookings/views.py
Booking.objects.select_related('client', 'trainer').all()
```

**prefetch_related** for many-to-many and reverse foreign keys:
```python
# apps/clients/views.py
Client.objects.prefetch_related('payments', 'bookings').all()
```

### Indexes

Add indexes to frequently queried fields:

```python
class Meta:
    indexes = [
        models.Index(fields=['trainer', 'is_active']),
        models.Index(fields=['created_at']),
        models.Index(fields=['email']),
    ]
```

### Database Connection Pooling

Use PgBouncer in production:

```ini
[databases]
trainerhubb = host=localhost port=5432 dbname=trainerhubb_prod

[pgbouncer]
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
```

## Caching Strategy

### Redis Configuration

See `config/settings/caching.py` for full configuration.

### Caching Views

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 15), name='dispatch')  # 15 minutes
class PublicPageView(DetailView):
    pass
```

### Caching Querysets

```python
from django.core.cache import cache

def get_trainer_pages(trainer_id):
    cache_key = f'trainer_pages_{trainer_id}'
    pages = cache.get(cache_key)
    
    if pages is None:
        pages = Page.objects.filter(trainer_id=trainer_id, is_published=True)
        cache.set(cache_key, pages, timeout=300)  # 5 minutes
    
    return pages
```

### Cache Invalidation

```python
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete

@receiver(post_save, sender=Page)
def invalidate_page_cache(sender, instance, **kwargs):
    cache_key = f'trainer_pages_{instance.trainer_id}'
    cache.delete(cache_key)
```

## Frontend Optimization

### Vite Configuration

Update `trainer-app/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: false, gzipSize: true })
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['lucide-react', '@radix-ui/react-dialog'],
          'api-vendor': ['axios', 'zustand']
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true  // Remove console.logs in production
      }
    }
  }
})
```

### Lazy Loading Routes

Update `trainer-app/src/App.tsx`:

```typescript
import { lazy, Suspense } from 'react';

const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ClientsManagementPage = lazy(() => import('./pages/ClientsManagementPage'));
const BookingsPage = lazy(() => import('./pages/BookingsPage'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/clients" element={<ClientsManagementPage />} />
        <Route path="/bookings" element={<BookingsPage />} />
      </Routes>
    </Suspense>
  );
}
```

### Image Optimization

Use Cloudinary transformations:

```typescript
const optimizedImageUrl = (url: string, width: number) => {
  return url.replace('/upload/', `/upload/w_${width},q_auto,f_auto/`);
};
```

### Code Splitting

Split large components:

```typescript
const HeavyComponent = lazy(() => import('./HeavyComponent'));

function MyComponent() {
  return (
    <Suspense fallback={<Spinner />}>
      <HeavyComponent />
    </Suspense>
  );
}
```

## API Optimization

### Pagination

All list endpoints use pagination:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}
```

### Filtering & Search

Use django-filter for efficient filtering:

```python
from django_filters.rest_framework import DjangoFilterBackend

class BookingViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status', 'booking_date']
    search_fields = ['client__name', 'notes']
```

### Compression

Enable GZIP compression:

```python
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    # ... other middleware
]
```

## Static Files

### Whitenoise Configuration

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### CDN

Use Cloudflare or AWS CloudFront:

```python
AWS_S3_CUSTOM_DOMAIN = 'd111111abcdef8.cloudfront.net'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

## Monitoring & Profiling

### Django Debug Toolbar (Development)

```bash
pip install django-debug-toolbar
```

```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### Query Counting

```python
from django.db import connection

def view_function(request):
    # Your code
    print(f"Queries: {len(connection.queries)}")
```

### New Relic APM

```bash
pip install newrelic

# Run with:
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn config.wsgi
```

## Load Testing

### Using Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.client.post("/api/users/login/", json={
            "email": "test@example.com",
            "password": "test123"
        })
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/bookings/")
    
    @task(1)
    def create_booking(self):
        self.client.post("/api/bookings/", json={
            "client_id": 1,
            "booking_date": "2024-01-15",
            "start_time": "10:00"
        })
```

Run:
```bash
locust -f locustfile.py
```

## Performance Benchmarks

Target metrics:
- API response time: < 200ms (p95)
- Page load time: < 2 seconds
- Time to Interactive: < 3 seconds
- Database query count per request: < 10
- React bundle size: < 500KB gzipped

## Scaling Checklist

- [ ] Optimize database queries (select_related, prefetch_related)
- [ ] Add database indexes
- [ ] Implement caching (Redis)
- [ ] Enable GZIP compression
- [ ] Use CDN for static files
- [ ] Lazy load routes
- [ ] Code split large components
- [ ] Minify and compress frontend assets
- [ ] Implement database connection pooling
- [ ] Set up database read replicas
- [ ] Use load balancer for multiple app servers
- [ ] Monitor query performance
- [ ] Implement API rate limiting
- [ ] Optimize images (Cloudinary)
- [ ] Enable HTTP/2
- [ ] Use service workers for offline support

## Quick Wins

1. **Add select_related to views**: 5 minutes, huge impact
2. **Enable caching**: 10 minutes, significant improvement
3. **Lazy load routes**: 15 minutes, faster initial load
4. **Optimize images**: 5 minutes, faster page loads
5. **Enable GZIP**: 2 minutes, smaller transfers

## Tools

- **Backend**: Django Debug Toolbar, django-silk, New Relic
- **Frontend**: React DevTools, Lighthouse, WebPageTest
- **Database**: pgAdmin, pg_stat_statements, EXPLAIN ANALYZE
- **Load Testing**: Locust, Apache Bench, Artillery
- **Monitoring**: New Relic, Datadog, Sentry

---

For performance issues, contact: performance@trainerhubb.app

