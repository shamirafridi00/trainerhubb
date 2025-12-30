# TrainerHub Monitoring & Logging

## Overview

TrainerHub uses a comprehensive monitoring and logging strategy to ensure reliability and quick issue resolution.

## Components

1. **Sentry** - Error tracking and performance monitoring
2. **Application Logging** - Structured logging to files and console
3. **Health Checks** - Endpoints for monitoring service status
4. **Metrics** - Basic application metrics

## Sentry Setup

### Installation

```bash
pip install sentry-sdk
```

### Configuration

Set environment variables:

```bash
export SENTRY_DSN="https://your-dsn@sentry.io/project-id"
export SENTRY_ENVIRONMENT="production"  # or development, staging
export SENTRY_TRACES_SAMPLE_RATE="0.1"  # 10% of transactions
```

### Features

- **Error Tracking**: Automatic capture of exceptions
- **Performance Monitoring**: Transaction and span tracking
- **Breadcrumbs**: Context leading up to errors
- **Release Tracking**: Track errors by deployment version
- **User Context**: Associate errors with users (without PII)

### Usage in Code

```python
import sentry_sdk

# Capture custom exception
try:
    risky_operation()
except Exception as e:
    sentry_sdk.capture_exception(e)

# Add context
sentry_sdk.set_context("trainer", {
    "id": trainer.id,
    "business_name": trainer.business_name
})

# Add breadcrumb
sentry_sdk.add_breadcrumb(
    category='auth',
    message='User logged in',
    level='info'
)

# Track performance
with sentry_sdk.start_transaction(op="task", name="process_payment"):
    process_payment()
```

## Application Logging

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical issues requiring immediate attention

### Log Files

Located in `/logs/` directory:

- `trainerhubb.log` - General application logs
- `errors.log` - Error-level logs only (production)
- `debug.log` - Debug-level logs (development)
- `workflows.log` - Workflow execution logs
- `api.log` - API request/response logs (JSON format)

### Log Rotation

Logs are automatically rotated:
- Max file size: 10MB (5MB for workflows)
- Backup count: 5 files (3 for debug)
- Old logs are automatically archived

### Usage in Code

```python
import logging

logger = logging.getLogger(__name__)

# Basic logging
logger.info("User logged in: %s", user.email)
logger.warning("Payment method not configured for trainer: %s", trainer.id)
logger.error("Failed to send email: %s", error_message)

# With extra context
logger.info("Booking created", extra={
    'trainer_id': trainer.id,
    'client_id': client.id,
    'booking_id': booking.id
})

# Exception logging
try:
    process_booking()
except Exception as e:
    logger.exception("Failed to process booking")
```

### Logging Best Practices

1. **Use appropriate levels**: DEBUG for development, INFO for production events
2. **Include context**: Add relevant IDs and data
3. **Avoid logging sensitive data**: No passwords, tokens, or PII
4. **Use structured logging**: JSON format for API logs
5. **Log user actions**: Track important user events
6. **Log errors with stack traces**: Use `logger.exception()`

## Health Checks

### Endpoints

#### 1. Health Check (`/health/`)

Basic service availability check.

```bash
curl http://localhost:8000/health/
```

Response:
```json
{
  "status": "healthy",
  "service": "TrainerHub API",
  "timestamp": 1640000000.0
}
```

Use for: Load balancer health checks, basic monitoring

#### 2. Readiness Check (`/ready/`)

Comprehensive check of all dependencies.

```bash
curl http://localhost:8000/ready/
```

Response:
```json
{
  "status": "ready",
  "checks": {
    "database": {"status": "healthy", "message": "Connected"},
    "cache": {"status": "healthy", "message": "Connected"},
    "email": {"status": "configured", "message": "SendGrid API key present"},
    "sms": {"status": "configured", "message": "Twilio credentials present"}
  },
  "timestamp": 1640000000.0
}
```

Use for: Kubernetes readiness probes, deployment verification

#### 3. Liveness Check (`/live/`)

Simple check that process is running.

```bash
curl http://localhost:8000/live/
```

Response:
```json
{
  "status": "alive",
  "timestamp": 1640000000.0
}
```

Use for: Kubernetes liveness probes, process monitoring

#### 4. Metrics (`/metrics/`)

Basic application metrics.

```bash
curl http://localhost:8000/metrics/
```

Response:
```json
{
  "users": {
    "total": 150,
    "trainers": 45
  },
  "bookings": {
    "total": 1250,
    "today": 12
  },
  "clients": {
    "total": 320
  },
  "timestamp": 1640000000.0
}
```

Use for: Monitoring dashboards, alerting

## Monitoring Setup

### Kubernetes/Docker

```yaml
# Liveness probe
livenessProbe:
  httpGet:
    path: /live/
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

# Readiness probe
readinessProbe:
  httpGet:
    path: /ready/
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Uptime Monitoring

Use services like:
- **Uptime Robot**: https://uptimerobot.com
- **Pingdom**: https://www.pingdom.com
- **StatusCake**: https://www.statuscake.com

Monitor:
- Main application: `https://trainerhubb.app/health/`
- API endpoint: `https://trainerhubb.app/api/users/me/` (authenticated)

### Alerting

Set up alerts for:

1. **Error Rate**: > 1% of requests fail
2. **Response Time**: p95 > 2 seconds
3. **Health Checks**: `/health/` returns non-200
4. **Database**: Connection failures
5. **Cache**: Redis connection issues
6. **Disk Space**: < 20% free
7. **Memory**: > 80% usage
8. **CPU**: > 80% usage sustained

### Alert Channels

- **Email**: devops@trainerhubb.app
- **Slack**: #alerts channel
- **PagerDuty**: For critical issues (production only)
- **Sentry**: Automatic issue notifications

## Performance Monitoring

### Database Query Monitoring

Enable query logging in development:

```python
# settings.py
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

Monitor for:
- Slow queries (> 100ms)
- N+1 query problems
- Missing indexes
- Full table scans

### API Performance

Track in Sentry:
- Endpoint response times
- Slowest endpoints
- Error rates by endpoint
- Database query counts per request

### Caching Effectiveness

Monitor:
- Cache hit rate
- Cache miss rate
- Cache size
- Eviction rate

## Production Checklist

Before deploying to production:

- [ ] Sentry DSN configured
- [ ] Logging configured with rotation
- [ ] Health check endpoints responding
- [ ] Uptime monitoring configured
- [ ] Alerts configured
- [ ] Log aggregation set up (optional)
- [ ] Performance monitoring enabled
- [ ] Error notification channels configured
- [ ] Backup monitoring in place
- [ ] Database performance monitoring

## Troubleshooting

### High Error Rate

1. Check Sentry dashboard for common errors
2. Review `/logs/errors.log`
3. Check health check endpoints
4. Verify database/cache connectivity
5. Review recent deployments

### Performance Issues

1. Check Sentry performance dashboard
2. Enable database query logging
3. Review API logs for slow endpoints
4. Check cache hit rates
5. Monitor server resources (CPU, memory)

### Service Unavailable

1. Check `/health/` endpoint
2. Review `/logs/errors.log`
3. Verify database connection
4. Check Redis connection
5. Verify external service status (SendGrid, Twilio)

## Maintenance

### Log Management

```bash
# View recent logs
tail -f logs/trainerhubb.log

# Search for errors
grep ERROR logs/trainerhubb.log

# View specific time range
grep "2024-01-15 10:" logs/trainerhubb.log
```

### Log Cleanup

Logs are automatically rotated, but you can manually clean old logs:

```bash
# Remove logs older than 30 days
find logs/ -name "*.log.*" -mtime +30 -delete
```

### Sentry Maintenance

- Review and close resolved issues regularly
- Update issue priorities
- Assign ownership for recurring issues
- Archive old projects/releases

## Best Practices

1. **Monitor proactively**: Don't wait for users to report issues
2. **Set up alerts**: Get notified of problems immediately
3. **Review logs regularly**: Look for patterns and recurring issues
4. **Track metrics**: Monitor trends over time
5. **Test monitoring**: Verify alerts fire correctly
6. **Document incidents**: Keep a log of issues and resolutions
7. **Regular reviews**: Weekly review of errors and performance
8. **Capacity planning**: Monitor resource usage trends

## Support

For monitoring and logging support:
- Email: devops@trainerhubb.app
- Slack: #devops channel
- Sentry: https://sentry.io/organizations/trainerhubb
- Documentation: https://docs.trainerhubb.app/monitoring

