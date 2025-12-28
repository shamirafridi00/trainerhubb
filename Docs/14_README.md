# TrainerHub - Fitness Professional Booking Platform

Complete production-ready SaaS booking system built with Django, PostgreSQL, and Paddle payments in 14.5 hours.

## 🎯 Overview

**TrainerHub** is a modern SaaS platform that solves a critical problem for fitness professionals:

**The Problem:**
- Fitness trainers manually manage bookings (calls, emails, spreadsheets)
- No automated payment processing or client management
- Difficulty scaling their business
- Missing insights into revenue and client metrics

**The Solution:**
- Automated booking system with real-time availability
- Integrated payment processing (Paddle)
- Complete client management with notes & history
- Session packages and credit tracking
- Automated email/SMS notifications
- Revenue analytics and performance metrics

## 🚀 Features

### Core Features (EPIC 1-5)
- ✅ Email-based user authentication with token API
- ✅ Trainer availability management (recurring weekly slots)
- ✅ Client management with fitness profiles
- ✅ Booking system with conflict detection
- ✅ Session packages with credit tracking

### Advanced Features (EPIC 6-8)
- ✅ Paddle payment processing with webhooks
- ✅ SendGrid email automation
- ✅ Twilio SMS notifications
- ✅ Celery background task processing
- ✅ Revenue analytics & dashboard
- ✅ Booking metrics & client insights

## 📊 Tech Stack

**Backend:** Django 5 + Django REST Framework
**Database:** PostgreSQL + Redis
**Payments:** Paddle (SaaS billing)
**Email:** SendGrid
**SMS:** Twilio
**Tasks:** Celery + Redis
**Hosting:** Docker + Cloud (AWS/GCP/Azure)
**Monitoring:** Sentry

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│   API (50+ Endpoints)           │
├─────────────────────────────────┤
│   Django Models (12 Tables)     │
├─────────────────────────────────┤
│   PostgreSQL Database            │
├─────────────────────────────────┤
│   Background Services            │
│   (Celery, Email, SMS, Payments) │
└─────────────────────────────────┘
```

## 📋 Database Schema

**12 Core Tables:**
1. User (Custom auth)/supabase
2. Trainer (Profile)
3. Client (Fitness info)
4. AvailabilitySlot (Weekly slots)
5. TrainerBreak (Vacation)
6. Booking (Session record)
7. SessionPackage (Pricing)
8. ClientPackage (Purchases)
9. Subscription (Paddle)
10. Payment (Transactions)
11. Notification (Email/SMS logs)
12. DashboardMetrics (Analytics)

## 🔐 API Endpoints (50+)

**Authentication (5 endpoints)**
- User registration
- Login/Logout
- Profile management
- Password reset

**Bookings (8 endpoints)**
- Create/Update/Delete bookings
- Confirm/Cancel/Complete
- Upcoming/Past views

**Clients (8 endpoints)**
- CRUD operations
- Add notes
- View bookings

**Availability (8 endpoints)**
- Set availability slots
- Manage breaks
- Get available times

**Payments (5 endpoints)**
- Create subscriptions
- View payments
- Paddle webhooks

**Packages (6 endpoints)**
- Create/Update packages
- Assign to clients
- Track usage

**Analytics (6 endpoints)**
- Dashboard metrics
- Revenue reports
- Booking stats
- Client insights

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis 6.0+
- pip/poetry

### Quick Setup

```bash
# Clone repository
git clone <repo>
cd trainerhub

# Create environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit `http://localhost:8000/admin` to access Django admin.

## 📚 Documentation

- **START_HERE.md** - Project orientation & learning path
- **QUICK_REFERENCE.md** - API endpoints & commands
- **TECH_STACK_REFERENCE.md** - Why each technology
- **DEV_CHECKLIST_EPIC1-2.md** - Authentication & availability code
- **DEV_CHECKLIST_EPIC3-5.md** - Clients, bookings, packages code
- **DEV_CHECKLIST_EPIC6-8.md** - Payments, notifications, analytics code

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific test
pytest apps/users/tests.py::UserTestCase::test_registration
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t trainerhub:latest .

# Run container
docker run -p 8000:8000 trainerhub:latest

# Using docker-compose
docker-compose up
```

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Total Code Lines** | 4,000+ |
| **API Endpoints** | 50+ |
| **Database Tables** | 12 |
| **Django Models** | 12 |
| **Test Scenarios** | 30+ |
| **Development Time** | 14.5 hours |
| **Setup Time** | 1 hour |

## 💰 Pricing Model

**SaaS Subscription Tiers:**
- Starter: $15/month (5 clients)
- Professional: $35/month (50 clients)
- Studio: $99/month (unlimited)

**Revenue Streams:**
- Subscription fees
- Payment processing (2.9% + $0.30)
- Premium features (future)

## 🎯 Success Metrics

- API latency: < 200ms
- Availability: 99.9%+
- Test coverage: > 80%
- User retention: 80%+
- NPS: > 50

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - see LICENSE.md

## 🙋 Support

- Issues: GitHub Issues
- Docs: /docs
- Email: support@trainerhub.com

## 📈 Roadmap

- [ ] Mobile app (React Native)
- [ ] Trainer reviews/ratings
- [ ] Advanced scheduling
- [ ] Group classes
- [ ] Integration marketplace
- [ ] White-label option

## 🎉 Credits

Built with Django, PostgreSQL, and modern Python best practices.

---

**Ready to scale your fitness business? Start with TrainerHub!** 💪
