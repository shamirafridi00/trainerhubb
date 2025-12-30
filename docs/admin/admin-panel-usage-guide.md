# TrainerHub Admin Panel - Complete Usage Guide

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Accessing the Admin Panel](#accessing-the-admin-panel)
3. [Admin Panel Features](#admin-panel-features)
4. [Managing Users](#managing-users)
5. [Managing Trainers](#managing-trainers)
6. [Managing Clients](#managing-clients)
7. [Managing Bookings](#managing-bookings)
8. [Managing Payments](#managing-payments)
9. [Platform Settings](#platform-settings)
10. [Action Logs](#action-logs)
11. [Domain Management](#domain-management)
12. [API Endpoints](#api-endpoints)
13. [Tips & Best Practices](#tips--best-practices)

---

## 🚀 Getting Started

### Prerequisites

- Django development server running
- Superuser account created
- Access to the admin panel URL

### Creating a Superuser

If you don't have a superuser account yet:

```bash
cd /home/shamir/trainerhubb
source venv/bin/activate  # If using virtual environment
python manage.py createsuperuser
```

Follow the prompts:
- **Email**: admin@trainerhub.app (or your preferred email)
- **Username**: admin (or your preferred username)
- **Password**: [Enter a secure password]

---

## 🔐 Accessing the Admin Panel

### Web Interface (Django Admin)

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to: `http://localhost:8000/admin/`

3. Login with your superuser credentials

### API Endpoints

All API endpoints require authentication via Token:
- Base URL: `http://localhost:8000/api/admin/`
- Authentication: `Authorization: Token YOUR_TOKEN`

To get a token:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@trainerhub.app","password":"your_password"}'
```

---

## 🎯 Admin Panel Features

### Dashboard Overview

The admin panel provides:

1. **User Management** - Manage all platform users
2. **Trainer Management** - View and manage trainer accounts
3. **Client Management** - Manage client profiles
4. **Booking Management** - View and manage all bookings
5. **Payment Management** - Track subscriptions and payments
6. **Platform Settings** - Configure global settings
7. **Action Logs** - Audit trail of all admin actions
8. **Domain Management** - Manage custom domains
9. **Analytics Dashboard** - View platform statistics

---

## 👥 Managing Users

### Viewing Users

1. Navigate to **Users** → **Users** in the admin sidebar
2. View list of all users with:
   - Email address
   - Username
   - User type (Trainer/Client)
   - Active status
   - Verification status

### Filtering Users

Use the right sidebar filters:
- **Active Status**: Filter by active/inactive users
- **User Type**: Filter by trainer/client
- **Verification**: Filter by verified/unverified
- **Date Joined**: Filter by registration date

### Searching Users

Use the search box to find users by:
- Email address
- Username
- First name
- Last name

### Editing Users

1. Click on a user's email to open their profile
2. Edit fields as needed:
   - Personal information
   - Permissions (staff, superuser)
   - Active status
   - Verification status

### Common Actions

- **Deactivate User**: Uncheck "Active" and save
- **Make Staff**: Check "Staff status" and save
- **Make Superuser**: Check "Superuser status" and save

---

## 🏋️ Managing Trainers

### Viewing Trainers

1. Navigate to **Trainers** → **Trainers**
2. View list showing:
   - Business name
   - Associated user
   - Rating
   - Verification status
   - Registration date

### Trainer Details

Click on a trainer to view:
- Business information
- Bio and expertise
- Location and timezone
- Subscription status
- Related clients and bookings

### Trainer Actions

**Via Web Interface:**
- Edit trainer profile
- View related clients
- View booking history
- View payment history

**Via API:**
```bash
# Suspend trainer
curl -X POST http://localhost:8000/api/admin/trainers/{id}/account_action/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "suspend", "reason": "Terms violation"}'

# Impersonate trainer (for support)
curl -X POST http://localhost:8000/api/admin/trainers/{id}/impersonate/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Support request"}'
```

---

## 👤 Managing Clients

### Viewing Clients

1. Navigate to **Clients** → **Clients**
2. View list showing:
   - Full name
   - Email
   - Associated trainer
   - Fitness level
   - Active status

### Client Details

Click on a client to view:
- Personal information
- Contact details
- Fitness goals and preferences
- Notes (trainer's private notes)
- Booking history
- Package assignments

### Client Notes

- View all notes added by trainers
- Notes are private to the trainer
- Can be used for progress tracking

---

## 📅 Managing Bookings

### Viewing Bookings

1. Navigate to **Bookings** → **Bookings**
2. View list showing:
   - Client name
   - Trainer name
   - Start/end time
   - Status
   - Duration

### Filtering Bookings

Use filters to find:
- **Status**: Pending, Confirmed, Completed, Cancelled
- **Date**: Filter by start time
- **Trainer**: Filter by specific trainer
- **Date Hierarchy**: Navigate by year/month/day

### Booking Statuses

- **Pending**: Awaiting confirmation
- **Confirmed**: Confirmed by trainer
- **Completed**: Session completed
- **Cancelled**: Cancelled by trainer or client
- **No-Show**: Client didn't show up

### Editing Bookings

- Change status
- Update times
- Add notes
- Add cancellation reason

---

## 💳 Managing Payments

### Subscriptions

1. Navigate to **Payments** → **Subscriptions**
2. View all trainer subscriptions:
   - Trainer name
   - Paddle subscription ID
   - Status (Active/Paused/Cancelled)
   - Next billing date

### Payments

1. Navigate to **Payments** → **Payments**
2. View payment history:
   - Trainer name
   - Amount and currency
   - Transaction ID
   - Status
   - Payment date

### Payment Statuses

- **Completed**: Payment successful
- **Pending**: Payment processing
- **Failed**: Payment failed
- **Refunded**: Payment refunded

---

## ⚙️ Platform Settings

### Viewing Settings

1. Navigate to **Admin Panel** → **Platform Settings**
2. View all global platform settings

### Adding/Editing Settings

1. Click "Add Platform Setting" or edit existing
2. Fields:
   - **Key**: Setting identifier (e.g., `maintenance_mode`)
   - **Value**: Setting value (JSON format)
   - **Description**: Human-readable description

### Common Settings

- `maintenance_mode`: Enable/disable maintenance mode
- `max_trainers`: Maximum number of trainers allowed
- `default_timezone`: Default timezone for new trainers
- `email_notifications_enabled`: Enable/disable email notifications

---

## 📝 Action Logs

### Viewing Logs

1. Navigate to **Admin Panel** → **Admin Action Logs**
2. View audit trail of all admin actions:
   - Action type (color-coded badges)
   - Admin user who performed action
   - Target trainer (if applicable)
   - Timestamp
   - IP address

### Log Details

Click on a log entry to view:
- Full action details
- Request information (IP, user agent)
- JSON details of the action

### Log Types

- **View Trainer**: Admin viewed trainer profile
- **Impersonate**: Admin impersonated trainer
- **Suspend**: Trainer account suspended
- **Activate**: Trainer account activated
- **Delete Trainer**: Trainer account deleted
- **Approve Domain**: Custom domain approved
- **Reject Domain**: Custom domain rejected

**Note**: Logs are immutable and cannot be deleted for audit compliance.

---

## 🌐 Domain Management

### Viewing Domains

1. Navigate to **Admin Panel** → **Custom Domains**
2. View all custom domain requests:
   - Domain name
   - Associated trainer
   - Status (color-coded badges)
   - DNS verification status
   - SSL certificate status

### Domain Statuses

- **Pending**: Awaiting DNS configuration
- **Verifying**: DNS verification in progress
- **Verified**: DNS verified, awaiting SSL
- **Active**: Domain live and active
- **Failed**: Verification failed
- **Rejected**: Admin rejected domain

### Domain Actions

**Via Web Interface:**
- View domain details
- Check verification status
- Approve/reject domains

**Via API:**
```bash
# Verify domain manually
curl -X POST http://localhost:8000/api/admin/domains/{id}/verify/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force": true}'

# Approve domain
curl -X POST http://localhost:8000/api/admin/domains/{id}/approve-reject/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'
```

---

## 📊 API Endpoints

### Platform Statistics

```bash
GET /api/admin/dashboard/stats/
```

Returns:
- Total trainers (active/inactive)
- Total clients
- Total bookings
- New signups this month
- Monthly revenue
- MRR (Monthly Recurring Revenue)
- Churn rate
- Subscription breakdown

### Analytics Dashboard

```bash
GET /api/admin/dashboard/analytics/?days=30&group_by=day
```

Returns comprehensive analytics:
- Revenue trends
- Signup trends
- Active users trends
- Geographic distribution
- Booking trends
- Client growth trends
- Top performing trainers

See [EPIC_0_4_COMPLETION_SUMMARY.md](./EPIC_0_4_COMPLETION_SUMMARY.md) for full analytics API documentation.

### Trainer Management

```bash
# List trainers
GET /api/admin/trainers/?search=keyword&is_active=true&plan=pro

# Get trainer details
GET /api/admin/trainers/{id}/

# Bulk actions
POST /api/admin/trainers/bulk-action/
{
  "action": "suspend",
  "trainer_ids": [1, 2, 3],
  "reason": "Terms violation"
}

# Export trainers
GET /api/admin/trainers/export/
```

See [ADMIN_PANEL_GUIDE.md](./ADMIN_PANEL_GUIDE.md) for full API documentation.

---

## 💡 Tips & Best Practices

### Security

1. **Never share superuser credentials**
   - Use individual admin accounts for each admin user
   - Enable 2FA if available

2. **Review action logs regularly**
   - Check for suspicious activity
   - Monitor impersonation usage

3. **Use API tokens securely**
   - Don't commit tokens to version control
   - Rotate tokens regularly

### Performance

1. **Use filters effectively**
   - Filter large lists before searching
   - Use date hierarchies for time-based queries

2. **Export large datasets**
   - Use CSV export for large lists
   - Don't load all records in browser

3. **Optimize queries**
   - Use select_related for foreign keys
   - Use prefetch_related for many-to-many

### Workflow

1. **Trainer Support**
   - Use impersonation for debugging
   - Always log reason for impersonation
   - Check action logs after support

2. **Account Management**
   - Suspend before deleting
   - Always provide reason for actions
   - Review before permanent deletion

3. **Domain Management**
   - Verify DNS before approving
   - Check SSL certificate expiry
   - Monitor verification logs

### Common Tasks

**Suspend a problematic trainer:**
1. Navigate to Trainers → Trainers
2. Find trainer by search
3. Click on trainer
4. Uncheck "Active" in user section
5. Save

**View trainer's booking history:**
1. Navigate to Trainers → Trainers
2. Click on trainer
3. Scroll to "Bookings" section
4. Click on booking count to see all bookings

**Export platform statistics:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/admin/dashboard/export-stats/ \
  -o platform_stats.csv
```

**Bulk verify trainers:**
```bash
curl -X POST http://localhost:8000/api/admin/trainers/bulk-action/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "verify",
    "trainer_ids": [1, 2, 3, 4, 5]
  }'
```

---

## 🆘 Troubleshooting

### Can't Access Admin Panel

**Problem**: Getting 403 Forbidden or redirected to login

**Solutions**:
1. Verify you're logged in as superuser
2. Check `is_superuser=True` in user profile
3. Clear browser cache and cookies
4. Try incognito/private browsing mode

### API Returns 403

**Problem**: API endpoints return 403 Forbidden

**Solutions**:
1. Verify token is valid
2. Check user has `is_superuser=True`
3. Verify token in Authorization header format: `Token YOUR_TOKEN`
4. Check token hasn't expired

### Can't See Certain Models

**Problem**: Some models don't appear in admin

**Solutions**:
1. Verify app is in `INSTALLED_APPS`
2. Check migrations are run: `python manage.py migrate`
3. Verify model is registered in admin.py
4. Check user has necessary permissions

### Action Logs Not Appearing

**Problem**: Actions not being logged

**Solutions**:
1. Verify `log_admin_action()` is called
2. Check AdminActionLog model exists
3. Verify migrations are up to date
4. Check database connection

---

## 📚 Additional Resources

- [Django Admin Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
- [ADMIN_PANEL_GUIDE.md](./ADMIN_PANEL_GUIDE.md) - API Reference
- [EPIC_0_4_COMPLETION_SUMMARY.md](./EPIC_0_4_COMPLETION_SUMMARY.md) - Analytics API
- [EPIC_0_1_COMPLETION_SUMMARY.md](./EPIC_0_1_COMPLETION_SUMMARY.md) - Admin Panel Overview

---

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review action logs for errors
3. Check Django logs: `logs/trainerhub.log`
4. Run test scripts to verify functionality

---

**Last Updated**: December 2024
**Version**: 1.0

