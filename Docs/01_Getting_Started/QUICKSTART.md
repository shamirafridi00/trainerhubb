# 🚀 TrainerHub - Quick Start Guide

## 🌐 Access Your Application

### 1. **Home Page** (API Root)
- **URL**: http://localhost:8000/
- **What you'll see**: Welcome message with all available endpoints
- **Status**: ✅ Working

### 2. **Django Admin Panel**
- **URL**: http://localhost:8000/admin/
- **Username**: `admin`
- **Password**: `admin123`
- **Status**: ✅ Working

### 3. **API Endpoints**
All API endpoints are available at:
- **Base URL**: http://localhost:8000/api/

## 🔐 Admin Panel Access

### Login Steps:
1. Open browser and go to: http://localhost:8000/admin/
2. Enter credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. Click "Log in"

### What you can do in Admin:
- View all registered users
- Manage user permissions
- Create/edit/delete users
- View authentication tokens
- Monitor system logs

## 🧪 Testing the API

### Option 1: Use the Test Script
```bash
cd /home/shamir/trainerhubb
bash test_api.sh
```

### Option 2: Manual Testing with curl

#### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trainer@example.com",
    "username": "trainer123",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

**Expected Response:**
```json
{
  "id": 3,
  "email": "trainer@example.com",
  "username": "trainer123",
  "first_name": "John",
  "last_name": "Doe",
  "token": "a1b2c3d4e5f6g7h8i9j0..."
}
```

#### 2. Login
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trainer@example.com",
    "password": "securepass123"
  }'
```

**Save the token from the response!**

#### 3. Get Your Profile
```bash
# Replace YOUR_TOKEN with the token from login response
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Token YOUR_TOKEN"
```

#### 4. Update Profile
```bash
curl -X PATCH http://localhost:8000/api/users/update-profile/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "phone_number": "+1234567890"
  }'
```

#### 5. Change Password
```bash
curl -X POST http://localhost:8000/api/users/change-password/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "securepass123",
    "new_password": "newpass456",
    "new_password_confirm": "newpass456"
  }'
```

#### 6. Logout
```bash
curl -X POST http://localhost:8000/api/users/logout/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Option 3: Use Browser

Visit http://localhost:8000/api/ in your browser to see the **Django REST Framework browsable API**.

You can test all endpoints directly from your browser!

## 📱 Using Postman

### Setup:
1. Create a new collection called "TrainerHub API"
2. Set base URL: `http://localhost:8000`
3. Create requests for each endpoint

### Authentication:
For authenticated endpoints, add header:
- **Key**: `Authorization`
- **Value**: `Token YOUR_TOKEN_HERE`

## 🗄️ Database Access (Supabase)

Your data is stored in Supabase PostgreSQL database:

- **Project URL**: https://supabase.com/dashboard/project/vonmkitsdzxecumgjbsd
- **Database**: PostgreSQL
- **Tables Created**:
  - `users_user` - Custom user model
  - `authtoken_token` - API tokens
  - Django default tables (auth, sessions, etc.)

### View Data in Supabase:
1. Go to your Supabase dashboard
2. Click "Table Editor"
3. Select `users_user` table
4. See all registered users

## 🔧 Troubleshooting

### Issue: Admin login not working
**Solution:**
```bash
cd /home/shamir/trainerhubb
bash test_admin.sh
```

### Issue: Server not running
**Solution:**
```bash
cd /home/shamir/trainerhubb
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Issue: Can't access from browser
**Solution:**
- Check if server is running: http://localhost:8000/
- Try 127.0.0.1:8000 instead
- Check firewall settings

### Issue: 404 on root URL
**Solution:** ✅ FIXED! The root URL now shows a welcome page.

## 📊 What's Working

- ✅ Root URL (/) - Welcome page
- ✅ Admin panel (/admin/)
- ✅ User registration
- ✅ User login
- ✅ User profile management
- ✅ Password change
- ✅ Token authentication
- ✅ Database connected (Supabase)
- ✅ All endpoints tested

## 🎯 Next Steps

Currently implemented:
- ✅ **EPIC 1**: User Authentication

Ready to implement:
- ⏳ **EPIC 2**: Trainer Availability
- ⏳ **EPIC 3**: Client Management
- ⏳ **EPIC 4**: Booking System
- ⏳ **EPIC 5**: Session Packages
- ⏳ **EPIC 6**: Payment Processing
- ⏳ **EPIC 7**: Notifications
- ⏳ **EPIC 8**: Analytics

## 🌟 Important URLs

- **API Root**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/
- **GitHub**: https://github.com/shamirafridi00/trainerhubb
- **Supabase**: https://supabase.com/dashboard/project/vonmkitsdzxecumgjbsd

## 💡 Pro Tips

1. **Keep the server running**: The Django server needs to be running in the background
2. **Save your tokens**: After login, save the token for authenticated requests
3. **Use the browsable API**: Visit /api/ in browser for easy testing
4. **Check Supabase**: Monitor your database in real-time
5. **Use test scripts**: Run `bash test_api.sh` for quick validation

## 🆘 Need Help?

- Check terminal output for errors
- Review Django logs
- Check Supabase logs
- Review this guide
- Ask for assistance!

---

**Happy Coding! 🚀**

