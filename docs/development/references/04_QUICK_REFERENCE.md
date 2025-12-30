# 📚 TRAINERHUB - QUICK REFERENCE

Fast lookup guide for common tasks, commands, and API endpoints. **Bookmark this file!**

---

## 🚀 SETUP COMMANDS

### Create Virtual Environment as this system is using ubuntu
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Create Django Project
```bash
django-admin startproject config .
mkdir apps
python manage.py startapp users apps/users
python manage.py startapp trainers apps/trainers
python manage.py startapp clients apps/clients
python manage.py startapp availability apps/availability
python manage.py startapp bookings apps/bookings
python manage.py startapp packages apps/packages
python manage.py startapp payments apps/payments
python manage.py startapp notifications apps/notifications
python manage.py startapp analytics apps/analytics
```

### Database Setup (supabase)
```bash
# Create PostgreSQL database
createdb trainerhub

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## 📊 DATABASE SCHEMA QUICK VIEW

### 12 Tables Overview

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **auth_user** | User accounts | email, username, password_hash |
| **trainers_trainer** | Trainer profiles | user_id, business_name, rating |
| **clients_client** | Client info | trainer_id, email, fitness_level |
| **availability_availabilityslot** | Availability | trainer_id, day_of_week, start_time |
| **availability_trainerbreak** | Time off | trainer_id, start_date, end_date |
| **bookings_booking** | Bookings | trainer_id, client_id, start_time, status |
| **packages_sessionpackage** | Session packages | trainer_id, name, price |
| **packages_clientpackage** | Client packages | client_id, session_package_id |
| **payments_subscription** | Subscriptions | trainer_id, paddle_subscription_id |
| **payments_payment** | Payments | subscription_id, amount, status |
| **notifications_notification** | Email/SMS logs | trainer_id, type, message |
| **analytics_dashboardmetrics** | Analytics data | trainer_id, date, revenue |

---

## 🔗 API ENDPOINTS (50+ Total)

### Authentication Endpoints (5)

```
POST   /api/users/register/
       Body: { email, username, password, first_name, last_name }
       Returns: { id, email, token }

POST   /api/users/login/
       Body: { email, password }
       Returns: { id, email, token }

POST   /api/users/logout/
       Headers: Authorization: Token <token>
       Returns: { message: "Logged out" }

GET    /api/users/me/
       Headers: Authorization: Token <token>
       Returns: { id, email, username, first_name, last_name }

POST   /api/users/change-password/
       Body: { old_password, new_password }
       Returns: { message: "Password changed" }
```

### Trainer Endpoints (10)

```
POST   /api/trainers/create-profile/
       Body: { business_name, bio, expertise, location, timezone }
       Returns: Trainer object

GET    /api/trainers/me/
       Returns: Current trainer profile

PATCH  /api/trainers/me/
       Body: { business_name, bio, expertise, ... }
       Returns: Updated trainer object

GET    /api/trainers/{id}/
       Returns: Public trainer profile

GET    /api/trainers/{id}/clients/
       Returns: List of trainer's clients

GET    /api/trainers/{id}/bookings/
       Returns: List of trainer's bookings

GET    /api/trainers/{id}/stats/
       Returns: { total_clients, total_bookings, avg_rating }

POST   /api/trainers/{id}/reviews/
       Body: { rating, comment, client_id }
       Returns: Review object

GET    /api/trainers/{id}/reviews/
       Returns: List of trainer reviews

DELETE /api/trainers/{id}/reviews/{review_id}/
       Returns: { message: "Review deleted" }
```

### Client Endpoints (8)

```
POST   /api/clients/
       Body: { email, first_name, last_name, fitness_level, goals }
       Returns: Client object

GET    /api/clients/
       Returns: List of trainer's clients

GET    /api/clients/{id}/
       Returns: Client details

PATCH  /api/clients/{id}/
       Body: { first_name, last_name, fitness_level, goals }
       Returns: Updated client

DELETE /api/clients/{id}/
       Returns: { message: "Client deleted" }

GET    /api/clients/{id}/bookings/
       Returns: List of client's bookings

GET    /api/clients/{id}/packages/
       Returns: List of client's packages

POST   /api/clients/{id}/notes/
       Body: { note }
       Returns: Note object
```

### Availability Endpoints (8)

```
POST   /api/availability/
       Body: { day_of_week, start_time, end_time, is_recurring }
       Returns: AvailabilitySlot object

GET    /api/availability/
       Returns: List of trainer's availability slots

PATCH  /api/availability/{id}/
       Body: { start_time, end_time, is_active }
       Returns: Updated slot

DELETE /api/availability/{id}/
       Returns: { message: "Slot deleted" }

GET    /api/availability/available-slots/
       Query: ?trainer_id=1&start_date=2025-01-01&end_date=2025-01-31
       Returns: { available_slots: [...] }

POST   /api/availability/breaks/
       Body: { start_date, end_date, reason }
       Returns: TrainerBreak object

GET    /api/availability/breaks/
       Returns: List of trainer breaks

DELETE /api/availability/breaks/{id}/
       Returns: { message: "Break deleted" }
```

### Booking Endpoints (8)

```
POST   /api/bookings/
       Body: { client_id, start_time, end_time }
       Returns: Booking object

GET    /api/bookings/
       Returns: List of bookings

GET    /api/bookings/{id}/
       Returns: Booking details

PATCH  /api/bookings/{id}/
       Body: { status, notes }
       Returns: Updated booking

DELETE /api/bookings/{id}/
       Returns: { message: "Booking deleted" }

GET    /api/bookings/{id}/history/
       Returns: Booking history

POST   /api/bookings/{id}/confirm/
       Returns: { message: "Booking confirmed" }

POST   /api/bookings/{id}/cancel/
       Body: { reason }
       Returns: { message: "Booking cancelled" }
```

### Package Endpoints (6)

```
POST   /api/packages/
       Body: { name, description, sessions_count, price }
       Returns: SessionPackage object

GET    /api/packages/
       Returns: List of packages

PATCH  /api/packages/{id}/
       Body: { name, price, sessions_count }
       Returns: Updated package

DELETE /api/packages/{id}/
       Returns: { message: "Package deleted" }

GET    /api/packages/{id}/clients/
       Returns: Clients using this package

POST   /api/packages/{id}/assign/
       Body: { client_id }
       Returns: { message: "Package assigned" }
```

### Payment Endpoints (5)

```
POST   /api/subscriptions/
       Body: { paddle_subscription_id, status }
       Returns: Subscription object

GET    /api/subscriptions/
       Returns: List of subscriptions

PATCH  /api/subscriptions/{id}/
       Body: { status }
       Returns: Updated subscription

GET    /api/payments/
       Returns: List of payments

POST   /api/webhooks/paddle/
       (Paddle webhook - auto-called)
       Returns: { message: "Webhook processed" }
```

### Analytics Endpoints (6)

```
GET    /api/analytics/dashboard/
       Returns: { total_revenue, bookings, clients, avg_rating }

GET    /api/analytics/revenue/
       Returns: { total, this_month, this_week, trend }

GET    /api/analytics/bookings/
       Returns: { total, completed, cancelled, avg_duration }

GET    /api/analytics/clients/
       Returns: { total, active, new, retention_rate }

GET    /api/analytics/trainers/
       Returns: { total, avg_rating, most_booked }

GET    /api/analytics/export/
       Query: ?format=csv&start_date=2025-01-01&end_date=2025-01-31
       Returns: CSV file
```

---

## 🔐 SECURITY CHECKLIST

```bash
# Django Security Settings
✅ SECRET_KEY in .env (never hardcoded)
✅ DEBUG=False in production
✅ ALLOWED_HOSTS configured
✅ CSRF protection enabled
✅ CORS headers configured
✅ Password hashing (PBKDF2)
✅ Token authentication
✅ Input validation on all endpoints
✅ Rate limiting on sensitive endpoints
✅ SQL injection prevention (ORM)
✅ XSS prevention (template escaping)
✅ HTTPS/SSL in production
✅ Regular security updates
✅ Error tracking (Sentry)
```

---

## 📝 COMMON PATTERNS

### Custom User Model
```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

### Serializer with Validation
```python
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email exists")
        return value.lower()
```

### ViewSet with Permissions
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class TrainerViewSet(viewsets.ModelViewSet):
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
```

### Query Optimization
```python
# ✅ Good - single query
trainers = Trainer.objects.select_related('user').all()

# ✅ Good - prefetch related
bookings = Booking.objects.prefetch_related('client').all()

# ❌ Bad - N+1 query
trainers = Trainer.objects.all()
for trainer in trainers:
    print(trainer.user.email)  # Extra query each iteration!
```

### Background Task (Celery)
```python
from celery import shared_task

@shared_task
def send_booking_confirmation(booking_id):
    booking = Booking.objects.get(id=booking_id)
    # Send email async
    send_email(booking.client.email, ...)
```

### Caching
```python
from django.core.cache import cache

# Set cache
cache.set('trainer:1:profile', trainer_data, timeout=60*5)

# Get cache
data = cache.get('trainer:1:profile')

# Delete cache
cache.delete('trainer:1:profile')
```

---

## 🧪 TESTING COMMANDS

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=apps

# Run specific test class
pytest tests/test_models.py::UserTestCase

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test Structure
```python
import pytest
from django.test import TestCase

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
    
    def test_user_login(self):
        authenticated = User.objects.filter(
            email='test@example.com'
        ).exists()
        self.assertTrue(authenticated)
```

---

## 🚀 DEPLOYMENT COMMANDS

```bash
# Collect static files
python manage.py collectstatic --noinput

# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create Docker image
docker build -t trainerhub:latest .

# Run Docker container
docker run -p 8000:8000 trainerhub:latest

# Push to registry
docker push your-registry/trainerhub:latest
```

---

## 📋 .env TEMPLATE

```env
# Django
DEBUG=False
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=trainerhub
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxxxx

# SMS (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890

# Payments (Paddle)
PADDLE_VENDOR_ID=12345
PADDLE_API_KEY=xxxxx

# Frontend
FRONTEND_URL=https://yourdomain.com
SUPPORT_EMAIL=support@yourdomain.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

---

## 🔗 USEFUL LINKS

### Documentation
- Django: https://docs.djangoproject.com
- DRF: https://www.django-rest-framework.org
- PostgreSQL: https://postgresql.org/docs
- Celery: https://docs.celeryproject.io
- Paddle: https://developer.paddle.com

### Tools
- Postman: https://www.postman.com
- Insomnia: https://insomnia.rest
- pgAdmin: https://www.pgadmin.org
- Redis Desktop: https://redisdesktop.com

### Security
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Django Security: https://docs.djangoproject.com/en/stable/topics/security/
- Rate Limiting: https://django-ratelimit.readthedocs.io

---

## 💡 TROUBLESHOOTING

### Common Issues

**ModuleNotFoundError**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Database Connection Error**
```bash
# Solution: Check PostgreSQL is running
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Windows
net start postgresql-x64-XX
```

**Permission Denied on Migrations**
```bash
# Solution: Run migrations
python manage.py migrate
```

**Redis Connection Error**
```bash
# Solution: Start Redis
redis-server

# Or with Homebrew
brew services start redis
```

**Celery Task Not Running**
```bash
# Solution: Start Celery worker
celery -A config worker -l info
```

**Static Files Not Loading**
```bash
# Solution: Collect static files
python manage.py collectstatic
```

---

## 📊 PERFORMANCE TIPS

### Database
- Use `select_related()` for ForeignKey relationships
- Use `prefetch_related()` for reverse ForeignKey/M2M
- Create indexes on frequently queried fields
- Use pagination for large result sets

### Caching
- Cache frequently accessed data (Redis)
- Cache database query results
- Cache external API responses
- Set appropriate cache timeouts

### API
- Use pagination (limit results)
- Use filtering to reduce data
- Use compression (gzip)
- Use CDN for static files

### Async Tasks
- Use Celery for email/SMS sending
- Use Celery for heavy computations
- Use Celery for scheduled tasks
- Don't do heavy work in views

---

## ✅ FINAL CHECKLIST

Before deploying to production:

- [ ] All tests passing
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Error tracking setup (Sentry)
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] SSL certificate installed
- [ ] HTTPS enforced
- [ ] Security headers set
- [ ] Rate limiting active
- [ ] Logging configured
- [ ] Database optimized
- [ ] Cache warmed up
- [ ] CDN configured

---

## 🎯 KEY TAKEAWAYS

**Remember:**
- Always validate input
- Always check permissions
- Always use HTTPS in production
- Always log important events
- Always test before deploying
- Always backup your data
- Always monitor performance
- Always respond to errors gracefully

---

**Bookmark this page! You'll reference it constantly during development.** 📌

Next file: TECH_STACK_REFERENCE.md - Ask me when ready!
