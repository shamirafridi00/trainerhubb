# TrainerHub - Fitness Professional Booking Platform

Complete SaaS booking system built with Django 5, PostgreSQL (Supabase), and modern Python stack.

## 🚀 Project Status

**Step 1.1 COMPLETED** ✅
- ✅ Supabase project created and configured
- ✅ Django project structure created
- ✅ All 9 apps initialized
- ✅ Custom User model implemented
- ✅ User authentication endpoints created
- ✅ Admin interface configured
- ⏳ Database migrations pending (network connectivity issue being resolved)

## 🛠️ Tech Stack

### Backend
- **Django 5.0.1** - Web framework
- **Django REST Framework 3.14.0** - API development
- **PostgreSQL (Supabase)** - Database with auth
- **Redis** - Caching and Celery broker
- **Celery 5.3.4** - Background task processing

### Third-Party Services
- **Supabase** - PostgreSQL database + authentication
- **SendGrid** - Email notifications
- **Twilio** - SMS notifications
- **Paddle** - Payment processing

## 📂 Project Structure

```
trainerhubb/
├── apps/
│   ├── users/          # User authentication & profiles
│   ├── trainers/       # Trainer profiles & business info
│   ├── availability/   # Availability slots & breaks
│   ├── clients/        # Client management
│   ├── bookings/       # Booking system
│   ├── packages/       # Session packages & pricing
│   ├── payments/       # Paddle payment integration
│   ├── notifications/  # Email & SMS notifications
│   └── analytics/      # Analytics & dashboard
├── config/             # Django settings & configuration
├── Docs/               # Project documentation
├── manage.py
├── requirements.txt
└── .env               # Environment variables (not in git)
```

## ⚙️ Setup Instructions

### 1. Clone and Setup Virtual Environment

```bash
cd /home/shamir/trainerhubb
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Edit `.env` file with your credentials:
- Supabase database connection
- SendGrid API key
- Twilio credentials
- Paddle API keys

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000/admin

## 🔐 API Endpoints

### Authentication
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `POST /api/users/logout/` - User logout
- `GET /api/users/me/` - Get current user profile
- `POST /api/users/change-password/` - Change password
- `PATCH /api/users/update-profile/` - Update profile

## 🗄️ Database Schema

### User Model (Custom)
- Email-based authentication
- Trainer/Client flags
- Supabase integration ready
- Phone number field
- Verification status

## 🚧 Current Issue

**Network Connectivity**: The system has IPv6-only connectivity issue with Supabase direct connection. 

**Solutions**:
1. ✅ Using Supabase Connection Pooler (recommended)
2. Configure IPv4/IPv6 dual stack
3. Use Supabase CLI for local development

## 📝 Next Steps

1. Resolve Supabase connection pooler authentication
2. Complete EPIC 1 testing
3. Implement EPIC 2: Trainer Availability
4. Implement remaining EPICs (3-8)
5. Setup Git and push to GitHub

## 🔗 Resources

- **Supabase Project**: https://supabase.com/dashboard/project/vonmkitsdzxecumgjbsd
- **GitHub Repo**: git@github.com:shamirafridi00/trainerhubb.git
- **Documentation**: See `Docs/` folder

## 👤 Developer

Shamir Afridi

