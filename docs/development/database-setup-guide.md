# Database Setup Guide

## Current Issue

Your TrainerHub project is configured for **Supabase PostgreSQL** but cannot connect.

Error: `could not translate host name "aws-1-us-west-1.pooler.supabase.com"`

## Choose Your Database Solution

### Option A: Fix Supabase Connection (Production-Ready)

**Steps:**

1. **Get Supabase Credentials:**
   - Go to https://supabase.com/dashboard
   - Select your project
   - Go to **Settings** → **Database**
   - Copy connection details

2. **Update `.env` file:**
   ```env
   # Database
   DB_NAME=postgres
   DB_USER=postgres.xxxxx
   DB_PASSWORD=your_password_here
   DB_HOST=aws-1-us-west-1.pooler.supabase.com
   DB_PORT=6543

   # Supabase
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_ANON_KEY=your_anon_key_here
   SUPABASE_PROJECT_ID=xxxxx
   ```

3. **Test connection:**
   ```bash
   python manage.py dbshell
   ```

4. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

---

### Option B: Use SQLite (Quick Testing)

For quick local testing without external database:

1. **Modify `config/settings.py`:**

   Find this section (around line 82):
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': config('DB_NAME'),
           'USER': config('DB_USER'),
           'PASSWORD': config('DB_PASSWORD'),
           'HOST': config('DB_HOST'),
           'PORT': config('DB_PORT', default='5432'),
           'CONN_MAX_AGE': 600,
           'OPTIONS': {
               'sslmode': 'require',
               'connect_timeout': 10,
           }
       }
   }
   ```

   Replace with:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

2. **Run migrations:**
   ```bash
   cd /home/shamir/trainerhubb
   source venv/bin/activate
   python manage.py migrate
   ```

3. **Create superuser:**
   ```bash
   python manage.py createsuperuser --email admin@trainerhub.app --username admin
   # Enter password when prompted: admin123456
   ```

---

### Option C: Use Local PostgreSQL

If you want PostgreSQL locally:

1. **Install PostgreSQL:**
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create database:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE trainerhub;
   CREATE USER trainerhub_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE trainerhub TO trainerhub_user;
   \q
   ```

3. **Update `.env`:**
   ```env
   DB_NAME=trainerhub
   DB_USER=trainerhub_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Update `config/settings.py` (remove SSL requirement):**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': config('DB_NAME'),
           'USER': config('DB_USER'),
           'PASSWORD': config('DB_PASSWORD'),
           'HOST': config('DB_HOST'),
           'PORT': config('DB_PORT', default='5432'),
           # Remove or comment out sslmode
       }
   }
   ```

---

## Recommendation

For **quick testing of admin panel**: Use **Option B (SQLite)**

For **production/deployment**: Use **Option A (Supabase)** or **Option C (Local PostgreSQL)**

---

## After Database Setup

Once database is working:

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Email: admin@trainerhub.app
# Username: admin  
# Password: admin123456

# Start server
python manage.py runserver

# Test login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@trainerhub.app","password":"admin123456"}'
```

---

## Verification

Server should show:
```
System check identified no issues (0 silenced).
December 29, 2024 - 12:00:00
Django version 5.x.x, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

You should be able to:
- ✅ Login and get token
- ✅ Access admin endpoints
- ✅ See platform statistics
- ✅ Manage trainers

