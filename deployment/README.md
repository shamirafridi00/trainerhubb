# TrainerHub Production Deployment Guide

This guide covers the complete production deployment process for the TrainerHub platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [SSL Certificate Setup](#ssl-certificate-setup)
4. [Application Deployment](#application-deployment)
5. [Database Setup](#database-setup)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring Setup](#monitoring-setup)
8. [Backup Strategy](#backup-strategy)
9. [Maintenance](#maintenance)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### Server Requirements

- **Ubuntu 20.04+** or **Debian 11+**
- **4GB RAM** minimum, 8GB recommended
- **2 CPU cores** minimum, 4 recommended
- **50GB SSD storage** minimum
- **Root access** or sudo privileges

### Required Software

- Docker & Docker Compose
- Nginx
- PostgreSQL (if not using Docker)
- Redis (if not using Docker)
- Certbot (for SSL)
- Git

### Domain Requirements

- Domain name (trainerhubb.app or custom domain)
- DNS access to configure records
- SSL certificate (Let's Encrypt via Certbot)

## Server Setup

### 1. Initial Server Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git htop vim ufw fail2ban

# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Create deployment user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG sudo deploy
sudo -u deploy mkdir -p /home/deploy/trainerhub
```

### 2. Install Docker and Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker deploy

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 3. Install and Configure Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Remove default configuration
sudo rm /etc/nginx/sites-enabled/default

# Copy our configuration
sudo cp deployment/nginx/nginx.prod.conf /etc/nginx/nginx.conf

# Test configuration
sudo nginx -t

# Enable and start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

## SSL Certificate Setup

### Using the SSL Setup Script

```bash
# Make script executable
chmod +x deployment/ssl/ssl-setup.sh

# Run SSL setup
sudo ./deployment/ssl/ssl-setup.sh

# Follow prompts to configure certificates
```

### Manual SSL Setup

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain wildcard certificate
sudo certbot certonly --manual --preferred-challenges=dns --email admin@trainerhubb.app --server https://acme-v02.api.letsencrypt.org/directory --agree-tos -d "*.trainerhubb.app"

# Follow DNS configuration instructions
# Then create symlinks for easy access
sudo ln -sf /etc/letsencrypt/live/trainerhubb.app/fullchain.pem /etc/ssl/certs/trainerhubb.crt
sudo ln -sf /etc/letsencrypt/live/trainerhubb.app/privkey.pem /etc/ssl/certs/trainerhubb.key
```

### Certificate Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Setup renewal hook to reload Nginx
sudo mkdir -p /etc/letsencrypt/renewal-hooks/deploy
sudo tee /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh > /dev/null <<EOF
#!/bin/bash
systemctl reload nginx
EOF
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

## Application Deployment

### 1. Clone Repository

```bash
# Clone as deploy user
sudo -u deploy git clone https://github.com/your-org/trainerhub.git /home/deploy/trainerhub
cd /home/deploy/trainerhub
```

### 2. Configure Environment

```bash
# Copy environment template
cp deployment/env.example .env

# Edit with your values
nano .env

# Set proper permissions
chmod 600 .env
```

### 3. Build and Start Services

```bash
# Build production containers
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs
```

### 4. Run Database Migrations

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec django python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec django python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec django python manage.py collectstatic --noinput
```

## Database Setup

### PostgreSQL in Docker (Recommended)

The `docker-compose.prod.yml` includes PostgreSQL configuration. The database will be automatically initialized.

### External PostgreSQL

If using external PostgreSQL:

```bash
# Install PostgreSQL client for management
sudo apt install -y postgresql-client

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE trainerhubb_prod;
CREATE USER trainerhubb_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE trainerhubb_prod TO trainerhubb_user;
ALTER USER trainerhubb_user CREATEDB;
\q
```

## Environment Configuration

### Required Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,*.yourdomain.com

# Database
DB_NAME=trainerhubb_prod
DB_USER=trainerhubb_user
DB_PASSWORD=your-secure-password
DB_HOST=postgres  # or your external DB host

# Redis
REDIS_URL=redis://redis:6379/0

# Email (SendGrid)
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Payments (Paddle)
PADDLE_VENDOR_ID=your-vendor-id
PADDLE_API_KEY=your-api-key
PADDLE_WEBHOOK_SECRET=your-webhook-secret

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_CUSTOM_DOMAIN=your-cdn-domain.com

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### Generate Secret Key

```python
# Run in Python shell
import secrets
print(secrets.token_urlsafe(50))
```

## Monitoring Setup

### 1. Sentry Error Tracking

```bash
# Install sentry-cli (optional)
npm install -g @sentry/cli

# Configure Sentry in your environment
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=1.0
```

### 2. Application Monitoring

```bash
# Check application health
curl -f https://yourdomain.com/health/

# View logs
docker-compose -f docker-compose.prod.yml logs django
docker-compose -f docker-compose.prod.yml logs celery
```

### 3. Database Monitoring

```bash
# Check database connections
docker-compose -f docker-compose.prod.yml exec postgres psql -U trainerhubb_user -d trainerhubb_prod -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli info
```

## Backup Strategy

### Database Backup

```bash
# Create backup script
sudo tee /home/deploy/backup.sh > /dev/null <<EOF
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p \$BACKUP_DIR

# Database backup
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U trainerhubb_user trainerhubb_prod > \$BACKUP_DIR/db_backup_\$DATE.sql

# Media files backup (if using local storage)
tar -czf \$BACKUP_DIR/media_backup_\$DATE.tar.gz /app/media/

# Clean old backups (keep last 30 days)
find \$BACKUP_DIR -name "*.sql" -mtime +30 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: \$DATE"
EOF

chmod +x /home/deploy/backup.sh
```

### Automated Backups

```bash
# Add to crontab for daily backups at 2 AM
sudo crontab -e

# Add this line:
0 2 * * * /home/deploy/backup.sh
```

## Maintenance

### Updating the Application

```bash
# Pull latest changes
cd /home/deploy/trainerhub
git pull origin main

# Build new images
docker-compose -f docker-compose.prod.yml build

# Run migrations (if any)
docker-compose -f docker-compose.prod.yml run --rm django python manage.py migrate

# Restart services
docker-compose -f docker-compose.prod.yml up -d

# Clean up old images
docker image prune -f
```

### Log Rotation

```bash
# Configure logrotate for Django logs
sudo tee /etc/logrotate.d/trainerhub > /dev/null <<EOF
/home/deploy/trainerhub/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 deploy deploy
    postrotate
        docker-compose -f /home/deploy/trainerhub/docker-compose.prod.yml restart django
    endscript
}
EOF
```

### SSL Certificate Renewal

SSL certificates are automatically renewed by Certbot. Monitor renewal logs:

```bash
# Check renewal status
sudo certbot certificates

# View renewal logs
sudo journalctl -u certbot
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs django

# Check resource usage
docker stats
```

#### 2. Database Connection Issues

```bash
# Test database connection
docker-compose -f docker-compose.prod.yml exec django python manage.py dbshell

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres
```

#### 3. SSL Certificate Problems

```bash
# Check certificate validity
openssl x509 -in /etc/ssl/certs/trainerhubb.crt -text -noout

# Test renewal
sudo certbot renew --dry-run
```

#### 4. Performance Issues

```bash
# Check application metrics
docker-compose -f docker-compose.prod.yml exec redis redis-cli info

# Monitor resource usage
htop
docker stats

# Check Nginx status
sudo systemctl status nginx
sudo nginx -t
```

#### 5. 502 Bad Gateway

```bash
# Check if Django is running
docker-compose -f docker-compose.prod.yml ps django

# Check Django logs
docker-compose -f docker-compose.prod.yml logs django

# Test Django directly
docker-compose -f docker-compose.prod.yml exec django curl http://localhost:8000/health/
```

### Emergency Recovery

#### Quick Rollback

```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Checkout previous version
git checkout HEAD~1

# Redeploy
docker-compose -f docker-compose.prod.yml up -d
```

#### Database Recovery

```bash
# Stop application
docker-compose -f docker-compose.prod.yml stop django celery

# Restore from backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U trainerhubb_user trainerhubb_prod < /home/deploy/backups/db_backup_YYYYMMDD_HHMMSS.sql

# Restart services
docker-compose -f docker-compose.prod.yml start django celery
```

## Security Checklist

- [ ] SSH access restricted to key-based authentication
- [ ] Firewall configured (UFW)
- [ ] SSL certificates properly configured
- [ ] Environment variables secured
- [ ] Database credentials rotated regularly
- [ ] Admin URL changed from default
- [ ] Debug mode disabled
- [ ] SECRET_KEY properly generated
- [ ] File permissions set correctly
- [ ] Regular security updates applied
- [ ] Fail2ban configured for SSH protection

## Performance Optimization

### Database Optimization

```bash
# Analyze query performance
docker-compose -f docker-compose.prod.yml exec postgres psql -U trainerhubb_user trainerhubb_prod -c "EXPLAIN ANALYZE SELECT * FROM bookings_booking LIMIT 10;"

# Check index usage
docker-compose -f docker-compose.prod.yml exec postgres psql -U trainerhubb_user trainerhubb_prod -c "SELECT * FROM pg_stat_user_indexes WHERE schemaname = 'public';"
```

### Caching Optimization

```bash
# Monitor cache hit rates
docker-compose -f docker-compose.prod.yml exec redis redis-cli info stats

# Clear cache if needed
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL
```

### Static File Optimization

```bash
# Pre-compress static files
docker-compose -f docker-compose.prod.yml exec django python manage.py compress

# Test CDN configuration
curl -I https://your-cdn.com/static/css/main.css
```

## Support

For additional support:
1. Check application logs
2. Review monitoring dashboards
3. Consult troubleshooting guide
4. Contact development team

---

**Last Updated:** December 30, 2025
**Version:** 1.0.0
