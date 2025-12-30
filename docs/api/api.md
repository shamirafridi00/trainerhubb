# TrainerHub API Documentation

## Base URL

```
https://trainerhubb.app/api
```

## Authentication

Most endpoints require authentication using Token authentication.

```http
Authorization: Token {your-token}
```

### Get Token

```http
POST /api/users/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "token": "abc123...",
  "user": { ... },
  "trainer": { ... }
}
```

## Core Endpoints

### Users & Authentication

- `POST /api/users/register/` - Register new user
- `POST /api/users/login/` - Login and get token
- `POST /api/users/logout/` - Logout (invalidates token)
- `GET /api/users/me/` - Get current user info

### Trainers

- `GET /api/trainers/` - List all trainers
- `GET /api/trainers/{id}/` - Get trainer details
- `PATCH /api/trainers/{id}/` - Update trainer profile
- `GET /api/trainers/me/` - Get current trainer profile

### Clients

- `GET /api/clients/` - List trainer's clients
- `POST /api/clients/` - Add new client
- `GET /api/clients/{id}/` - Get client details
- `PATCH /api/clients/{id}/` - Update client
- `DELETE /api/clients/{id}/` - Delete client
- `GET /api/clients/{id}/payments/` - Get client payment history

### Bookings

- `GET /api/bookings/` - List trainer's bookings
- `POST /api/bookings/` - Create booking
- `GET /api/bookings/{id}/` - Get booking details
- `PATCH /api/bookings/{id}/` - Update booking
- `DELETE /api/bookings/{id}/` - Cancel booking
- `POST /api/bookings/{id}/confirm/` - Confirm booking
- `POST /api/bookings/{id}/complete/` - Mark booking as completed

### Packages

- `GET /api/packages/` - List trainer's packages
- `POST /api/packages/` - Create package
- `GET /api/packages/{id}/` - Get package details
- `PATCH /api/packages/{id}/` - Update package
- `DELETE /api/packages/{id}/` - Delete package

### Pages (Page Builder)

- `GET /api/pages/` - List trainer's pages
- `POST /api/pages/` - Create page
- `GET /api/pages/{id}/` - Get page details
- `PATCH /api/pages/{id}/` - Update page
- `DELETE /api/pages/{id}/` - Delete page
- `POST /api/pages/{id}/publish/` - Publish page
- `POST /api/pages/{id}/unpublish/` - Unpublish page
- `GET /api/pages/templates/` - List available templates

### Payments & Subscriptions

- `GET /api/subscriptions/` - Get current subscription
- `POST /api/subscriptions/upgrade/` - Upgrade subscription
- `POST /api/subscriptions/cancel/` - Cancel subscription
- `GET /api/payments/` - List payments
- `POST /api/payments/` - Record manual payment
- `GET /api/payments/revenue-summary/` - Get revenue summary
- `GET /api/payments/unpaid-clients/` - Get unpaid clients

### Workflows

- `GET /api/workflows/` - List workflows
- `POST /api/workflows/` - Create workflow
- `GET /api/workflows/{id}/` - Get workflow details
- `PATCH /api/workflows/{id}/` - Update workflow
- `DELETE /api/workflows/{id}/` - Delete workflow
- `POST /api/workflows/{id}/activate/` - Activate workflow
- `POST /api/workflows/{id}/deactivate/` - Deactivate workflow

### Email & SMS Templates

- `GET /api/workflows/email-templates/` - List email templates
- `POST /api/workflows/email-templates/` - Create email template
- `GET /api/workflows/sms-templates/` - List SMS templates
- `POST /api/workflows/sms-templates/` - Create SMS template

### White Label Settings

- `GET /api/trainers/whitelabel/` - Get white label settings
- `PUT /api/trainers/whitelabel/` - Update white label settings

### Analytics

- `GET /api/analytics/dashboard/` - Get dashboard statistics
- `GET /api/analytics/bookings-trend/` - Get booking trends
- `GET /api/analytics/revenue-trend/` - Get revenue trends

## Public API Endpoints

These endpoints don't require authentication and are used for public trainer pages.

### Public Pages

- `GET /api/public/{trainer_slug}/pages/` - List published pages
- `GET /api/public/{trainer_slug}/pages/{page_slug}/` - Get page content
- `GET /api/public/{trainer_slug}/profile/` - Get trainer profile
- `GET /api/public/{trainer_slug}/availability/` - Get availability
- `POST /api/public/{trainer_slug}/bookings/` - Create booking (public)
- `POST /api/public/{trainer_slug}/contact/` - Submit contact form

## Pagination

List endpoints support pagination:

```
GET /api/clients/?page=1&page_size=20
```

Response:
```json
{
  "count": 100,
  "next": "https://trainerhubb.app/api/clients/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtering & Search

Many endpoints support filtering:

```
GET /api/bookings/?status=confirmed&start_date=2024-01-01
GET /api/clients/?search=john
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message",
  "errors": {
    "field_name": ["Error for this field"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 429 Too Many Requests
```json
{
  "detail": "Request was throttled. Expected available in X seconds."
}
```

## Rate Limiting

- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Admin users: Unlimited

## Webhooks

### Paddle Webhook

```
POST /api/payments/paddle-webhook/
```

Handles Paddle subscription events.

## Usage Limits

Different subscription tiers have different limits:

| Resource | Free | Pro | Business |
|----------|------|-----|----------|
| Clients | 10 | 100 | Unlimited |
| Bookings/month | 50 | 500 | Unlimited |
| Pages | 1 | 5 | Unlimited |
| Workflows | 0 | 3 | Unlimited |
| Email/month | 100 | 1000 | Unlimited |
| SMS/month | 0 | 100 | 1000 |

## Best Practices

1. **Cache responses** where appropriate
2. **Use pagination** for large datasets
3. **Handle errors gracefully**
4. **Respect rate limits**
5. **Keep tokens secure**
6. **Use HTTPS** for all requests
7. **Validate input** on client side before sending

## SDKs & Libraries

Currently, TrainerHub provides a REST API. Consider creating client libraries for:
- JavaScript/TypeScript
- Python
- PHP
- Mobile (iOS/Android)

## Support

For API support:
- Email: api@trainerhubb.app
- Documentation: https://docs.trainerhubb.app
- Status: https://status.trainerhubb.app

