# 🤖 AI AGENT PROMPT - TRAINERHUB IMPLEMENTATION GUIDE

**Version:** 2.0
**Purpose:** Complete instructions for AI to implement TrainerHub SaaS platform
**Status:** Production-Ready

---

## 🎯 CORE MISSION

You are an expert full-stack Django developer tasked with implementing a complete, production-ready SaaS booking platform called **TrainerHubb**. Your mission is to:

1. **Read and understand** the 15 reference files
2. **Implement** code from FILES 7-9 step-by-step
3. **Follow best practices** for production Django development
4. **Ensure quality** through testing and validation
5. **Complete deployment** configuration

---

## 📋 DETAILED INSTRUCTIONS FOR AI AGENT

### PHASE 1: INFORMATION GATHERING (READ ALL FILES FIRST)

**Duration:** 30 minutes
**Goal:** Understand the complete project scope and architecture

#### Step 1.1: Read Learning Files (10 min)
```
READ IN THIS ORDER:
1. FILE 1: 00_READ_ME_FIRST.txt
   - Purpose: Understand what you're building
   - Focus: Project overview, problem/solution
   - Action: Absorb the high-level context

2. FILE 2: START_HERE.md
   - Purpose: Understand project structure
   - Focus: Architecture, features, tech choices
   - Action: Map out the feature list

3. FILE 5: QUICK_REFERENCE.md (BOOKMARK THIS)
   - Purpose: Keep as constant reference
   - Focus: All 50+ API endpoints with examples
   - Action: Search this whenever you need endpoint info
```

#### Step 1.2: Understand Architecture (10 min)
```
READ:
4. FILE 4: TRAINERHUB_FINAL_SUMMARY.md
   - Purpose: Technical architecture
   - Focus: Database schema (12 tables), relationships
   - Action: Draw entity-relationship diagram in your mind
   
5. FILE 6: TECH_STACK_REFERENCE.md
   - Purpose: Why each technology was chosen
   - Focus: Django, PostgreSQL, Celery, Paddle, etc.
   - Action: Understand trade-offs and decisions

Optional but recommended:
6. FILE 3: EXECUTIVE_SUMMARY.txt
   - Purpose: Business context
   - Focus: Market opportunity, pricing, success metrics
   - Action: Understand business implications
```

#### Step 1.3: Create Project Map (10 min)
```
After reading, create a mental model:

PROJECT STRUCTURE:
trainerhub/
├── config/              (Django settings)
├── apps/
│   ├── users/           (EPIC 1)
│   ├── availability/    (EPIC 2)
│   ├── clients/         (EPIC 3)
│   ├── bookings/        (EPIC 4)
│   ├── packages/        (EPIC 5)
│   ├── payments/        (EPIC 6)
│   ├── notifications/   (EPIC 7)
│   └── analytics/       (EPIC 8)
├── manage.py
├── requirements.txt
├── .env
└── docker-compose.yml

DATABASE TABLES (12 TOTAL):
1. User (custom auth)
2. Trainer (profile)
3. Client (fitness info)
4. AvailabilitySlot (weekly slots)
5. TrainerBreak (vacation)
6. Booking (session record)
7. SessionPackage (pricing)
8. ClientPackage (purchases)
9. Subscription (Paddle)
10. Payment (transactions)
11. Notification (logs)
12. DashboardMetrics (analytics)
```

---

### PHASE 2: ENVIRONMENT SETUP (1 hour)

**Duration:** 1 hour
**Goal:** Create working development environment

#### Step 2.1: Project Initialization
```bash
# Create project directory structure
mkdir trainerhub && cd trainerhub
mkdir -p apps config tests docs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Create requirements.txt with these core packages:
Django==5.0.1
djangorestframework==3.14.0
django-cors-headers==4.3.1
python-decouple==3.8
psycopg2-binary==2.9.9
celery==5.3.4
redis==5.0.1
requests==2.31.0
sendgrid==6.11.0
twilio==8.10.0
gunicorn==21.2.0
pytest==7.4.3
pytest-django==4.7.0

# Install
pip install -r requirements.txt
```

#### Step 2.2: Django Project Setup
```bash
# Create Django project
django-admin startproject config .

# Create apps
python manage.py startapp users
python manage.py startapp availability
python manage.py startapp clients
python manage.py startapp bookings
python manage.py startapp packages
python manage.py startapp payments
python manage.py startapp notifications
python manage.py startapp analytics

# Create .env file from template
cat > .env << EOF
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=postgresql://postgres:password@localhost:5432/trainerhub_db
REDIS_URL=redis://localhost:6379/0
PADDLE_API_KEY=your-paddle-key
PADDLE_WEBHOOK_SECRET=your-webhook-secret
SENDGRID_API_KEY=your-sendgrid-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
EOF
```

#### Step 2.3: Database Setup
```bash
# Start PostgreSQL
# On macOS: brew services start postgresql
# On Linux: sudo systemctl start postgresql
# On Windows: Start PostgreSQL service

# Create database
createdb trainerhub_db

# Update settings.py with PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trainerhub_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Install Redis
# On macOS: brew services start redis
# On Linux: sudo systemctl start redis
# On Windows: Download and start redis-server.exe
```

---

### PHASE 3: EPIC-BY-EPIC IMPLEMENTATION (13 hours)

**Duration:** 13 hours total
**Goal:** Implement all 8 EPICs with full functionality

#### ⚠️ CRITICAL IMPLEMENTATION RULES

Before implementing any EPIC, follow these rules ALWAYS:

**RULE 1: Copy Code Exactly**
- Copy code from FILES 7-9 EXACTLY as written
- Do NOT modify or "improve" code logic
- If code seems wrong, it's probably intentional for learning
- DO fix obvious typos or syntax errors

**RULE 2: Follow Step-by-Step Order**
- EPIC 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8
- Within each EPIC, follow steps in order
- Don't skip steps
- Test after each step before moving to next

**RULE 3: Run Migrations After Models**
```bash
# After creating any models:
python manage.py makemigrations
python manage.py migrate
# VERIFY: No errors in output
```

**RULE 4: Test Endpoints After Implementation**
- Use curl examples from FILES 7-9
- Test CRUD operations
- Test validation errors
- Test permissions

**RULE 5: Create Admin Interface Immediately**
- Register models in admin.py after creating them
- Test admin interface
- Add display_list, filters, search_fields

---

### EPIC-BY-EPIC BREAKDOWN

#### 🔐 EPIC 1: USER AUTHENTICATION (3.5 hours) - FILE 7

**What you're building:**
- Custom user model with email-based authentication
- Registration/login endpoints
- Token authentication
- Password management
- User profile management

**Implementation steps from FILE 7:**

**Step 1.1: User Models (30 min)**
```
FILE 7 → Section: "Step 1.1: User Models"
File path: apps/users/models.py

IMPLEMENT:
1. Import required Django modules
2. Create User model (extending AbstractUser)
   - email field (unique)
   - is_trainer field
   - is_client field
   - Custom manager with create_user
   - Custom manager with create_superuser
3. Create UserProfile model (optional)

AFTER CODING:
- python manage.py makemigrations
- python manage.py migrate
- Verify: No errors
```

**Step 1.2: User Serializers (30 min)**
```
FILE 7 → Section: "Step 1.2: User Serializers"
File path: apps/users/serializers.py

IMPLEMENT:
1. UserRegistrationSerializer
   - email, password, password_confirm
   - Validate passwords match
   - Validate email unique
2. UserLoginSerializer
   - email, password
   - Return token on success
3. UserSerializer
   - For profile viewing
   - Read-only created_at
4. ChangePasswordSerializer
   - old_password, new_password

TESTING:
- Verify serializer validation works
- Test error messages are clear
```

**Step 1.3: User Views (45 min)**
```
FILE 7 → Section: "Step 1.3: User Views"
File path: apps/users/views.py

IMPLEMENT:
1. UserViewSet with register, login, logout
2. @action endpoints:
   - /register/ (POST)
   - /login/ (POST)
   - /logout/ (POST)
   - /profile/ (GET/PUT)
   - /change-password/ (POST)

TESTING (using curl):
# Test registration
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123","password_confirm":"pass123"}'

# Test login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Save token from response
TOKEN="token_here"

# Test authenticated request
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Token $TOKEN"
```

**Step 1.4: URL Configuration (15 min)**
```
FILE 7 → Section: "Step 1.4: URL Configuration"
File path: apps/users/urls.py

IMPLEMENT:
1. Create router with UserViewSet
2. Include in main config/urls.py

VERIFY:
- Run: python manage.py runserver
- Visit: http://localhost:8000/api/users/register/
- Should see browsable API interface
```

**Step 1.5: Admin Interface (15 min)**
```
FILE 7 → Section: "Step 1.5: Admin Interface"
File path: apps/users/admin.py

IMPLEMENT:
1. Register User with @admin.register(User)
2. Configure list_display, list_filter, search_fields
3. Set readonly_fields for created_at, updated_at

VERIFY:
- python manage.py createsuperuser
- Visit: http://localhost:8000/admin/
- Login and see User model
```

**EPIC 1 COMPLETION CHECKLIST:**
- [ ] User model created and migrated
- [ ] All serializers working
- [ ] Registration endpoint working
- [ ] Login endpoint returning token
- [ ] Profile endpoint working
- [ ] Password change working
- [ ] Admin interface configured
- [ ] All curl examples passing
- [ ] Validation errors clear and helpful

---

#### 📅 EPIC 2: TRAINER AVAILABILITY (3.5 hours) - FILE 7

**What you're building:**
- Weekly recurring availability slots
- Trainer vacation/breaks
- Availability calculation for bookings
- Conflict detection

**Implementation steps from FILE 7:**

**Step 2.1: Availability Models (30 min)**
```
FILE 7 → Section: "Step 2.1: Availability Models"
File path: apps/availability/models.py

IMPLEMENT:
1. AvailabilitySlot model
   - trainer (ForeignKey)
   - day_of_week (choices: 0-6, Monday-Sunday)
   - start_time (TimeField)
   - end_time (TimeField)
   - is_active (BooleanField)

2. TrainerBreak model
   - trainer (ForeignKey)
   - start_date (DateField)
   - end_date (DateField)
   - reason (CharField)

3. Add Meta classes with ordering, indexes

MIGRATION:
- python manage.py makemigrations
- python manage.py migrate
```

**Step 2.2: Availability Serializers (30 min)**
```
FILE 7 → Section: "Step 2.2: Availability Serializers"
File path: apps/availability/serializers.py

IMPLEMENT:
1. AvailabilitySlotSerializer
   - All fields
   - Validate day_of_week (0-6)
   - Validate end_time > start_time

2. TrainerBreakSerializer
   - All fields
   - Validate end_date >= start_date

TESTING:
- Test serializer validation
- Test error messages
```

**Step 2.3: Availability Views (45 min)**
```
FILE 7 → Section: "Step 2.3: Availability Views"
File path: apps/availability/views.py

IMPLEMENT:
1. AvailabilitySlotViewSet
   - get_queryset: filter by trainer
   - @action get_available_slots
   - Calculate available times for a date

2. TrainerBreakViewSet
   - CRUD operations
   - Only trainer can manage own breaks

TESTING:
# Create availability slot
curl -X POST http://localhost:8000/api/availability-slots/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "day_of_week": 1,
    "start_time": "09:00:00",
    "end_time": "17:00:00"
  }'

# Get available slots for a date
curl -X GET "http://localhost:8000/api/availability-slots/available/?date=2025-01-10" \
  -H "Authorization: Token $TOKEN"
```

**Step 2.4: Utility Functions (30 min)**
```
FILE 7 → Section: "Step 2.4: Availability Utilities"
File path: apps/availability/utils.py

IMPLEMENT:
1. has_conflict(trainer_id, start_time, end_time)
   - Check if trainer has availability
   - Check if not in break period
   - Check if no booking conflict
   - Return: True/False

2. get_available_times(trainer_id, date)
   - Find day of week
   - Get availability slots for that day
   - Remove booked times
   - Remove break times
   - Return list of available slots

LOGIC:
- Parse date to day_of_week (0=Monday)
- Query AvailabilitySlot.objects.filter(trainer=trainer, day_of_week=dow)
- Query Booking.objects.filter(trainer=trainer, start_time__date=date)
- Query TrainerBreak.objects.filter(trainer=trainer, start_date<=date, end_date>=date)
- Return available times
```

**Step 2.5: Admin Interface (15 min)**
```
FILE 7 → Section: "Step 2.5: Admin Interface"
File path: apps/availability/admin.py

IMPLEMENT:
1. Register AvailabilitySlot
   - list_display: ('trainer', 'day_of_week', 'start_time', 'end_time', 'is_active')
   - list_filter: ('day_of_week', 'is_active')
   - search_fields: ('trainer__user__email',)

2. Register TrainerBreak
   - list_display: ('trainer', 'start_date', 'end_date', 'reason')
   - list_filter: ('start_date',)
```

**EPIC 2 COMPLETION CHECKLIST:**
- [ ] AvailabilitySlot model created and migrated
- [ ] TrainerBreak model created and migrated
- [ ] Serializers validating correctly
- [ ] Availability endpoints working
- [ ] Get available slots working
- [ ] Conflict detection working
- [ ] Admin interface configured
- [ ] All curl examples passing

---

#### 👥 EPIC 3: CLIENT MANAGEMENT (1.5 hours) - FILE 8

**What you're building:**
- Client profiles with fitness information
- Client notes/progress tracking
- Search and filtering

**Implementation steps from FILE 8:**

**Step 3.1: Client Models (30 min)**
```
FILE 8 → Section: "Step 3.1: Client Models"
File path: apps/clients/models.py

IMPLEMENT:
1. Client model
   - trainer (ForeignKey to Trainer)
   - email, first_name, last_name, phone
   - fitness_level (choices: beginner, intermediate, advanced, athlete)
   - goals (JSONField, list of goals)
   - preferences (JSONField, dict)
   - notes (TextField)
   - is_active (BooleanField)

2. ClientNote model
   - client (ForeignKey to Client)
   - content (TextField)
   - created_by (ForeignKey to User)
   - created_at (auto_now_add)

MIGRATION:
- python manage.py makemigrations
- python manage.py migrate
```

**Step 3.2: Client Serializers (20 min)**
```
FILE 8 → Section: "Step 3.2: Client Serializers"
File path: apps/clients/serializers.py

IMPLEMENT:
1. ClientNoteSerializer
   - Fields: id, content, created_by_name, created_at
   - created_by_name as read-only with source='created_by.get_full_name'

2. ClientSerializer
   - Fields: all client fields + notes_count
   - get_notes_count method

3. ClientDetailSerializer
   - Extends ClientSerializer
   - Includes full notes list
   - Includes bookings_count
```

**Step 3.3: Client Views (45 min)**
```
FILE 8 → Section: "Step 3.3: Client Views"
File path: apps/clients/views.py

IMPLEMENT:
1. ClientViewSet
   - get_queryset: filter by trainer
   - Filters: fitness_level, is_active
   - Search: first_name, last_name, email, phone
   - Ordering: created_at, first_name, last_name

2. @action endpoints:
   - POST /clients/{id}/add_note/ - Add note to client
   - GET /clients/{id}/notes/ - Get all notes
   - GET /clients/{id}/bookings/ - Get all bookings

TESTING:
# Create client
curl -X POST http://localhost:8000/api/clients/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "fitness_level": "beginner",
    "goals": ["lose weight", "build strength"]
  }'

# Add note
curl -X POST http://localhost:8000/api/clients/1/add_note/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Great progress this week!"}'
```

**Step 3.4: Admin Interface (15 min)**
```
FILE 8 → Section: "Step 3.4: Admin Interface"
File path: apps/clients/admin.py

IMPLEMENT:
1. Register Client
   - list_display: ('get_full_name', 'email', 'trainer', 'fitness_level', 'is_active', 'created_at')
   - list_filter: ('fitness_level', 'is_active', 'created_at')
   - search_fields: ('first_name', 'last_name', 'email')

2. Register ClientNote
   - list_display: ('client', 'created_by', 'created_at')
   - list_filter: ('created_at', 'created_by')
```

**EPIC 3 COMPLETION CHECKLIST:**
- [ ] Client model created and migrated
- [ ] ClientNote model created and migrated
- [ ] All serializers working
- [ ] Client CRUD endpoints working
- [ ] Search and filtering working
- [ ] Add note endpoint working
- [ ] Admin interface configured
- [ ] All curl examples passing

---

#### 📅 EPIC 4: BOOKING SYSTEM (2 hours) - FILE 8

**What you're building:**
- Booking creation with conflict detection
- Status management (pending, confirmed, completed, cancelled)
- Booking history and filtering

**Implementation steps from FILE 8:**

**Step 4.1: Booking Models (30 min)**
```
FILE 8 → Section: "Step 4.1: Booking Models"
File path: apps/bookings/models.py

IMPLEMENT:
1. Booking model
   - trainer (ForeignKey)
   - client (ForeignKey)
   - start_time (DateTimeField, db_index)
   - end_time (DateTimeField)
   - status (CharField with choices)
   - notes (TextField)
   - cancellation_reason (TextField)
   - created_at, updated_at

2. Add clean() method
   - Validate end_time > start_time
   - Validate not in past
   - Call has_conflict utility

3. Add properties
   - duration_minutes
   - is_upcoming
   - is_past

MIGRATION:
- python manage.py makemigrations
- python manage.py migrate
```

**Step 4.2: Booking Serializers (30 min)**
```
FILE 8 → Section: "Step 4.2: Booking Serializers"
File path: apps/bookings/serializers.py

IMPLEMENT:
1. BookingSerializer
   - Read-only: id, created_at, duration_minutes, is_upcoming, is_past
   - client_name and trainer_name as read-only

2. BookingCreateSerializer
   - For creation: client, start_time, end_time, notes
   - Automatically add trainer from context

3. BookingDetailSerializer
   - Extends BookingSerializer
   - Includes cancellation_reason

VALIDATION:
- Validate start_time in future
- Validate end_time > start_time
- Check trainer availability (has_conflict)
```

**Step 4.3: Booking Views (45 min)**
```
FILE 8 → Section: "Step 4.3: Booking Views"
File path: apps/bookings/views.py

IMPLEMENT:
1. BookingViewSet
   - get_queryset: filter by trainer
   - Filters: status, client
   - Search: client__first_name, client__last_name, notes
   - Ordering: start_time, created_at

2. Custom actions:
   - POST /bookings/{id}/confirm/ - Confirm pending booking
   - POST /bookings/{id}/cancel/ - Cancel booking
   - POST /bookings/{id}/mark_completed/ - Mark as completed
   - GET /bookings/upcoming/ - Get upcoming bookings
   - GET /bookings/past/ - Get past bookings

3. Action validation:
   - confirm: only pending → confirmed
   - cancel: not completed/cancelled
   - mark_completed: only confirmed

TESTING:
# Create booking
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client": 1,
    "start_time": "2025-01-15T10:00:00Z",
    "end_time": "2025-01-15T11:00:00Z"
  }'

# Confirm booking
curl -X POST http://localhost:8000/api/bookings/1/confirm/ \
  -H "Authorization: Token $TOKEN"
```

**Step 4.4: Admin Interface (15 min)**
```
FILE 8 → Section: "Step 4.4: Admin Interface"
File path: apps/bookings/admin.py

IMPLEMENT:
1. Register Booking
   - list_display: ('client', 'trainer', 'start_time', 'status', 'duration_minutes')
   - list_filter: ('status', 'start_time', 'created_at')
   - search_fields: ('client__first_name', 'trainer__business_name')
   - readonly_fields: ('created_at', 'updated_at', 'duration_minutes')
   - date_hierarchy: 'start_time'
```

**EPIC 4 COMPLETION CHECKLIST:**
- [ ] Booking model created and migrated
- [ ] All serializers working
- [ ] Booking CRUD endpoints working
- [ ] Status transition endpoints working
- [ ] Conflict detection working
- [ ] Upcoming/Past views working
- [ ] Admin interface configured
- [ ] All curl examples passing
- [ ] Availability integration working

---

#### 📦 EPIC 5: SESSION PACKAGES (1 hour) - FILE 8

**What you're building:**
- Package definitions (5-pack, 10-pack, etc.)
- Package assignment to clients
- Session credit tracking

**Implementation steps from FILE 8:**

**Step 5.1: Package Models (20 min)**
```
FILE 8 → Section: "Step 5.1: Package Models"
File path: apps/packages/models.py

IMPLEMENT:
1. SessionPackage model
   - trainer (ForeignKey)
   - name (CharField)
   - description (TextField)
   - sessions_count (IntegerField)
   - price (DecimalField)
   - is_active (BooleanField)

2. ClientPackage model
   - client (ForeignKey)
   - session_package (ForeignKey)
   - sessions_remaining (IntegerField)
   - expiry_date (DateField, nullable)
   - purchased_at (auto_now_add)

3. Add properties
   - is_expired: check if past expiry_date
   - is_active: sessions_remaining > 0 AND not expired

MIGRATION:
- python manage.py makemigrations
- python manage.py migrate
```

**Step 5.2: Package Serializers (20 min)**
```
FILE 8 → Section: "Step 5.2: Package Serializers"
File path: apps/packages/serializers.py

IMPLEMENT:
1. SessionPackageSerializer
   - All fields including is_active
   - Validate sessions_count > 0
   - Validate price > 0

2. ClientPackageSerializer
   - Fields: id, session_package, package_name, sessions_remaining, expiry_date, is_expired, is_active, purchased_at
   - Read-only: purchased_at, is_expired, is_active
   - package_name as read-only with source='session_package.name'
```

**Step 5.3: Package Views (20 min)**
```
FILE 8 → Section: "Step 5.3: Package Views"
File path: apps/packages/views.py

IMPLEMENT:
1. SessionPackageViewSet
   - CRUD: create/read/update/delete
   - @action POST /packages/{id}/assign_to_client/
     - Validate client belongs to trainer
     - Create ClientPackage
     - Set sessions_remaining = sessions_count
   - @action GET /packages/{id}/client_packages/
     - Get all client packages for this package

2. ClientPackageViewSet
   - ReadOnly: can't modify directly
   - @action POST /client-packages/{id}/use_session/
     - Decrement sessions_remaining
     - Validate > 0 and not expired
     - Return updated package

TESTING:
# Create package
curl -X POST http://localhost:8000/api/packages/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "5-Pack",
    "sessions_count": 5,
    "price": "249.99"
  }'

# Assign to client
curl -X POST http://localhost:8000/api/packages/1/assign_to_client/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"client_id": 1, "expiry_date": "2025-12-31"}'

# Use session
curl -X POST http://localhost:8000/api/client-packages/1/use_session/ \
  -H "Authorization: Token $TOKEN"
```

**Step 5.4: Admin Interface (10 min)**
```
FILE 8 → Section: "Step 5.4: Admin Interface"
File path: apps/packages/admin.py

IMPLEMENT:
1. Register SessionPackage
2. Register ClientPackage
   - list_display: ('client', 'session_package', 'sessions_remaining', 'expiry_date', 'is_active')
```

**EPIC 5 COMPLETION CHECKLIST:**
- [ ] SessionPackage model created and migrated
- [ ] ClientPackage model created and migrated
- [ ] All serializers working
- [ ] Create/assign package endpoints working
- [ ] Use session endpoint working
- [ ] Expiration logic working
- [ ] Admin interface configured
- [ ] All curl examples passing

---

#### 💳 EPIC 6: PAYMENT PROCESSING (2 hours) - FILE 9

**What you're building:**
- Paddle payment integration
- Subscription management
- Webhook handling for payment events

**Implementation steps from FILE 9:**

**Step 6.1: Payment Models (20 min)**
```
FILE 9 → Section: "Step 6.1: Payment Models"
File path: apps/payments/models.py

IMPLEMENT:
1. Subscription model
   - trainer (OneToOneField)
   - paddle_subscription_id (CharField, unique)
   - status (CharField: active, paused, cancelled, expired)
   - next_billing_date (DateField)

2. Payment model
   - subscription (ForeignKey)
   - amount (DecimalField)
   - currency (CharField, default='USD')
   - paddle_transaction_id (CharField, unique)
   - status (CharField: completed, pending, failed, refunded)
   - created_at (auto_now_add)

MIGRATION:
- python manage.py makemigrations
- python manage.py migrate
```

**Step 6.2: Payment Service (20 min)**
```
FILE 9 → Section: "Step 6.2: Payment Service"
File path: apps/payments/paddle_service.py

IMPLEMENT:
1. PaddleService class
   - __init__: Setup API key and headers
   - create_checkout(trainer_id, product_id, return_url)
     - POST to Paddle API
     - Return checkout link
   - get_subscription(subscription_id)
     - GET from Paddle API
   - cancel_subscription(subscription_id)
     - POST to Paddle API

KEY POINTS:
- Use requests library
- Set Authorization header with API key
- Handle errors gracefully
- Return JSON responses

TESTING:
- These will be tested via webhooks
```

**Step 6.3: Payment Views (45 min)**
```
FILE 9 → Section: "Step 6.3: Payment Views"
File path: apps/payments/views.py

IMPLEMENT:
1. SubscriptionViewSet
   - get_queryset: filter by current trainer
   - @action POST /subscriptions/create_checkout/
     - Call paddle_service.create_checkout()
     - Return checkout URL
   - @action POST /subscriptions/{id}/cancel/
     - Call paddle_service.cancel_subscription()
     - Update subscription.status = 'cancelled'

2. PaymentViewSet (ReadOnly)
   - get_queryset: filter by trainer
   - List all payments for trainer

3. paddle_webhook view (csrf_exempt)
   - POST endpoint: /api/webhooks/paddle/
   - Verify webhook signature
   - Handle events:
     - subscription.created
     - subscription.updated
     - subscription.cancelled
     - transaction.completed
     - transaction.failed

4. Webhook handlers:
   - _handle_subscription_created
   - _handle_subscription_updated
   - _handle_subscription_cancelled
   - _handle_transaction_completed
   - _handle_transaction_failed

WEBHOOK LOGIC:
```python
# subscription.created
→ Create Subscription record with paddle_subscription_id

# transaction.completed
→ Create Payment record with status='completed'

# transaction.failed
→ Create Payment record with status='failed'
```

**Step 6.4: Admin Interface (10 min)**
```
FILE 9 → Section: "Step 6.4: Admin Interface"
File path: apps/payments/admin.py

IMPLEMENT:
1. Register Subscription
2. Register Payment
   - list_display: ('subscription', 'amount', 'currency', 'status', 'created_at')
```

**EPIC 6 COMPLETION CHECKLIST:**
- [ ] Subscription model created and migrated
- [ ] Payment model created and migrated
- [ ] PaddleService working
- [ ] Subscription endpoints working
- [ ] Webhook endpoint accessible
- [ ] Webhook handler parsing events correctly
- [ ] Subscription created/cancelled working
- [ ] Payment records created on webhook
- [ ] Admin interface configured

**PADDLE SETUP:**
```
1. Sign up for Paddle account
2. Create products for subscriptions
3. Get API key and webhook secret
4. Configure webhook URL: https://yourdomain.com/api/webhooks/paddle/
5. Add keys to .env:
   PADDLE_API_KEY=...
   PADDLE_WEBHOOK_SECRET=...
```

---

#### 📬 EPIC 7: NOTIFICATIONS (1.5 hours) - FILE 9

**What you're building:**
- Email notifications via SendGrid
- SMS notifications via Twilio
- Background task processing with Celery
- Booking reminders at 24h and 1h

**Implementation steps from FILE 9:**

**Step 7.1: Notification Models (15 min)**
```
FILE 9 → Section: "Step 7.1: Notification Models"
File path: apps/notifications/models.py

IMPLEMENT:
1. Notification model
   - trainer (ForeignKey)
   - notification_type (CharField: email, sms, push)
   - recipient (CharField: email or phone)
   - subject (CharField, for email)
   - message (TextField)
   - status (CharField: pending, sent, failed)
   - sent_at (DateTimeField, nullable)
   - failed_reason (TextField)
   - created_at (auto_now_add)

MIGRATION:
- python manage.py makemigrations
- python manage.py migrate
```

**Step 7.2: Email Service (20 min)**
```
FILE 9 → Section: "Step 7.2: Email Service"
File path: apps/notifications/email_service.py

IMPLEMENT:
1. EmailService class using SendGrid
   - __init__: Setup SendGridAPIClient
   - send_booking_confirmation(client_email, booking)
   - send_booking_reminder(client_email, booking, hours_before)
   - send_payment_receipt(trainer_email, payment)
   - _render_template(template_name, context) - static method

KEY POINTS:
- Use sendgrid library
- Create HTML templates in templates/emails/
- Use Mail class from sendgrid.helpers.mail
- Return (success: bool, response_code: int)

TEMPLATES NEEDED:
- templates/emails/booking_confirmation.html
- templates/emails/booking_reminder.html
- templates/emails/payment_receipt.html

TEMPLATE CONTENT:
```html
<!-- booking_confirmation.html -->
<h1>Booking Confirmed</h1>
<p>Hi {{ client_name }},</p>
<p>Your session with {{ trainer_name }} is confirmed for:</p>
<p><strong>{{ date }} at {{ time }}</strong></p>
<p>Duration: {{ duration }} minutes</p>
```
```

**Step 7.3: SMS Service (15 min)**
```
FILE 9 → Section: "Step 7.3: SMS Service"
File path: apps/notifications/sms_service.py

IMPLEMENT:
1. SMSService class using Twilio
   - __init__: Setup Twilio Client
   - send_booking_reminder(phone_number, booking)
   - send_confirmation(phone_number, booking)

MESSAGE FORMAT:
- Keep under 160 characters for single SMS
- Include date, time, trainer name
- Use professional language

EXAMPLE:
"Your session with {trainer} is {date} at {time}. Reply CONFIRM to confirm."
```

**Step 7.4: Celery Tasks (30 min)**
```
FILE 9 → Section: "Step 7.4: Celery Tasks"
File path: apps/notifications/tasks.py

IMPLEMENT:
1. @shared_task send_booking_confirmation(booking_id)
   - Get booking from database
   - Call email_service.send_booking_confirmation()
   - Call sms_service.send_confirmation() if phone
   - Create Notification records
   - Log any errors

2. @shared_task send_booking_reminders()
   - Query bookings for tomorrow
   - Send email & SMS reminders
   - Create Notification records
   - This runs daily (scheduled via Celery Beat)

3. @shared_task send_hour_reminders()
   - Query bookings in next hour
   - Send SMS reminder
   - This runs every 30 minutes (scheduled via Celery Beat)

CELERY CONFIGURATION (config/celery.py):
```python
app.conf.beat_schedule = {
    'send-24h-reminders': {
        'task': 'apps.notifications.tasks.send_booking_reminders',
        'schedule': crontab(hour=10, minute=0),  # Daily at 10 AM
    },
    'send-1h-reminders': {
        'task': 'apps.notifications.tasks.send_hour_reminders',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}
```

HOW TO RUN CELERY:
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A config worker -l info

# Terminal 3: Start Celery beat (scheduler)
celery -A config beat -l info

# Terminal 4: Start Django
python manage.py runserver
```
```

**Step 7.5: Admin Interface (5 min)**
```
FILE 9 → Section: "Step 7.5: Admin Interface"
File path: apps/notifications/admin.py

IMPLEMENT:
1. Register Notification model
   - list_display: ('trainer', 'notification_type', 'recipient', 'status', 'sent_at')
   - list_filter: ('status', 'notification_type', 'created_at')
   - readonly_fields: ('created_at', 'sent_at')
```

**SENDGRID SETUP:**
```
1. Sign up at sendgrid.com
2. Create API key
3. Add to .env: SENDGRID_API_KEY=...
4. Create email templates
5. Verify domain/sender email
```

**TWILIO SETUP:**
```
1. Sign up at twilio.com
2. Create account
3. Get Account SID, Auth Token, Phone Number
4. Add to .env:
   TWILIO_ACCOUNT_SID=...
   TWILIO_AUTH_TOKEN=...
   TWILIO_PHONE_NUMBER=...
```

**EPIC 7 COMPLETION CHECKLIST:**
- [ ] Notification model created and migrated
- [ ] EmailService working (test with SendGrid API key)
- [ ] SMSService working (test with Twilio API key)
- [ ] Email templates created
- [ ] Celery tasks defined
- [ ] Celery Beat schedule configured
- [ ] Notifications created on booking confirmation
- [ ] 24h reminders sending
- [ ] 1h reminders sending
- [ ] Notification logs in admin
- [ ] Admin interface configured

---

#### 📊 EPIC 8: ANALYTICS & DASHBOARD (1.5 hours) - FILE 9

**What you're building:**
- Analytics data models
- Dashboard metrics
- Revenue reports
- Booking and client statistics

**Implementation steps from FILE 9:**

**Step 8.1: Analytics Models (15 min)**
```
FILE 9 → Section: "Step 8.1: Analytics Models"
File path: apps/analytics/models.py

IMPLEMENT:
1. DashboardMetrics model
   - trainer (ForeignKey)
   - date (DateField, db_index)
   - bookings_count (IntegerField)
   - completed_bookings (IntegerField)
   - cancelled_bookings (IntegerField)
   - revenue (DecimalField)
   - new_clients (IntegerField)
   - active_clients (IntegerField)
   - average_session_rating (DecimalField)
   - created_at (auto_now_add)

Meta:
   - unique_together: ['trainer', 'date']
   - Proper indexes for performance

MIGRATION:
- python manage.py makemigrations
- python manage.py migrate
```

**Step 8.2: Analytics Serializers (10 min)**
```
FILE 9 → Section: "Step 8.2: Analytics Serializers"
File path: apps/analytics/serializers.py

IMPLEMENT:
1. DashboardMetricsSerializer
   - All fields
   - read_only: id, created_at
```

**Step 8.3: Analytics Views (45 min)**
```
FILE 9 → Section: "Step 8.3: Analytics Views"
File path: apps/analytics/views.py

IMPLEMENT:
1. AnalyticsViewSet (ReadOnly)
   - get_queryset: filter by trainer

2. @action GET /analytics/dashboard/
   RETURNS: High-level metrics
   {
     "total_bookings": 150,
     "completed_bookings": 140,
     "upcoming_bookings": 5,
     "total_clients": 45,
     "new_clients": 3,
     "total_revenue": 15000.00,
     "monthly_revenue": 2500.00,
     "average_booking_value": 100.00
   }

   LOGIC:
   - total_bookings: Booking.objects.filter(trainer=trainer).count()
   - completed_bookings: filter(status='completed').count()
   - upcoming_bookings: filter(status__in=['pending','confirmed'], start_time__gte=now).count()
   - total_clients: Client.objects.filter(trainer=trainer).count()
   - new_clients: filter(created_at__gte=this_month).count()
   - total_revenue: Payment.objects.filter(subscription__trainer=trainer).aggregate(Sum('amount'))
   - monthly_revenue: filter(created_at__gte=this_month).aggregate(Sum('amount'))

3. @action GET /analytics/revenue/
   PARAMS: period (week, month, year)
   RETURNS:
   {
     "period": "month",
     "total_revenue": 5000.00,
     "payment_count": 20,
     "average_payment": 250.00,
     "start_date": "2024-12-01",
     "end_date": "2025-01-01"
   }

4. @action GET /analytics/bookings-stats/
   RETURNS:
   {
     "total": 150,
     "by_status": {
       "pending": 5,
       "confirmed": 10,
       "completed": 130,
       "cancelled": 5
     },
     "completion_rate": 86.7,
     "cancellation_rate": 3.3
   }

5. @action GET /analytics/client-stats/
   RETURNS:
   {
     "total_clients": 45,
     "active_clients": 40,
     "inactive_clients": 5,
     "by_fitness_level": {
       "beginner": 20,
       "intermediate": 15,
       "advanced": 8,
       "athlete": 2
     }
   }

TESTING:
# Get dashboard
curl -X GET http://localhost:8000/api/analytics/dashboard/ \
  -H "Authorization: Token $TOKEN"

# Get revenue by month
curl -X GET "http://localhost:8000/api/analytics/revenue/?period=month" \
  -H "Authorization: Token $TOKEN"
```

**Step 8.4: Admin Interface (10 min)**
```
FILE 9 → Section: "Step 8.4: Admin Interface"
File path: apps/analytics/admin.py

IMPLEMENT:
1. Register DashboardMetrics
   - list_display: ('trainer', 'date', 'bookings_count', 'revenue', 'new_clients')
   - list_filter: ('date', 'trainer')
   - readonly_fields: ('created_at',)
```

**EPIC 8 COMPLETION CHECKLIST:**
- [ ] DashboardMetrics model created and migrated
- [ ] All serializers working
- [ ] Dashboard endpoint working
- [ ] Revenue endpoint working
- [ ] Booking stats endpoint working
- [ ] Client stats endpoint working
- [ ] All calculations accurate
- [ ] Admin interface configured
- [ ] All curl examples passing

---

### PHASE 4: INTEGRATION & TESTING (1 hour)

**Duration:** 1 hour
**Goal:** Ensure all EPICs work together

#### Step 4.1: End-to-End Flow Testing
```
TEST COMPLETE BOOKING FLOW:

1. Trainer registers
   POST /api/users/register/ → Get trainer account

2. Trainer logs in
   POST /api/users/login/ → Get token

3. Trainer adds availability
   POST /api/availability-slots/ → Add Monday 9AM-5PM

4. Trainer adds break
   POST /api/trainer-breaks/ → Add vacation Jan 15-20

5. Trainer creates package
   POST /api/packages/ → Create 5-Pack

6. Client registers
   POST /api/users/register/ (as client)

7. Trainer adds client
   POST /api/clients/ → Add client

8. Trainer assigns package
   POST /api/packages/1/assign_to_client/ → Client gets 5 sessions

9. Book session
   POST /api/bookings/ → Create booking for Jan 10, 10AM-11AM

10. Check availability
   GET /api/availability-slots/available/?date=2025-01-10
   → Should show available slots

11. Confirm booking
   POST /api/bookings/1/confirm/ → Changes status to confirmed

12. Verify notification sent
   GET /api/notifications/ → Check booking confirmation sent

13. Use session
   POST /api/client-packages/1/use_session/ → Decrement to 4

14. Check dashboard
   GET /api/analytics/dashboard/ → Should show 1 booking, revenue, etc.

15. Cancel booking
   POST /api/bookings/1/cancel/ → Changes status to cancelled

EXPECTED RESULTS:
- All endpoints return 200/201
- Conflicts prevent double-booking
- Sessions decrement correctly
- Analytics update automatically
```

#### Step 4.2: Create Test Suite
```bash
# Create tests directory
mkdir -p tests

# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific test
pytest tests/test_epic1.py::UserRegistrationTest
```

#### Step 4.3: Verify All URLs
```bash
# Check all URLs working
python manage.py runserver
# Visit http://localhost:8000/api/
# Should see browsable API with all endpoints
```

---

### PHASE 5: DEPLOYMENT CONFIGURATION (2 hours)

**Duration:** 2 hours
**Goal:** Prepare for production deployment

#### Step 5.1: Create Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### Step 5.2: Create Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: trainerhub_db
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/trainerhub_db
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A config worker -l info
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/trainerhub_db
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

#### Step 5.3: Deployment Commands
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Check logs
docker-compose logs -f web

# Stop services
docker-compose down
```

---

## 🎯 CHECKLIST FOR AI AGENT

### Before Starting Implementation
- [ ] Read all 15 files
- [ ] Understand problem statement
- [ ] Understand architecture and database schema
- [ ] Know all 50+ API endpoints
- [ ] Understand tech stack choices
- [ ] Setup development environment

### During Implementation
- [ ] Follow EPIC order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8
- [ ] Within each EPIC, follow step order
- [ ] Copy code EXACTLY from FILES 7-9
- [ ] Run migrations after each model
- [ ] Test endpoints with curl examples
- [ ] Verify admin interfaces work
- [ ] Check error handling
- [ ] Validate input/output

### Testing After Each Step
- [ ] Models migrate without errors
- [ ] Serializers validate correctly
- [ ] Endpoints return correct responses
- [ ] Error cases handled properly
- [ ] Admin interface accessible
- [ ] Relationships work correctly

### Before Deployment
- [ ] All 8 EPICs complete
- [ ] All tests passing
- [ ] Docker files created
- [ ] Environment variables set
- [ ] Database migrations tested
- [ ] All endpoints tested
- [ ] Admin interface working
- [ ] Third-party services configured

---

## 📞 TROUBLESHOOTING GUIDE

### Migration Errors
```bash
# If you get migration conflicts
python manage.py migrate --fake-initial

# If you need to reset migrations
python manage.py migrate apps.users zero
# Then delete migration files and recreate
```

### Database Connection Error
```bash
# Check PostgreSQL running
psql -U postgres -d trainerhub_db
# If fails, start PostgreSQL:
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### Celery Tasks Not Working
```bash
# Check Redis running
redis-cli ping
# Should return: PONG

# Start Celery in debug
celery -A config worker -l debug

# Check task in Redis CLI
redis-cli
KEYS *
```

### Endpoint 404
```bash
# Check URLs are included in config/urls.py
# Check router registration in app urls.py
# Verify app is in INSTALLED_APPS in settings.py
```

### Permission Denied
```bash
# Check IsAuthenticated permission is set
# Verify token is being passed:
# curl -H "Authorization: Token YOUR_TOKEN" ...

# Check user is trainer/client
# Check trainer profile exists
```

---

## ✅ FINAL CHECKLIST

### All Code Complete
- [ ] EPIC 1: Authentication ✅
- [ ] EPIC 2: Availability ✅
- [ ] EPIC 3: Clients ✅
- [ ] EPIC 4: Bookings ✅
- [ ] EPIC 5: Packages ✅
- [ ] EPIC 6: Payments ✅
- [ ] EPIC 7: Notifications ✅
- [ ] EPIC 8: Analytics ✅

### All Tests Passing
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All API tests pass
- [ ] Coverage > 80%

### All Features Working
- [ ] User registration/login
- [ ] Availability management
- [ ] Client management
- [ ] Booking system
- [ ] Package management
- [ ] Payment processing
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Analytics dashboard

### Deployment Ready
- [ ] Docker files created
- [ ] Environment configured
- [ ] Database migrations tested
- [ ] All endpoints tested
- [ ] Admin interface working
- [ ] Production checklist complete

---

## 🚀 NEXT STEPS FOR AI AGENT

1. **Read FILES 1-6** thoroughly (30 minutes)
2. **Create project structure** (15 minutes)
3. **Implement EPIC 1-2** (3.5 hours)
4. **Implement EPIC 3-5** (4.5 hours)
5. **Implement EPIC 6-8** (5 hours)
6. **Test all endpoints** (1 hour)
7. **Create Docker files** (30 minutes)
8. **Verify everything works** (30 minutes)

**Total time: 14.5 hours**

---

## 💡 KEY REMINDERS

✅ **DO:**
- Read all files before starting
- Follow instructions exactly
- Copy code as written
- Test after each step
- Run migrations regularly
- Use curl to test endpoints
- Check admin interfaces
- Follow the EPIC order

❌ **DON'T:**
- Skip reading files
- Modify code logic
- Try to improve code
- Skip steps
- Test everything at end
- Use hardcoded values
- Forget migrations
- Mix EPIC implementation

---

**You have everything needed to complete this project successfully!**

**Start by reading FILE 1, then proceed step-by-step through FILES 7-9.**

**Good luck! 🚀**
