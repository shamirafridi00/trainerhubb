# Developer Setup Guide

This guide will help you set up TrainerHub for local development.

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for caching)
- Git

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourorg/trainerhubb.git
cd trainerhubb
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Database

```bash
# Create PostgreSQL database
createdb trainerhubb_dev

# Or using psql:
psql -U postgres
CREATE DATABASE trainerhubb_dev;
\q
```

### 4. Configure Environment Variables

Create `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-generate-new-one
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/trainerhubb_dev

# Or use Supabase:
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db.your-project.supabase.co
DB_PORT=5432

# Email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@trainerhubb.app

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Paddle (Payments)
PADDLE_VENDOR_ID=your-vendor-id
PADDLE_API_KEY=your-api-key
PADDLE_PUBLIC_KEY=your-public-key
PADDLE_WEBHOOK_SECRET=your-webhook-secret
PADDLE_ENVIRONMENT=sandbox  # or production

# Cloudinary (Media Storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
# Or use the script:
python create_superuser.py
```

### 7. Seed Initial Data (Optional)

```bash
# Seed page templates
python manage.py seed_templates

# Seed workflow templates (when implemented)
python manage.py seed_workflow_templates
```

### 8. Set Up Frontend

```bash
cd trainer-app
npm install
```

### 9. Start Development Servers

**Backend (Django):**
```bash
# From project root
python manage.py runserver
```

**Frontend (React):**
```bash
# From trainer-app directory
npm run dev
```

Frontend will be available at `http://localhost:3000`
Backend API at `http://localhost:8000`

## Project Structure

```
trainerhubb/
├── apps/                    # Django apps
│   ├── users/              # User authentication
│   ├── trainers/           # Trainer profiles
│   ├── clients/            # Client management
│   ├── bookings/           # Booking system
│   ├── packages/           # Training packages
│   ├── payments/           # Payments & subscriptions
│   ├── pages/              # Page builder
│   ├── workflows/          # Automation workflows
│   ├── notifications/      # Email/SMS
│   ├── analytics/          # Analytics & reports
│   ├── admin_panel/        # Super admin panel
│   └── frontend/           # HTMX frontend (legacy)
│
├── config/                  # Django configuration
│   ├── settings.py         # Settings
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI config
│
├── trainer-app/             # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── api/            # API client
│   │   ├── store/          # State management (Zustand)
│   │   ├── hooks/          # Custom hooks
│   │   └── types/          # TypeScript types
│   ├── public/             # Static assets
│   └── package.json        # Node dependencies
│
├── deployment/              # Deployment configs
│   ├── nginx/              # Nginx configuration
│   └── ssl/                # SSL setup scripts
│
├── docs/                    # Documentation
├── tests/                   # Integration tests
├── manage.py               # Django management
├── requirements.txt        # Python dependencies
└── README.md              # Project README
```

## Development Workflow

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests:
   ```bash
   # Backend tests
   python manage.py test
   
   # Frontend tests
   cd trainer-app && npm test
   ```

4. Check linting:
   ```bash
   # Python (if using black/flake8)
   black apps/
   flake8 apps/
   
   # TypeScript
   cd trainer-app && npm run lint
   ```

5. Commit changes:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. Push and create PR:
   ```bash
   git push origin feature/your-feature-name
   ```

### Running Tests

**Backend:**
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

**Frontend:**
```bash
cd trainer-app
npm test
```

### Database Migrations

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations

# Revert migration
python manage.py migrate app_name migration_name
```

### Creating New Apps

```bash
# Create Django app
python manage.py startapp app_name apps/app_name

# Add to INSTALLED_APPS in config/settings.py
```

### API Development

1. Create models in `models.py`
2. Create serializers in `serializers.py`
3. Create views in `views.py`
4. Add URL patterns in `urls.py`
5. Register with admin in `admin.py`
6. Write tests in `tests.py`

### Frontend Development

1. Create component in `src/components/`
2. Add types to `src/types/`
3. Create API client functions in `src/api/`
4. Add state management if needed in `src/store/`
5. Create page in `src/pages/`
6. Add route in `src/App.tsx`

## Debugging

### Django Debug Toolbar

Install Django Debug Toolbar for development:

```bash
pip install django-debug-toolbar
```

Add to `INSTALLED_APPS` and middleware in settings.py.

### React DevTools

Install React DevTools browser extension for debugging React components.

### Database Queries

View SQL queries in Django:

```python
from django.db import connection
print(connection.queries)
```

### API Testing

Use tools like:
- Postman
- Insomnia
- cURL
- HTTPie

### Logging

Configure logging in `config/settings.py`:

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

## Common Issues

### Port Already in Use

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Database Connection Errors

- Check PostgreSQL is running
- Verify database credentials in `.env`
- Ensure database exists

### Module Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or for frontend:
cd trainer-app && npm install
```

### Migration Conflicts

```bash
# Reset migrations (DANGEROUS - only in development)
python manage.py migrate app_name zero
rm apps/app_name/migrations/00*.py
python manage.py makemigrations
python manage.py migrate
```

## Code Style

### Python

- Follow PEP 8
- Use Black for formatting
- Use type hints where appropriate
- Write docstrings for functions/classes

### TypeScript/React

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Keep components small and focused

### Git Commits

Follow conventional commits:

```
feat: add new feature
fix: bug fix
docs: documentation
style: formatting
refactor: code restructuring
test: adding tests
chore: maintenance
```

## Useful Commands

```bash
# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Check for issues
python manage.py check

# Run server on different port
python manage.py runserver 8001

# Database shell
python manage.py dbshell

# Clear cache (if using Redis)
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Getting Help

- Check existing issues on GitHub
- Ask in development Slack channel
- Review pull request guidelines
- Contact lead developer

---

Happy coding! 🚀

