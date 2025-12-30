#!/bin/bash

# SSL Certificate Setup Script for TrainerHub
# This script sets up SSL certificates for production deployment

set -e

# Configuration
DOMAIN="trainerhubb.app"
EMAIL="admin@trainerhubb.app"
CERT_DIR="/etc/ssl/certs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root"
    exit 1
fi

# Install Certbot if not installed
if ! command -v certbot &> /dev/null; then
    log "Installing Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Create certificate directory
mkdir -p "$CERT_DIR"

# Function to obtain wildcard certificate
obtain_wildcard_cert() {
    log "Obtaining wildcard certificate for *.$DOMAIN..."

    # Stop nginx temporarily
    systemctl stop nginx || true

    # Obtain wildcard certificate
    if certbot certonly \
        --standalone \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --domain "*.$DOMAIN" \
        --domain "$DOMAIN"; then

        log "Wildcard certificate obtained successfully"

        # Create symlinks for easy access
        ln -sf "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$CERT_DIR/trainerhubb.crt"
        ln -sf "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$CERT_DIR/trainerhubb.key"

        # Set proper permissions
        chmod 600 "$CERT_DIR/trainerhubb.key"
        chown nginx:nginx "$CERT_DIR"/*.crt "$CERT_DIR"/*.key

        return 0
    else
        error "Failed to obtain wildcard certificate"
        return 1
    fi
}

# Function to obtain regular certificate
obtain_regular_cert() {
    log "Obtaining regular certificate for $DOMAIN..."

    if certbot --nginx \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --domain "$DOMAIN"; then

        log "Certificate obtained successfully"
        return 0
    else
        error "Failed to obtain certificate"
        return 1
    fi
}

# Function to setup auto-renewal
setup_renewal() {
    log "Setting up certificate auto-renewal..."

    # Create renewal hook script
    cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh << 'EOF'
#!/bin/bash
systemctl reload nginx
EOF

    chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh

    # Test renewal
    certbot renew --dry-run

    log "Auto-renewal configured"
}

# Function to check certificate validity
check_certificates() {
    log "Checking certificate validity..."

    if [[ -f "$CERT_DIR/trainerhubb.crt" ]]; then
        # Check expiry date
        expiry_date=$(openssl x509 -in "$CERT_DIR/trainerhubb.crt" -noout -enddate | cut -d= -f2)
        expiry_epoch=$(date -d "$expiry_date" +%s)
        current_epoch=$(date +%s)
        days_left=$(( (expiry_epoch - current_epoch) / 86400 ))

        if [[ $days_left -gt 30 ]]; then
            log "Certificate is valid for $days_left days"
        else
            warn "Certificate expires in $days_left days"
        fi
    else
        warn "Certificate file not found"
    fi
}

# Main execution
main() {
    log "Starting SSL certificate setup for TrainerHub..."

    # Check existing certificates
    if [[ -f "$CERT_DIR/trainerhubb.crt" ]]; then
        log "Certificate already exists, checking validity..."
        check_certificates

        read -p "Do you want to renew the existing certificate? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Skipping certificate renewal"
            exit 0
        fi
    fi

    # Try to obtain wildcard certificate first
    if obtain_wildcard_cert; then
        log "Wildcard certificate setup completed"
    else
        log "Falling back to regular certificate..."
        if obtain_regular_cert; then
            log "Regular certificate setup completed"
        else
            error "Failed to obtain any certificate"
            exit 1
        fi
    fi

    # Setup auto-renewal
    setup_renewal

    # Restart nginx
    log "Restarting Nginx..."
    systemctl start nginx || systemctl reload nginx

    log "SSL setup completed successfully!"
    log "Your site is now available at https://$DOMAIN"
}

# Run main function
main "$@"