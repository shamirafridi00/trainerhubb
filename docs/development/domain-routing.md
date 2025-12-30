# Domain Routing Configuration

This document explains how TrainerHub handles subdomain and custom domain routing for trainer pages.

## Overview

TrainerHub supports three types of domain routing:

1. **Main Application**: `trainerhubb.app` - The main platform where trainers manage their business
2. **Trainer Subdomains**: `{trainer-slug}.trainerhubb.app` - Public pages for each trainer
3. **Custom Domains**: `customdomain.com` - Trainers can use their own domains

## Architecture

### Subdomain Detection

The `SubdomainMiddleware` in `apps/pages/middleware.py` detects the trainer from the request:

```python
# Example: trainer-john.trainerhubb.app -> identifies trainer "john"
```

The middleware:
- Extracts the subdomain from the host
- Looks up the trainer by username or email prefix
- Attaches the trainer object to the request
- Public API endpoints use this to serve trainer-specific content

### Custom Domain Mapping

Custom domains are stored in the `CustomDomain` model:

```python
class CustomDomain(models.Model):
    trainer = ForeignKey(Trainer)
    domain = CharField()  # e.g., "johnsfitness.com"
    is_verified = BooleanField()
    is_active = BooleanField()
```

The middleware checks for custom domains first, then falls back to subdomain detection.

## Nginx Configuration

### Main Application Server

Serves the main platform at `trainerhubb.app`:
- React frontend
- Django API
- Admin panel
- Static/media files

### Subdomain Server

Handles `*.trainerhubb.app` requests:
- Uses regex to extract trainer slug
- Serves public pages (React app)
- Proxies API requests to Django
- Django middleware identifies the trainer

### Custom Domain Server

Catch-all server for custom domains:
- Serves any domain not matching above patterns
- Django middleware performs database lookup
- Maps domain to trainer
- Serves their public pages

## SSL/TLS Configuration

### Wildcard Certificate

For subdomains, use a wildcard certificate:

```bash
./deployment/ssl/ssl-setup.sh
```

This obtains a certificate for:
- `trainerhubb.app`
- `*.trainerhubb.app`

### Custom Domain Certificates

Each custom domain needs its own certificate:

```bash
certbot --nginx -d customdomain.com -d www.customdomain.com
```

The system automatically:
- Obtains the certificate
- Configures nginx
- Sets up auto-renewal

## Setup Instructions

### 1. Install Dependencies

```bash
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx
```

### 2. Copy Nginx Configuration

```bash
cp deployment/nginx/nginx.conf /etc/nginx/sites-available/trainerhubb
ln -s /etc/nginx/sites-available/trainerhubb /etc/nginx/sites-enabled/
```

### 3. Configure DNS

For the main domain:
```
A Record: trainerhubb.app -> YOUR_SERVER_IP
A Record: *.trainerhubb.app -> YOUR_SERVER_IP
```

For custom domains:
```
A Record: customdomain.com -> YOUR_SERVER_IP
CNAME Record: www.customdomain.com -> customdomain.com
```

### 4. Obtain SSL Certificates

```bash
chmod +x deployment/ssl/ssl-setup.sh
./deployment/ssl/ssl-setup.sh
```

### 5. Test Configuration

```bash
nginx -t
systemctl reload nginx
```

## Adding Custom Domains

When a trainer wants to add a custom domain:

### 1. Database Entry

Create a `CustomDomain` record in the admin panel or via API:
- `trainer`: The trainer
- `domain`: `customdomain.com`
- `is_verified`: `False` (initially)
- `is_active`: `False` (initially)

### 2. DNS Verification

Verify the trainer owns the domain:
- Ask them to add a TXT record: `_trainerhubb-verification={verification_token}`
- Check for the record using `dig` or DNS API
- Mark `is_verified=True` when confirmed

### 3. SSL Certificate

Obtain certificate for the custom domain:

```bash
certbot --nginx -d customdomain.com -d www.customdomain.com --email trainer@email.com
```

### 4. Activate Domain

Set `is_active=True` in the database.

The domain is now live and serves the trainer's public pages.

## Troubleshooting

### Subdomain Not Working

1. Check DNS: `dig trainer-slug.trainerhubb.app`
2. Verify nginx is running: `systemctl status nginx`
3. Check nginx logs: `tail -f /var/log/nginx/error.log`
4. Test middleware: Check Django logs for subdomain detection

### Custom Domain Not Working

1. Verify DNS points to server: `dig customdomain.com`
2. Check CustomDomain record in database
3. Verify SSL certificate exists: `ls /etc/letsencrypt/live/customdomain.com/`
4. Check nginx configuration: `nginx -t`

### SSL Certificate Issues

1. Check certificate expiry: `certbot certificates`
2. Test renewal: `certbot renew --dry-run`
3. Check cron job: `crontab -l`
4. Manual renewal: `certbot renew`

## Performance Considerations

### Caching

- Static files cached for 30 days
- Media files cached for 7 days
- Consider adding CDN for global distribution

### Load Balancing

For high traffic:
- Use multiple Django workers (Gunicorn/uWSGI)
- Add Redis for session storage
- Implement database read replicas

### Monitoring

Monitor:
- Nginx access/error logs
- Django performance
- SSL certificate expiry
- DNS resolution times

## Security

### Headers

Nginx adds security headers:
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`

### HTTPS

- All traffic redirected to HTTPS
- TLS 1.2+ only
- Strong cipher suites

### Rate Limiting

Consider adding rate limiting to nginx:

```nginx
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;
limit_req zone=one burst=20 nodelay;
```

## Maintenance

### Certificate Renewal

Automatic renewal runs twice daily via cron.

Manual renewal if needed:
```bash
certbot renew
systemctl reload nginx
```

### Adding New Subdomains

No action needed - wildcard certificate covers all `*.trainerhubb.app`.

### Removing Custom Domains

1. Set `is_active=False` in database
2. Optionally delete SSL certificate: `certbot delete -d customdomain.com`
3. Remove nginx configuration if custom

## Future Enhancements

- Automatic SSL provisioning for custom domains via API
- DNS management integration (Cloudflare API)
- IP-based rate limiting per trainer
- Geographic routing for global trainers
- Custom domain verification UI for trainers

