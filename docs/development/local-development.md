# 🏋️‍♀️ TrainerHub Local Development Setup

This guide explains how to set up the hybrid architecture locally with proper subdomain routing.

## 🏗️ Architecture Overview

TrainerHub uses a **hybrid frontend architecture**:

- **`localhost`** or **`trainerhubb.local`** - SEO-optimized HTMX landing page
- **`app.localhost`** or **`app.trainerhubb.local`** - Full React SPA dashboard
- **`trainer-slug.localhost`** - HTMX public pages

## 🚀 Quick Start

### Option 1: Simple Port-Based Development (Recommended)

```bash
# Run both Django and React servers automatically
./run_local.sh
```

This script will:
- ✅ Start Django backend on port 8000 (HTMX landing page)
- ✅ Start React frontend on port 3000 (React dashboard)
- ✅ Set up database and static files automatically
- ✅ No Docker or hosts file modifications needed

### Option 2: Docker Setup (Advanced)

If you have Docker installed and want subdomain routing:

```bash
# Run the automated setup script
./setup_local_dev.sh
```

This script will:
- ✅ Configure your `/etc/hosts` file for local subdomains
- ✅ Start all Docker containers with development settings
- ✅ Set up the complete development environment

### Option 3: Manual Setup

1. **Configure Hosts File** (optional, for subdomain testing)
   ```bash
   sudo tee -a /etc/hosts > /dev/null << 'EOF'

   # TrainerHub Local Development Domains
   127.0.0.1    trainerhubb.local
   127.0.0.1    www.trainerhubb.local
   127.0.0.1    app.trainerhubb.local
   127.0.0.1    app.localhost
   EOF
   ```

2. **Start Django Backend**
   ```bash
   source venv/bin/activate
   python manage.py runserver 8000 --settings=config.settings.development
   ```

3. **Start React Frontend** (in another terminal)
   ```bash
   cd trainer-app
   npm run dev
   ```

## 🌐 Local Development URLs

After running `./run_local.sh`, you'll have these local endpoints:

| URL | Purpose | Technology |
|-----|---------|------------|
| `http://localhost:8000` | Landing page | HTMX + Tailwind |
| `http://localhost:3000` | React dashboard | React + TypeScript |

### Alternative: Subdomain Setup (with Docker)

If using Docker setup, you'll have these domains:

| Domain | Purpose | Technology |
|--------|---------|------------|
| `http://trainerhubb.local` | Landing page | HTMX + Tailwind |
| `http://app.trainerhubb.local` | React dashboard | React + TypeScript |

## 🔄 User Flow

1. **Visit Landing Page** → `http://localhost:8000`
   - SEO-optimized HTMX page with animations
   - Click "Get Started Free" → React login modal appears

2. **Authentication** → Modal handles login/register
   - Uses Django REST API for authentication
   - On success, redirects to React app on port 3000

3. **Dashboard** → `http://localhost:3000/dashboard`
   - Full React SPA experience
   - Modern dashboard with all features

## 🛠️ Development Workflow

### Starting Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f django

# Rebuild after code changes
docker-compose up --build -d
```

### Testing the Flow

1. **Landing Page**: Visit `http://trainerhubb.local`
   - Should show HTMX landing page with buttons
   - Clicking "Get Started" opens React modal

2. **Authentication**: Use the modal to register/login
   - Should redirect to `http://app.localhost/dashboard`
   - Creates a trainer profile automatically

3. **Dashboard**: Full React app at app subdomain
   - Should show dashboard with navigation
   - Can access all features (clients, bookings, etc.)

### Debugging

```bash
# Check container status
docker-compose ps

# View Django logs
docker-compose logs django

# View Nginx logs
docker-compose logs nginx

# Access Django shell
docker-compose exec django python manage.py shell

# Run Django tests
docker-compose exec django python manage.py test
```

## 🔧 Configuration Files

### Environment Variables
Create `.env` file:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=trainerhub_dev
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=postgres
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
```

### Hosts File Entries
The setup script adds these to `/etc/hosts`:
```
127.0.0.1    localhost
127.0.0.1    trainerhubb.local
127.0.0.1    app.trainerhubb.local
127.0.0.1    app.localhost
```

## 🐛 Troubleshooting

### Common Issues

**1. Subdomains not resolving**
```bash
# Check hosts file
cat /etc/hosts | grep trainerhub

# Flush DNS cache (macOS)
sudo killall -HUP mDNSResponder

# Flush DNS cache (Linux)
sudo systemd-resolve --flush-caches
```

**2. Containers not starting**
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose up --build
```

**3. Authentication not working**
```bash
# Check Django is running
curl http://localhost/api/health/

# Check API endpoints
curl http://localhost/api/auth/me/ -H "Authorization: Token <your-token>"
```

**4. React modal not appearing**
- Check browser console for JavaScript errors
- Ensure nginx is routing correctly
- Check that subdomain type is being set properly

### Resetting Development Environment

```bash
# Stop everything
docker-compose down -v

# Remove all containers and volumes
docker system prune -a
docker volume prune

# Re-run setup
./setup_local_dev.sh
```

## 🎯 Development Tips

1. **Hot Reload**: Code changes auto-reload in development
2. **Database**: Uses SQLite for development (no PostgreSQL setup needed)
3. **Debugging**: Full Django debug mode enabled
4. **API Testing**: Use tools like Postman or curl against `http://localhost/api/`

## 📱 Mobile Testing

For mobile testing on the same network:

1. Find your computer's IP: `ip addr show`
2. Update mobile hosts file or use IP directly
3. Access via: `http://YOUR_IP_ADDRESS`

## 🚀 Production Deployment

When ready for production:
- Use `docker-compose.prod.yml`
- Update DNS to point subdomains to your server
- Configure SSL certificates
- Update nginx.prod.conf for production routing

---

Happy developing! 🏋️‍♀️💪
