# 🧪 TrainerHub API Endpoint Testing Guide

## Overview

This guide covers testing all API endpoints across Epics 1-8 of the TrainerHub project.

## Logging Configuration

### Enhanced Logging Setup

The logging configuration has been enhanced with:

- **Verbose Formatter**: Detailed log format with timestamp, module, process, and thread
- **File Handler**: Logs saved to `logs/trainerhub.log`
- **Console Handler**: Logs displayed in console
- **App-Specific Loggers**: Separate loggers for:
  - `apps.bookings`
  - `apps.payments`
  - `apps.notifications`
  - `apps.analytics`

### Log File Location

```
logs/trainerhub.log
```

### Log Format

```
INFO 2025-12-29 10:00:00,123 module 12345 67890 Message here
```

## Comprehensive Test Script

### File: `test_all_endpoints.py`

A comprehensive test script that tests all endpoints across all Epics.

### Usage

```bash
# Make sure server is running
python manage.py runserver

# In another terminal, run the test script
python test_all_endpoints.py
```

### What It Tests

#### Epic 1-2: User & Trainer Endpoints
- ✅ Get user profile
- ✅ Update user profile

#### Epic 2: Availability Endpoints
- ✅ Create availability slot
- ✅ List availability slots
- ✅ Get available slots

#### Epic 3: Client Management Endpoints
- ✅ List clients
- ✅ Get client details
- ✅ Add note to client
- ✅ Get client notes

#### Epic 4: Booking Endpoints
- ✅ List bookings
- ✅ Create booking
- ✅ Get booking details
- ✅ Confirm booking
- ✅ Get upcoming bookings
- ✅ Get past bookings

#### Epic 5: Session Package Endpoints
- ✅ Create package
- ✅ List packages
- ✅ Assign package to client
- ✅ List client packages

#### Epic 6: Payment Endpoints
- ✅ List subscriptions
- ✅ List payments

#### Epic 7: Notification Endpoints
- ✅ List notifications
- ✅ Get notification statistics
- ✅ Get recent notifications

#### Epic 8: Analytics Endpoints
- ✅ Get dashboard summary
- ✅ Get revenue analytics
- ✅ Get booking statistics
- ✅ Get client statistics
- ✅ Get metrics summary

## Manual Testing

### 1. Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "yourpassword"}'

# Save the token from response
export TOKEN="your_token_here"
```

### 2. Test Endpoints

#### Users
```bash
# Get profile
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/profile/

# Update profile
curl -X PATCH -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Updated"}' \
  http://localhost:8000/api/profile/
```

#### Availability
```bash
# List slots
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/availability-slots/

# Get available slots
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/availability-slots/available-slots/?trainer_id=1&start_date=2025-12-30&end_date=2026-01-06"
```

#### Clients
```bash
# List clients
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/clients/

# Get client details
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/clients/1/

# Add note
curl -X POST -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test note"}' \
  http://localhost:8000/api/clients/1/add-note/
```

#### Bookings
```bash
# List bookings
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/bookings/

# Create booking
curl -X POST -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client": 1,
    "start_time": "2025-12-30T10:00:00Z",
    "end_time": "2025-12-30T11:00:00Z"
  }' \
  http://localhost:8000/api/bookings/

# Confirm booking
curl -X POST -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/bookings/1/confirm/

# Get upcoming bookings
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/bookings/upcoming/
```

#### Packages
```bash
# List packages
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/packages/

# Create package
curl -X POST -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "5-Pack",
    "sessions_count": 5,
    "price": "99.99"
  }' \
  http://localhost:8000/api/packages/

# Assign to client
curl -X POST -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"client_id": 1}' \
  http://localhost:8000/api/packages/1/assign-to-client/
```

#### Payments
```bash
# List subscriptions
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/subscriptions/

# List payments
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/payments/
```

#### Notifications
```bash
# List notifications
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/notifications/

# Get stats
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/notifications/stats/

# Get recent
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/notifications/recent/
```

#### Analytics
```bash
# Dashboard summary
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/analytics/dashboard/

# Revenue analytics
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/analytics/revenue/?period=month

# Booking stats
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/analytics/bookings-stats/

# Client stats
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/analytics/client-stats/

# Metrics summary
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/analytics/metrics-summary/?start_date=2025-01-01&end_date=2025-01-31"
```

## Test Results

The test script provides:
- ✅ Total tests run
- ✅ Passed tests count
- ❌ Failed tests count
- ⚠️ Skipped tests count
- 📊 Success rate percentage

## Logging

All API requests and responses are logged to:
- **Console**: Real-time output
- **File**: `logs/trainerhub.log` (persistent)

## Notes

- Make sure the Django server is running before testing
- Ensure you have test data (user, trainer, client) set up
- The test script creates test data automatically if needed
- Check logs for detailed error messages if tests fail

## Troubleshooting

### Authentication Failed
- Check if user exists
- Verify password is correct
- Check if user has trainer profile

### Endpoint Not Found (404)
- Verify server is running
- Check URL path is correct
- Ensure endpoint is registered in URLs

### Permission Denied (403)
- Check authentication token is valid
- Verify user has required permissions
- Check if trainer profile exists

### Server Error (500)
- Check server logs for details
- Verify database connection
- Check for missing migrations

