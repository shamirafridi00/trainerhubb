#!/bin/bash
# SSL Certificate Setup for TrainerHub Platform
# Uses Let's Encrypt via Certbot

set -e

echo "==================================="
echo "TrainerHub SSL Certificate Setup"
echo "==================================="

# Install Certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Get email for SSL certificate notifications
read -p "Enter email address for SSL notifications: " EMAIL

# Main domain
MAIN_DOMAIN="trainerhubb.app"

echo ""
echo "Setting up SSL for main domain: $MAIN_DOMAIN"
echo ""

# Option 1: Wildcard certificate for subdomains (requires DNS challenge)
echo "Would you like to set up a wildcard certificate for *.trainerhubb.app?"
echo "This requires DNS TXT record verification."
read -p "(y/n): " WILDCARD

if [ "$WILDCARD" == "y" ]; then
    echo ""
    echo "Setting up wildcard certificate..."
    echo "You will need to add a DNS TXT record to verify domain ownership."
    echo ""
    
    certbot certonly \
        --manual \
        --preferred-challenges dns \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $MAIN_DOMAIN \
        -d "*.$MAIN_DOMAIN"
    
    echo ""
    echo "✓ Wildcard certificate obtained!"
else
    # Option 2: Standard certificate for main domain only
    echo ""
    echo "Setting up certificate for main domain only..."
    echo ""
    
    certbot --nginx \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $MAIN_DOMAIN \
        -d www.$MAIN_DOMAIN
    
    echo ""
    echo "✓ Main domain certificate obtained!"
fi

# Set up auto-renewal
echo ""
echo "Setting up automatic certificate renewal..."

# Add cron job for renewal (runs twice daily)
(crontab -l 2>/dev/null || true; echo "0 0,12 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -

echo "✓ Auto-renewal configured!"

# Test renewal process
echo ""
echo "Testing renewal process..."
certbot renew --dry-run

echo ""
echo "==================================="
echo "SSL Setup Complete!"
echo "==================================="
echo ""
echo "Certificates are located at:"
echo "/etc/letsencrypt/live/$MAIN_DOMAIN/"
echo ""
echo "Auto-renewal is configured to run twice daily."
echo ""
echo "To manually renew certificates, run:"
echo "certbot renew"
echo ""

# Reload nginx to apply certificates
if systemctl is-active --quiet nginx; then
    echo "Reloading nginx..."
    systemctl reload nginx
    echo "✓ Nginx reloaded!"
fi

echo ""
echo "==================================="
echo "Custom Domain SSL Setup"
echo "==================================="
echo ""
echo "To add SSL for custom trainer domains:"
echo ""
echo "1. Ensure the custom domain's DNS points to your server IP"
echo "2. Run: certbot --nginx -d customdomain.com -d www.customdomain.com"
echo "3. Nginx will be automatically configured"
echo ""
echo "Note: Each custom domain needs its own certificate."
echo "These are managed separately from the wildcard certificate."
echo ""

