# Admin Panel Login Instructions

## Problem: Database Connection Failed

The error shows that Django cannot connect to the Supabase database:
```
psycopg2.OperationalError: could not translate host name "aws-1-us-west-1.pooler.supabase.com"
```

## Solutions

### Option 1: Fix Supabase Connection (Recommended)

1. **Check your `.env` file** has these variables:
   ```bash
   DB_NAME=your_database_name
   DB_USER=postgres
   DB_PASSWORD=your_supabase_password
   DB_HOST=aws-1-us-west-1.pooler.supabase.com
   DB_PORT=5432
   
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_PROJECT_ID=your_project_id
   ```

2. **Check Internet Connection**
   ```bash
   ping aws-1-us-west-1.pooler.supabase.com
   ```

3. **Verify Supabase Project is Running**
   - Go to https://supabase.com/dashboard
   - Check if your project is active

4. **Once connected, create superuser:**
   ```bash
   cd /home/shamir/trainerhubb
   source venv/bin/activate
   python create_superuser.py
   ```

---

### Option 2: Use Local SQLite (Quick Testing)

If you just want to test the admin panel quickly:

1. **Temporarily switch to SQLite** by modifying `config/settings.py`:

   ```python
   # Comment out the PostgreSQL config
   # DATABASES = {
   #     'default': {
   #         'ENGINE': 'django.db.backends.postgresql',
   #         ...
   #     }
   # }
   
   # Add SQLite config
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   # Email: admin@trainerhub.app
   # Username: admin
   # Password: admin123456
   ```

---

## Default Admin Credentials

Once the superuser is created:

```
📧 Email:    admin@trainerhub.app
🔑 Password: admin123456
```

**⚠️ IMPORTANT: Change this password after first login!**

---

## How to Login to Admin Panel

### Method 1: Using cURL

```bash
# Login and get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@trainerhub.app",
    "password": "admin123456"
  }'
```

**Response:**
```json
{
  "token": "abc123def456...",
  "user_id": 1,
  "email": "admin@trainerhub.app"
}
```

### Method 2: Using Python Test Script

```bash
python test_admin_panel.py
```

Enter credentials when prompted.

### Method 3: Using Postman/Thunder Client

1. **Request:** POST `http://localhost:8000/api/auth/login/`
2. **Headers:** `Content-Type: application/json`
3. **Body:**
   ```json
   {
     "email": "admin@trainerhub.app",
     "password": "admin123456"
   }
   ```
4. **Copy the token** from response
5. **Use token** for admin endpoints:
   ```
   Authorization: Token YOUR_TOKEN_HERE
   ```

---

## Admin Panel Endpoints

Once logged in, you can access:

```bash
# Get platform statistics
GET http://localhost:8000/api/admin/dashboard/stats/
Headers: Authorization: Token YOUR_TOKEN

# List all trainers
GET http://localhost:8000/api/admin/trainers/
Headers: Authorization: Token YOUR_TOKEN

# Get trainer details
GET http://localhost:8000/api/admin/trainers/1/
Headers: Authorization: Token YOUR_TOKEN

# View audit logs
GET http://localhost:8000/api/admin/logs/
Headers: Authorization: Token YOUR_TOKEN
```

---

## Troubleshooting

### "Authentication credentials were not provided"
- Add header: `Authorization: Token YOUR_TOKEN`

### "You must be a superuser to access this resource"
- Make sure user has `is_superuser=True`
- Run: `python create_superuser.py`

### "User does not exist"
- The database is empty
- Create superuser first (see above)

### Server not running
```bash
python manage.py runserver
```

---

## Quick Start Checklist

- [ ] Fix database connection (Supabase or SQLite)
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python create_superuser.py` or `python manage.py createsuperuser`
- [ ] Start server: `python manage.py runserver`
- [ ] Login via API: POST `/api/auth/login/`
- [ ] Use token to access admin endpoints

---

## Next Steps

Once logged in successfully:
1. Test platform stats endpoint
2. List trainers
3. Try impersonation feature
4. Review audit logs
5. Continue with Epic 0.2 (Domain Management)

