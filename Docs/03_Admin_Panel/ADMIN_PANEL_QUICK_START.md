# Admin Panel Quick Start Guide

## 🚀 Quick Access

### Web Interface
- **URL**: http://localhost:8000/admin/
- **Login**: Use your superuser credentials

### API Endpoints
- **Base URL**: http://localhost:8000/api/admin/
- **Auth**: Token authentication required

---

## 📋 Common Tasks

### 1. View Platform Statistics
```
GET /api/admin/dashboard/stats/
```

### 2. Search for a Trainer
**Web**: Navigate to Trainers → Trainers → Search box
**API**: `GET /api/admin/trainers/?search=keyword`

### 3. Suspend a Trainer
**Web**: Trainers → Select trainer → Uncheck "Active" → Save
**API**: `POST /api/admin/trainers/{id}/account_action/` with `{"action": "suspend"}`

### 4. View Action Logs
**Web**: Admin Panel → Admin Action Logs
**API**: `GET /api/admin/logs/`

### 5. Export Trainers List
**API**: `GET /api/admin/trainers/export/`

### 6. View Analytics Dashboard
**API**: `GET /api/admin/dashboard/analytics/?days=30&group_by=day`

---

## 🎨 Visual Enhancements

The admin panel now includes:
- ✅ Color-coded status badges
- ✅ Clickable links between related models
- ✅ Better organized fieldsets
- ✅ Enhanced search and filtering
- ✅ Custom styling with gradient headers

---

## 📚 Full Documentation

For complete documentation, see:
- **[ADMIN_PANEL_USAGE_GUIDE.md](./ADMIN_PANEL_USAGE_GUIDE.md)** - Complete usage guide
- **[ADMIN_PANEL_GUIDE.md](./ADMIN_PANEL_GUIDE.md)** - API reference
- **[EPIC_0_4_COMPLETION_SUMMARY.md](./EPIC_0_4_COMPLETION_SUMMARY.md)** - Analytics API

---

## 🔑 Getting Started

1. **Create superuser** (if needed):
   ```bash
   python manage.py createsuperuser
   ```

2. **Start server**:
   ```bash
   python manage.py runserver
   ```

3. **Access admin**:
   - Web: http://localhost:8000/admin/
   - API: http://localhost:8000/api/admin/

4. **Get API token**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@trainerhub.app","password":"your_password"}'
   ```

---

**That's it! You're ready to use the admin panel.** 🎉

