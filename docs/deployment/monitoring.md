# TrainerHub Monitoring & Logging Guide

This document outlines the monitoring, logging, and observability setup for the TrainerHub platform.

## Table of Contents

1. [Overview](#overview)
2. [Health Checks](#health-checks)
3. [Error Tracking](#error-tracking)
4. [Application Logging](#application-logging)
5. [Performance Monitoring](#performance-monitoring)
6. [Database Monitoring](#database-monitoring)
7. [Infrastructure Monitoring](#infrastructure-monitoring)
8. [Alerting](#alerting)
9. [Dashboards](#dashboards)
10. [Troubleshooting](#troubleshooting)

## Overview

The TrainerHub platform implements comprehensive monitoring across all layers:

- **Application Layer**: Health checks, error tracking, performance metrics
- **Database Layer**: Query performance, connection pooling, backups
- **Infrastructure Layer**: Server metrics, container health, resource usage
- **External Services**: Email, SMS, payment processor integrations

## Health Checks

### Endpoints

The application provides several health check endpoints:

#### `/health/` - Comprehensive Health Check

Returns JSON with system status and component health:

```json
{
  "status": "healthy",
  "timestamp": "2025-12-30T12:00:00Z",
  "version": "v1.0.0",
  "environment": "production",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "OK"
    },
    "redis": {
      "status": "healthy",
      "message": "OK"
    },
    "sendgrid": {
      "status": "configured",
      "message": "API key configured"
    }
  }
}
```

#### `/readiness/` - Kubernetes Readiness Check

Used by container orchestrators to determine if the application is ready to serve traffic.

#### `/liveness/` - Kubernetes Liveness Check

Basic check to ensure the application process is running.

#### `/api/system-info/` - System Information

Detailed system information for debugging (requires authentication in production):

```json
{
  "version": "v1.0.0",
  "environment": "production",
  "debug": false,
  "database_engine": "postgresql",
  "cache_backend": "redis",
  "installed_apps": ["apps.users", "apps.trainers", ...],
  "middleware": ["SecurityMiddleware", "CorsMiddleware", ...]
}
```

### Health Check Configuration

Health checks are configured in `apps/core/views.py` and include:

- **Database connectivity** - Tests PostgreSQL connection
- **Redis connectivity** - Tests cache connection
- **External services** - Checks API key configuration
- **Service dependencies** - Validates required services are available

### Load Balancer Integration

Configure your load balancer to use the `/health/` endpoint:

```nginx
# Nginx upstream health check
server {
    location /health/ {
        proxy_pass http://backend;
        proxy_connect_timeout 5s;
        proxy_read_timeout 5s;
    }
}
```

## Error Tracking

### Sentry Integration

Sentry is configured for comprehensive error tracking:

```python
# In production settings
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=config('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(),
        RedisIntegration(),
        CeleryIntegration(),
    ],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    environment=config('ENVIRONMENT', default='production'),
    release=config('RELEASE_VERSION', default=''),
)
```

### Frontend Error Tracking

React errors are also tracked via Sentry:

```javascript
// In trainer-app/src/main.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  integrations: [
    new Sentry.BrowserTracing(),
    new Sentry.Replay(),
  ],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

### Error Categories

Sentry captures different types of errors:

- **Application Errors**: Django exceptions, 500 errors
- **Database Errors**: Connection issues, query failures
- **External API Errors**: Payment processor, email service failures
- **Frontend Errors**: JavaScript exceptions, React errors
- **Background Task Errors**: Celery task failures

## Application Logging

### Log Configuration

Structured JSON logging is configured in `config/settings/logging.py`:

```python
LOGGING = {
    'formatters': {
        'json': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/trainerhub/django.log',
            'formatter': 'json',
        }
    }
}
```

### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General application flow
- **WARNING**: Warning conditions
- **ERROR**: Error conditions
- **CRITICAL**: Critical errors requiring immediate attention

### Log Categories

- **django**: Django framework logs
- **apps**: Application-specific logs
- **apps.bookings**: Booking-related operations
- **apps.payments**: Payment processing
- **apps.notifications**: Email/SMS notifications
- **apps.analytics**: Analytics and reporting

### Request Logging

The `RequestLoggingMiddleware` logs all HTTP requests:

```json
{
  "method": "POST",
  "path": "/api/bookings/",
  "status_code": 201,
  "duration_ms": 245.67,
  "user_agent": "Mozilla/5.0...",
  "remote_addr": "192.168.1.100",
  "user_id": 123,
  "trainer_id": 456
}
```

### Performance Logging

Slow requests and high resource usage are automatically logged:

```json
{
  "message": "Slow request",
  "path": "/api/bookings/",
  "method": "GET",
  "duration_ms": 8500.23,
  "db_queries": 45,
  "db_time": 3.45
}
```

## Performance Monitoring

### Application Performance Monitoring (APM)

Sentry provides APM features:

- **Transaction Tracing**: End-to-end request tracing
- **Performance Metrics**: Response times, throughput
- **Database Query Monitoring**: Slow queries, N+1 problems
- **Memory Usage**: Application memory consumption

### Custom Performance Metrics

Key performance indicators tracked:

- **Response Time**: P95, P99 response times
- **Throughput**: Requests per second
- **Error Rate**: Percentage of failed requests
- **Database Performance**: Query execution times
- **Cache Hit Rate**: Cache effectiveness

### React Performance Monitoring

Frontend performance is monitored via:

- **Core Web Vitals**: LCP, FID, CLS metrics
- **Bundle Analysis**: Bundle size, code splitting effectiveness
- **Runtime Performance**: React render times, memory usage

## Database Monitoring

### Query Performance

Database queries are monitored through:

- **Django Debug Toolbar** (development)
- **Sentry APM** (production)
- **PostgreSQL logs** (server level)

### Connection Pooling

Database connection pooling is configured:

```python
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'autocommit': True,
        }
    }
}
```

### Database Metrics

Monitor these database metrics:

- **Connection Count**: Active connections
- **Query Performance**: Slow queries (>100ms)
- **Table Sizes**: Database growth
- **Index Usage**: Index hit ratios
- **Lock Waits**: Database contention

## Infrastructure Monitoring

### Docker Container Monitoring

Monitor container health and resources:

```bash
# Container resource usage
docker stats

# Container logs
docker-compose -f docker-compose.prod.yml logs -f

# Container health
docker-compose -f docker-compose.prod.yml ps
```

### Server Monitoring

Monitor server-level metrics:

- **CPU Usage**: Application and system CPU
- **Memory Usage**: RAM consumption
- **Disk Usage**: Storage utilization
- **Network I/O**: Bandwidth usage
- **System Load**: Server load averages

### Redis Monitoring

Monitor Redis performance:

```bash
# Redis info
redis-cli info

# Key metrics to monitor:
# - connected_clients
# - used_memory
# - keyspace_hits/keyspace_misses
# - evicted_keys
```

## Alerting

### Alert Types

Configure alerts for:

#### Critical Alerts
- Application down (health check failures)
- Database connection failures
- High error rates (>5%)
- Certificate expiration (<30 days)

#### Warning Alerts
- High response times (>2 seconds)
- Low cache hit rates (<80%)
- High memory usage (>80%)
- Disk space low (<10% free)

#### Info Alerts
- Deployment completed
- Backup completed
- Certificate renewed

### Alert Channels

- **Email**: Critical alerts to development team
- **Slack**: Real-time notifications
- **PagerDuty**: On-call notifications for critical issues
- **Sentry**: Automatic error notifications

## Dashboards

### Grafana Dashboards

Create Grafana dashboards for:

#### Application Dashboard
- Request rate and response times
- Error rates by endpoint
- Database query performance
- Cache hit rates

#### Infrastructure Dashboard
- Server CPU, memory, disk usage
- Container resource usage
- Network throughput
- SSL certificate status

#### Business Metrics Dashboard
- User registrations
- Booking completions
- Revenue metrics
- Subscription conversions

### Sentry Dashboards

Sentry provides built-in dashboards for:

- Error trends and patterns
- Performance metrics
- Release health
- User impact analysis

## Troubleshooting

### Common Issues

#### High Response Times

1. Check database query performance
2. Monitor cache hit rates
3. Review application logs for bottlenecks
4. Check server resource usage

#### High Error Rates

1. Check Sentry for error patterns
2. Review application logs
3. Monitor external service status
4. Check database connectivity

#### Memory Issues

1. Monitor container memory usage
2. Check for memory leaks in application
3. Review database connection pooling
4. Monitor Redis memory usage

#### Database Performance

1. Check slow query logs
2. Monitor connection pool usage
3. Review index effectiveness
4. Check for N+1 query problems

### Debug Mode

Enable debug logging temporarily:

```bash
# Environment variable
DEBUG_LOGGING=true

# Or modify settings
LOGGING['loggers']['apps']['level'] = 'DEBUG'
```

### Performance Profiling

Use Django's profiling tools:

```python
# In settings for development
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    ...
]

INSTALLED_APPS = [
    'debug_toolbar',
    ...
]
```

### Log Analysis

Analyze logs for patterns:

```bash
# Search for errors
grep "ERROR" /var/log/trainerhub/django.log

# Find slow requests
grep "Slow request" /var/log/trainerhub/django.log

# Count requests by status
grep "status_code" /var/log/trainerhub/django.log | jq -r .status_code | sort | uniq -c
```

## Configuration

### Environment Variables

```bash
# Monitoring
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Health Checks
HEALTH_CHECK_ENABLED=true
MONITORING_KEY=your-secret-key

# Performance
PERFORMANCE_MONITORING_ENABLED=true
SLOW_REQUEST_THRESHOLD=5.0
```

### Docker Monitoring

Add monitoring to docker-compose:

```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Best Practices

### Monitoring Principles

1. **Monitor what matters**: Focus on business-critical metrics
2. **Alert on symptoms, not causes**: Alert on user impact, not internal errors
3. **Keep noise low**: Avoid alert fatigue with meaningful thresholds
4. **Automate recovery**: Use self-healing where possible
5. **Document incidents**: Learn from every incident

### Logging Best Practices

1. **Structured logging**: Use consistent JSON format
2. **Appropriate log levels**: Don't log everything as INFO
3. **Include context**: Add user IDs, request IDs, etc.
4. **Log security events**: Track authentication failures, admin actions
5. **Rotate logs**: Prevent disk space issues

### Performance Optimization

1. **Set realistic targets**: P95 < 500ms for API endpoints
2. **Monitor trends**: Watch for gradual performance degradation
3. **Capacity planning**: Monitor resource usage trends
4. **Load testing**: Regularly test system limits

## Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [Django Logging](https://docs.djangoproject.com/en/stable/topics/logging/)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/)

---

**Last Updated:** December 30, 2025
**Version:** 1.0.0