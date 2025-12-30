# TrainerHub Admin Panel Guide

## Overview

The Admin Panel provides super admin functionality for managing trainers, viewing platform statistics, and monitoring system activity.

## Authentication

Only users with `is_superuser=True` can access admin panel endpoints.

### Creating a Super Admin

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

---

## API Endpoints

Base URL: `/api/admin/`

### 1. Platform Statistics

**GET** `/api/admin/dashboard/stats/`

Returns platform-wide statistics including:
- Total trainers (active and inactive)
- Total clients
- Total bookings
- New signups this month
- Monthly revenue
- MRR (Monthly Recurring Revenue)
- Churn rate
- Subscription breakdown by plan

**Example Response:**
```json
{
  "total_trainers": 150,
  "active_trainers": 145,
  "total_clients": 1250,
  "total_bookings": 5000,
  "new_signups_this_month": 12,
  "total_revenue_this_month": "2100.00",
  "mrr": "4205.00",
  "churn_rate": 2.5,
  "subscription_breakdown": {
    "free": 50,
    "pro": 75,
    "business": 20
  }
}
```

---

### 2. Trainer Management

#### List All Trainers

**GET** `/api/admin/trainers/`

Query Parameters:
- `search` - Search by business name or email
- `is_active` - Filter by active status (true/false)
- `plan` - Filter by subscription plan (free/pro/business)
- `page` - Page number for pagination

**Example Response:**
```json
{
  "count": 150,
  "next": "http://api/admin/trainers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user_id": 5,
      "user_email": "trainer@example.com",
      "user_is_active": true,
      "business_name": "FitPro Training",
      "subscription_status": "active",
      "subscription_plan": "pro",
      "total_clients": 25,
      "total_bookings": 150,
      "total_pages": 1,
      "custom_domain": null,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Get Trainer Details

**GET** `/api/admin/trainers/{id}/`

Returns detailed information including recent clients, bookings, and payment history.

---

#### Suspend/Activate Trainer

**POST** `/api/admin/trainers/{id}/account_action/`

```json
{
  "action": "suspend",
  "reason": "Violation of terms of service"
}
```

Actions:
- `suspend` - Deactivate trainer account
- `activate` - Reactivate trainer account
- `verify` - Mark trainer as verified
- `delete` - Permanently delete trainer account

---

#### Impersonate Trainer

**POST** `/api/admin/trainers/{id}/impersonate/`

```json
{
  "reason": "Support request - investigating booking issue"
}
```

**Response:**
```json
{
  "token": "abc123def456...",
  "trainer_id": 1,
  "user_id": 5,
  "email": "trainer@example.com",
  "business_name": "FitPro Training",
  "message": "Impersonation active. Use this token to access trainer dashboard."
}
```

Use the returned token in Authorization header to access trainer's dashboard as them:
```
Authorization: Token abc123def456...
```

---

### 3. Action Logs

**GET** `/api/admin/logs/`

View audit trail of all admin actions.

Query Parameters:
- `admin_id` - Filter by admin user
- `trainer_id` - Filter by target trainer
- `action` - Filter by action type

**Example Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "admin_email": "admin@trainerhub.app",
      "action": "impersonate",
      "action_display": "Impersonate Trainer",
      "trainer_name": "FitPro Training",
      "details": {
        "reason": "Support request"
      },
      "ip_address": "192.168.1.1",
      "created_at": "2024-01-20T14:30:00Z"
    }
  ]
}
```

---

## Usage Examples

### Python/Requests

```python
import requests

# Login as super admin
response = requests.post('http://api/api/auth/login/', json={
    'email': 'admin@trainerhub.app',
    'password': 'your_password'
})
token = response.json()['token']

headers = {'Authorization': f'Token {token}'}

# Get platform stats
stats = requests.get('http://api/api/admin/dashboard/stats/', headers=headers)
print(stats.json())

# List trainers
trainers = requests.get('http://api/api/admin/trainers/?search=fitness', headers=headers)
print(trainers.json())

# Suspend a trainer
suspend = requests.post(
    'http://api/api/admin/trainers/5/account_action/',
    json={'action': 'suspend', 'reason': 'Payment fraud'},
    headers=headers
)
print(suspend.json())
```

### cURL

```bash
# Get stats
curl -H "Authorization: Token YOUR_TOKEN" \
  http://api/api/admin/dashboard/stats/

# Search trainers
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://api/api/admin/trainers/?search=john"

# Impersonate trainer
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Support debugging"}' \
  http://api/api/admin/trainers/5/impersonate/
```

---

## Security Considerations

1. **Audit Trail**: All admin actions are logged in the `AdminActionLog` model
2. **IP Tracking**: Admin actions record the IP address
3. **Impersonation**: Impersonation is logged with reason
4. **Superuser Only**: All endpoints require `is_superuser=True`
5. **Token Based**: Uses Django REST Framework token authentication

---

## Next Steps (Epic 0.2 - Epic 0.4)

- Domain management and verification system
- Platform analytics dashboard with charts
- Email notifications to admins on critical events
- Trainer account upgrade/downgrade functionality
- Bulk actions for trainers

---

## Troubleshooting

### "You must be a superuser to access this resource"

Make sure your user has `is_superuser=True`:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email='your@email.com')
user.is_superuser = True
user.is_staff = True
user.save()
```

### Can't see admin endpoints

Ensure `apps.admin_panel` is in `INSTALLED_APPS` and migrations are run:

```bash
python manage.py migrate admin_panel
```

