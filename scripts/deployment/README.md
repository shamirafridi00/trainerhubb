# Deployment & Docker Configuration

This folder contains Docker and deployment configuration files.

## Files

- `Dockerfile` - Docker image configuration for the application
- `docker-compose.yml` - Local development Docker Compose setup
- `docker-compose.prod.yml` - Production deployment Docker Compose setup
- `env.example` - Example environment variables file
- `nginx/` - Nginx configuration files for production deployment
- `ssl/` - SSL certificate configuration scripts

## Usage

```bash
# Copy environment template
cp scripts/deployment/env.example .env

# Local development
docker-compose up

# Production deployment
docker-compose -f scripts/deployment/docker-compose.prod.yml up -d

# Build Docker image
docker build -f scripts/deployment/Dockerfile .
```

## Purpose

These files provide:
- Containerized application deployment
- Development environment setup
- Production-ready deployment configuration
- Multi-environment support (dev/prod)
