# 🛠️ TRAINERHUB - TECH STACK REFERENCE

Detailed breakdown of each technology and why it was chosen.

---

## 📊 TECHNOLOGY OVERVIEW

```
┌─────────────────────────────────────────────────────┐
│              TRAINERHUB TECH STACK                  │
├─────────────────────────────────────────────────────┤
│ Frontend        │ HTML5 + HTMX + TailwindCSS       │
├─────────────────────────────────────────────────────┤
│ Backend         │ Django 5 + Django REST Framework │
├─────────────────────────────────────────────────────┤
│ Database        │ PostgreSQL + Redis    supabase           │
├─────────────────────────────────────────────────────┤
│ Task Queue      │ Celery + Redis Broker            │
├─────────────────────────────────────────────────────┤
│ Payments        │ Paddle                           │
├─────────────────────────────────────────────────────┤
│ Email           │ SendGrid                         │
├─────────────────────────────────────────────────────┤
│ SMS             │ Twilio                           │
├─────────────────────────────────────────────────────┤
│ Hosting         │ Docker + Cloud (AWS/GCP/Azure) + digital ocean droplet  │
├─────────────────────────────────────────────────────┤
│ Monitoring      │ Sentry + ELK Stack               │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 BACKEND: DJANGO 5

### Why Django?

**Maturity & Stability**
- First released: 2008 (15+ years)
- Used by: Instagram, Pinterest, Spotify, Pinterest
- LTS versions with 3-year support
- Battle-tested in production

**Security Built-In**
- CSRF protection out of box
- XSS prevention (template escaping)
- SQL injection prevention (ORM)
- Password hashing with PBKDF2
- Secure headers defaults
- Regular security patches

**Developer Productivity**
- "Batteries included" philosophy
- Admin interface (saves 40% of dev time)
- ORM (no raw SQL needed)
- Form validation built-in
- Authentication system included
- Migration system for database changes

**Scalability**
- Used at Instagram scale (300M+ users)
- Horizontal scaling (stateless)
- Connection pooling
- Query optimization tools
- Caching framework
- Async task support (Celery)

**Performance**
- Fast request handling (<200ms typical)
- QuerySet lazy evaluation
- Database connection pooling
- Middleware optimization
- Template caching

### Installation & Setup

```bash
# Install Django
pip install django==5.0

# Create project
django-admin startproject config .

# Create app
python manage.py startapp users

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Key Django Features Used

**Models (ORM)**
```python
from django.db import models

class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    bio = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Admin Interface**
```python
from django.contrib import admin

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('business_name', 'user__email')
```

---

## 🔌 API: DJANGO REST FRAMEWORK (DRF)

### Why DRF?

**RESTful API Made Easy**
- Built for REST APIs (not templated responses)
- Automatic serialization/deserialization
- Built-in API authentication
- Browsable API for testing
- Pagination out of box
- Filtering & searching

**Quality of Life**
- Auto-generated API documentation
- Request/response validation
- Permission classes
- Throttling & rate limiting
- Versioning support
- Error handling

**Production Ready**
- Used by: Uber, Stripe, Eventbrite, Mozilla
- Mature ecosystem
- Excellent documentation
- Community support
- Security best practices

### Installation & Setup

```bash
pip install djangorestframework
```

### Settings Configuration

```python
# settings.py
INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}
```

### Serializers

```python
from rest_framework import serializers

class TrainerSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Trainer
        fields = ['id', 'user_email', 'business_name', 'rating']
    
    def validate_business_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Name too short")
        return value
```

### ViewSets & Routers

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class TrainerViewSet(viewsets.ModelViewSet):
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        trainer = self.get_object()
        return Response({
            'total_clients': trainer.client_set.count(),
            'total_bookings': trainer.booking_set.count(),
        })

# URLs
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'trainers', TrainerViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

---

## 🗄️ DATABASE: POSTGRESQL

### Why PostgreSQL?

**Advanced Features**
- JSONB data type (hybrid relational/document)
- Full-text search
- Window functions
- Common Table Expressions (CTEs)
- Array types
- UUID support
- Range types

**Reliability**
- ACID compliance (guaranteed data integrity)
- Multi-version concurrency control (MVCC)
- Point-in-time recovery
- Replication support
- Excellent crash recovery

**Performance**
- Sophisticated query planner
- Index types: B-tree, Hash, GiST, GIN
- Partial indexes
- Index-only scans
- Parallel query execution
- Query result caching

**Scalability**
- Handle 1000+ connections
- Database partitioning
- Sharding support
- Replication capabilities
- Good for analytics

**Cost**
- Free (open source)
- No licensing costs
- Runs on cheaper hardware
- No vendor lock-in

### Installation

```bash
# macOS
brew install postgresql@15

# Linux (Ubuntu)
sudo apt-get install postgresql-15

# Windows
# Download from postgresql.org/download
```

### Database Setup

```bash
# Create database
createdb trainerhub

# Connect to database
psql trainerhub

# Create user
CREATE USER trainer WITH PASSWORD 'password';
ALTER ROLE trainer CREATEDB;
```

### Django Configuration

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trainerhub',
        'USER': 'trainer',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

### Performance Optimization

```python
# Query optimization
trainers = Trainer.objects.select_related('user').all()

# Pagination
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

# Database indexes
class Trainer(models.Model):
    email = models.EmailField(unique=True)  # Auto-indexed
    
    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['rating']),
        ]
```

---

## ⚡ CACHE: REDIS

### Why Redis?

**Performance**
- In-memory data store (microsecond access)
- ~1 million operations/second
- Reduce database load
- Session caching
- Query result caching

**Features**
- Key-value store
- Data structures (lists, sets, hashes)
- Pub/Sub messaging
- Transactions
- Persistence (RDB, AOF)
- Replication

**Use Cases**
- Session management
- Cache layer
- Rate limiting
- Real-time features
- Message broker (for Celery)
- Leaderboards

### Installation

```bash
# macOS
brew install redis

# Linux
sudo apt-get install redis-server

# Windows
# Download from redis.io/download
```

### Django Configuration

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### Usage Examples

```python
from django.core.cache import cache

# Set cache
cache.set('trainer:1:profile', trainer_data, timeout=60*5)

# Get cache
data = cache.get('trainer:1:profile')

# Delete cache
cache.delete('trainer:1:profile')

# View-level caching
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)
def available_slots(request):
    return Response(available_slots)
```

---

## 📬 TASK QUEUE: CELERY

### Why Celery?

**Asynchronous Tasks**
- Send emails without blocking requests
- Heavy computations in background
- Scheduled tasks
- Retry failed tasks
- Task monitoring

**Scalability**
- Process thousands of tasks/second
- Distribute tasks across workers
- Load balancing
- Worker auto-scaling

**Reliability**
- Task persistence
- Automatic retry
- Task timeouts
- Dead letter handling
- Task result storage

### Installation

```bash
pip install celery redis
```

### Configuration

```python
# config/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('trainerhub')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

### Task Definition

```python
# apps/notifications/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation(booking_id):
    booking = Booking.objects.get(id=booking_id)
    send_mail(
        subject='Booking Confirmed',
        message=f'Your booking with {booking.trainer.business_name} is confirmed',
        from_email='noreply@trainerhub.com',
        recipient_list=[booking.client.email],
    )

# Usage
send_booking_confirmation.delay(booking_id)
```

### Scheduled Tasks

```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-booking-reminders': {
        'task': 'apps.notifications.tasks.send_reminders',
        'schedule': crontab(hour=10, minute=0),  # Daily at 10am
    },
    'generate-daily-reports': {
        'task': 'apps.analytics.tasks.generate_reports',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}
```

### Running Celery

```bash
# Start Celery worker
celery -A config worker -l info

# Start Celery beat (scheduler)
celery -A config beat -l info

# Monitor tasks
celery -A config events
```

---

## 💳 PAYMENTS: PADDLE

### Why Paddle?

**SaaS-Focused**
- Built for SaaS platforms
- Subscription management
- Global payment methods
- Automatic tax handling
- Multi-currency support

**Easy Integration**
- REST API
- Webhooks
- Pre-built UI
- Customer portal
- Invoice generation

**Low Fees**
- 5-8% per transaction (competitive)
- No setup fees
- No monthly fees
- Transparent pricing

**Compliance**
- Handles VAT/GST globally
- PCI compliance
- Secure payment processing
- Regulatory compliance

### Installation

```bash
pip install paddle-python
```

### Configuration

```python
# settings.py
PADDLE_VENDOR_ID = os.getenv('PADDLE_VENDOR_ID')
PADDLE_API_KEY = os.getenv('PADDLE_API_KEY')

# .env
PADDLE_VENDOR_ID=12345
PADDLE_API_KEY=xxxxx
```

### Usage

```python
# apps/payments/paddle_service.py
import requests

class PaddleService:
    BASE_URL = 'https://api.paddle.com/2.0'
    
    def create_subscription(self, customer_email, plan_id):
        response = requests.post(
            f'{self.BASE_URL}/customers',
            headers={'Authorization': f'Bearer {PADDLE_API_KEY}'},
            json={'email': customer_email}
        )
        return response.json()
    
    def create_checkout(self, product_id, customer_email):
        # Create checkout link
        pass
    
    def cancel_subscription(self, subscription_id):
        # Cancel subscription
        pass
```

### Webhook Handling

```python
# apps/payments/webhook.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def paddle_webhook(request):
    if request.method == 'POST':
        event = request.POST.get('event_type')
        
        if event == 'subscription.created':
            # Handle new subscription
            pass
        elif event == 'subscription.cancelled':
            # Handle cancellation
            pass
        elif event == 'transaction.completed':
            # Handle payment
            pass
    
    return JsonResponse({'status': 'ok'})
```

---

## 📧 EMAIL: SENDGRID

### Why SendGrid?

**Reliability**
- 99.9% uptime
- Global delivery network
- Bounce handling
- Spam filtering

**Features**
- Email templates
- Dynamic content
- Scheduled sending
- Delivery tracking
- Analytics
- Subaccount management

**Scale**
- Send millions of emails/day
- Automatic scaling
- Rate limiting
- Webhook integration

### Installation

```bash
pip install sendgrid
```

### Configuration

```python
# settings.py
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
```

### Usage

```python
# apps/notifications/email_service.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(SENDGRID_API_KEY)
    
    def send_booking_confirmation(self, client_email, booking):
        message = Mail(
            from_email='noreply@trainerhub.com',
            to_emails=client_email,
            subject='Booking Confirmation',
            plain_text_content=f'Your booking with {booking.trainer.business_name} is confirmed',
            html_content='<strong>Booking Confirmed</strong>'
        )
        response = self.client.send(message)
        return response.status_code
```

---

## 📱 SMS: TWILIO

### Why Twilio?

**Global Coverage**
- SMS to 200+ countries
- Reliable delivery (99.5%+)
- Two-way messaging
- Short codes
- Phone number verification

**Features**
- SMS API
- WhatsApp API
- Programmatic voice calls
- Video calling
- Number masking

**Scalability**
- Handle millions of messages/day
- Auto-scaling
- Built-in retry
- Delivery tracking

### Installation

```bash
pip install twilio
```

### Configuration

```python
# settings.py
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# .env
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890
```

### Usage

```python
# apps/notifications/sms_service.py
from twilio.rest import Client

class SMSService:
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    def send_booking_reminder(self, client_phone, booking):
        message = self.client.messages.create(
            body=f'Reminder: Your session with {booking.trainer.business_name} is tomorrow at {booking.start_time}',
            from_=TWILIO_PHONE_NUMBER,
            to=client_phone
        )
        return message.sid
```

---

## 🐳 DEPLOYMENT: DOCKER

### Why Docker?

**Consistency**
- Same environment dev/staging/prod
- No "works on my machine" issues
- Reproducible deployments
- Easy onboarding

**Scalability**
- Easy to scale horizontally
- Container orchestration (Kubernetes)
- Load balancing
- Blue-green deployments

**Efficiency**
- Lightweight vs virtual machines
- Fast startup times
- Resource isolation
- Easy rollbacks

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:password@db:5432/trainerhub
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: trainerhub
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  
  celery:
    build: .
    command: celery -A config worker -l info
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

---

## 📊 MONITORING: SENTRY

### Why Sentry?

**Error Tracking**
- Automatic error detection
- Stack traces
- Breadcrumbs
- User context
- Source maps

**Alerting**
- Real-time notifications
- Slack integration
- Email alerts
- Custom alerts

**Performance Monitoring**
- Transaction tracing
- Performance metrics
- Slow transaction detection

### Installation

```bash
pip install sentry-sdk
```

### Configuration

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=False
)
```

---

## 🎨 FRONTEND: HTML + HTMX + TAILWINDCSS

### Why This Stack?

**Lightweight**
- No heavy JavaScript framework
- Small bundle size
- Fast page loads
- Good for mobile

**Server-Driven**
- HTMX sends requests to server
- Server returns HTML fragments
- Browser swaps content
- No JSON parsing
- Progressive enhancement

**Productivity**
- TailwindCSS for rapid styling
- Semantic HTML
- Server-side templating (Django)
- No build step needed

### HTMX Example

```html
<!-- Booking form with live availability check -->
<form hx-post="/api/bookings/" 
      hx-target="#confirmation"
      hx-on="htmx:afterRequest: if(event.detail.xhr.status==201) htmx.redirect('/')">
    <input type="date" name="date" required>
    <input type="time" name="time" required>
    <button type="submit">Book Now</button>
</form>

<div id="confirmation"></div>
```

### TailwindCSS Example

```html
<div class="bg-blue-500 text-white p-4 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-2">Booking Confirmed</h2>
    <p class="text-sm text-blue-100">Your session is scheduled for tomorrow</p>
</div>
```

---

## 📈 COMPARISON WITH ALTERNATIVES

### Backend Alternatives

| Framework | Pros | Cons |
|-----------|------|------|
| **Django** ✅ | Batteries included, secure, scalable | Monolithic, slower for simple APIs |
| **FastAPI** | Fast, modern, async | Smaller ecosystem |
| **Flask** | Lightweight, flexible | Too minimal for this project |
| **Node.js** | Fast, JavaScript everywhere | Less mature ecosystem |

### Database Alternatives

| Database | Pros | Cons |
|----------|------|------|
| **PostgreSQL** ✅ | Advanced features, reliable, scales well | Heavier than SQLite |
| **MySQL** | Popular, good performance | Less advanced features than Postgres |
| **MongoDB** | Flexible schema, fast | Not ACID compliant |
| **SQLite** | Simple, serverless | Not for production |

### Payment Alternatives

| Service | Pros | Cons |
|---------|------|------|
| **Paddle** ✅ | SaaS-focused, global, low fees | Limited payment methods |
| **Stripe** | Popular, feature-rich | Higher fees, complex |
| **PayPal** | Well-known, global | Not ideal for subscriptions |
| **Square** | Simple, affordable | Less flexible |

---

## 💾 SYSTEM REQUIREMENTS

### Development

- Python 3.11+
- PostgreSQL 13+
- Redis 6.0+
- 4GB RAM minimum
- 50GB disk space

### Production

- Python 3.11+
- PostgreSQL 13+ (managed service recommended)
- Redis 6.0+ (managed service recommended)
- 8GB RAM minimum
- 100GB disk space (SSD)
- Load balancer
- CDN for static files

---

## 🚀 TECHNOLOGY JUSTIFICATION SUMMARY

| Technology | Why It's Perfect |
|-----------|-----------------|
| **Django** | Mature, secure, batteries-included for rapid development |
| **DRF** | REST API best practices built-in |
| **PostgreSQL** | Advanced features, reliability, scalability |
| **Redis** | Fast caching and Celery broker |
| **Celery** | Background tasks without blocking |
| **Paddle** | SaaS-focused, easy payments |
| **SendGrid** | Reliable email at scale |
| **Twilio** | Global SMS delivery |
| **Docker** | Consistent deployments |
| **Sentry** | Production error tracking |
| **HTMX** | Lightweight interactivity |
| **TailwindCSS** | Rapid UI development |

---

## 📚 NEXT STEPS

1. **Install all dependencies** (see requirements.txt)
2. **Setup PostgreSQL & Redis** (local development)
3. **Configure .env file** (with API keys)
4. **Run migrations** (create database schema)
5. **Start building EPIC 1** (user authentication)

---

**Next file: INDEX.md** - Ask me when ready!
