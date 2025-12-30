# TrainerHub Deployment Guide

This guide covers deploying TrainerHub to production.

## Overview

TrainerHub consists of:
- Django backend (REST API)
- React frontend (Single Page App)
- PostgreSQL database
- Redis (optional, for caching)
- Nginx (web server/reverse proxy)
- Let's Encrypt SSL certificates

## Prerequisites

- Ubuntu 20.04+ server
- Domain name pointing to your server
- Root or sudo access
- At least 2GB RAM
- 20GB disk space

## Quick Start (Docker)

Coming soon: Docker Compose setup for easy deployment.

## Manual Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-dev python3-venv \
    postgresql postgresql-contrib nginx \
    git curl build-essential

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. Create Deploy User

```bash
# Create user
sudo adduser trainerhubb
sudo usermod -aG sudo trainerhubb

# Switch to user
sudo su - trainerhubb
```

### 3. Clone Repository

```bash
cd /home/trainerhubb
git clone https://github.com/yourorg/trainerhubb.git
cd trainerhubb
```

### 4. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 5. Configure Database

```bash
# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE trainerhubb_prod;
CREATE USER trainerhubb WITH PASSWORD 'secure-password-here';
ALTER ROLE trainerhubb SET client_encoding TO 'utf8';
ALTER ROLE trainerhubb SET default_transaction_isolation TO 'read committed';
ALTER ROLE trainerhubb SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE trainerhubb_prod TO trainerhubb;
\q
EOF
```

### 6. Environment Variables

Create `/home/trainerhubb/trainerhubb/.env.production`:

```env
DEBUG=False
SECRET_KEY=generate-secure-random-key-here
ALLOWED_HOSTS=trainerhubb.app,www.trainerhubb.app,*.trainerhubb.app
DJANGO_SETTINGS_MODULE=config.settings

DATABASE_URL=postgresql://trainerhubb:password@localhost/trainerhubb_prod

SENDGRID_API_KEY=your-key
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890

PADDLE_VENDOR_ID=your-id
PADDLE_API_KEY=your-key
PADDLE_PUBLIC_KEY=your-key
PADDLE_WEBHOOK_SECRET=your-secret
PADDLE_ENVIRONMENT=production

CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret

REDIS_URL=redis://localhost:6379/0
```

### 7. Run Migrations

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 8. Build Frontend

```bash
cd trainer-app
npm install
npm run build
```

### 9. Configure Gunicorn

Create `/etc/systemd/system/trainerhubb.service`:

```ini
[Unit]
Description=TrainerHub Django Application
After=network.target

[Service]
Type=notify
User=trainerhubb
Group=trainerhubb
WorkingDirectory=/home/trainerhubb/trainerhubb
Environment="PATH=/home/trainerhubb/trainerhubb/venv/bin"
EnvironmentFile=/home/trainerhubb/trainerhubb/.env.production
ExecStart=/home/trainerhubb/trainerhubb/venv/bin/gunicorn \
          --bind unix:/home/trainerhubb/trainerhubb/gunicorn.sock \
          --workers 3 \
          --timeout 60 \
          --access-logfile /var/log/trainerhubb/access.log \
          --error-logfile /var/log/trainerhubb/error.log \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Create log directory:
```bash
sudo mkdir -p /var/log/trainerhubb
sudo chown trainerhubb:trainerhubb /var/log/trainerhubb
```

Start Gunicorn:
```bash
sudo systemctl start trainerhubb
sudo systemctl enable trainerhubb
sudo systemctl status trainerhubb
```

### 10. Configure Nginx

Copy the nginx configuration:

```bash
sudo cp deployment/nginx/nginx.conf /etc/nginx/sites-available/trainerhubb
sudo ln -s /etc/nginx/sites-available/trainerhubb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Update paths in nginx.conf:
- `/var/www/static/` -> Django static files
- `/var/www/media/` -> Django media files  
- `/var/www/frontend/` -> React build output
- `unix:/home/trainerhubb/trainerhubb/gunicorn.sock` -> Gunicorn socket

### 11. Set Up SSL

```bash
cd /home/trainerhubb/trainerhubb
chmod +x deployment/ssl/ssl-setup.sh
sudo ./deployment/ssl/ssl-setup.sh
```

Follow the prompts to obtain SSL certificates.

### 12. Set Up Static Files

```bash
sudo mkdir -p /var/www/static /var/www/media /var/www/frontend
sudo chown trainerhubb:trainerhubb /var/www/static /var/www/media /var/www/frontend

# Copy static files
cp -r /home/trainerhubb/trainerhubb/staticfiles/* /var/www/static/

# Copy frontend build
cp -r /home/trainerhubb/trainerhubb/trainer-app/dist/* /var/www/frontend/
```

### 13. Configure Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 14. Set Up Monitoring (Optional)

Install and configure:
- **Sentry** for error tracking
- **New Relic** or **Datadog** for performance monitoring
- **Uptime Robot** for uptime monitoring
- **Logrotate** for log management

### 15. Set Up Backups

Create backup script `/home/trainerhubb/backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
BACKUP_DIR="/home/trainerhubb/backups"

mkdir -p $BACKUP_DIR

# Backup database
pg_dump trainerhubb_prod | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/media/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

Add to cron:
```bash
crontab -e
# Add: 0 2 * * * /home/trainerhubb/backup.sh
```

## Updating the Application

### Backend Updates

```bash
cd /home/trainerhubb/trainerhubb
git pull origin main

source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

sudo cp -r staticfiles/* /var/www/static/
sudo systemctl restart trainerhubb
```

### Frontend Updates

```bash
cd /home/trainerhubb/trainerhubb/trainer-app
git pull origin main
npm install
npm run build
sudo cp -r dist/* /var/www/frontend/
```

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SSH_HOST }}
          username: trainerhubb
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /home/trainerhubb/trainerhubb
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate
            python manage.py collectstatic --noinput
            sudo systemctl restart trainerhubb
```

## Environment-Specific Settings

Create `config/settings/production.py`:

```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/trainerhubb/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

## Monitoring & Maintenance

### Health Checks

Create health check endpoint in `apps/core/views.py`:

```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'healthy'})
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=500)
```

### Log Monitoring

```bash
# View Django logs
tail -f /var/log/trainerhubb/error.log

# View Nginx logs
tail -f /var/log/nginx/error.log

# View Gunicorn logs
sudo journalctl -u trainerhubb -f
```

### Performance Monitoring

Use tools like:
- Django Debug Toolbar (development only)
- New Relic APM
- Datadog
- Custom metrics with StatsD

## Scaling

### Horizontal Scaling

1. Set up load balancer (HAProxy or AWS ELB)
2. Deploy multiple application servers
3. Use shared session storage (Redis)
4. Use CDN for static/media files

### Database Scaling

1. Set up read replicas
2. Implement connection pooling (PgBouncer)
3. Optimize queries with indexes
4. Consider sharding for very large datasets

### Caching Strategy

1. Redis for session storage
2. Cache frequently accessed data
3. Use CDN for static assets
4. Implement HTTP caching headers

## Troubleshooting

### Application Won't Start

```bash
# Check Gunicorn status
sudo systemctl status trainerhubb

# View logs
sudo journalctl -u trainerhubb -n 50

# Test manually
cd /home/trainerhubb/trainerhubb
source venv/bin/activate
gunicorn config.wsgi:application
```

### Database Connection Issues

```bash
# Test connection
psql -U trainerhubb -d trainerhubb_prod -h localhost

# Check PostgreSQL status
sudo systemctl status postgresql
```

### Nginx Issues

```bash
# Test configuration
sudo nginx -t

# Check logs
tail -f /var/log/nginx/error.log

# Reload nginx
sudo systemctl reload nginx
```

### SSL Certificate Issues

```bash
# Check certificates
sudo certbot certificates

# Renew manually
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Use environment variables for secrets
- [ ] Enable firewall
- [ ] Set up SSL/TLS
- [ ] Keep software updated
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular backups
- [ ] Review and audit logs
- [ ] Use strong SECRET_KEY
- [ ] Disable DEBUG in production
- [ ] Set ALLOWED_HOSTS correctly
- [ ] Use HTTPS only
- [ ] Implement CSRF protection
- [ ] Set security headers

## Support

For deployment support:
- Email: devops@trainerhubb.app
- Slack: #deployments channel
- Documentation: https://docs.trainerhubb.app/deployment

---

Good luck with your deployment! 🚀

