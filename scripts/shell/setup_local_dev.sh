#!/bin/bash

# TrainerHub Local Development Setup
# This script helps set up local subdomain routing for development

echo "🏋️‍♀️ Setting up TrainerHub Local Development Environment"
echo "======================================================"

# Check if running on Linux/macOS
if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for Linux/macOS systems"
    exit 1
fi

# Check if user has sudo access
if ! sudo -n true 2>/dev/null; then
    echo "❌ This script requires sudo access to modify /etc/hosts"
    echo "Please run this script as a user with sudo privileges"
    exit 1
fi

echo "📝 Adding local subdomains to /etc/hosts..."

# Backup hosts file
sudo cp /etc/hosts /etc/hosts.backup.$(date +%Y%m%d_%H%M%S)

# Add TrainerHub local domains
sudo tee -a /etc/hosts > /dev/null << 'EOF'

# TrainerHub Local Development Domains
127.0.0.1    localhost
127.0.0.1    trainerhubb.local
127.0.0.1    www.trainerhubb.local
127.0.0.1    app.trainerhubb.local
127.0.0.1    app.localhost
EOF

echo "✅ Local domains added to /etc/hosts"
echo ""
echo "🌐 Your local domains are now configured:"
echo "   • Landing Page:     http://trainerhubb.local"
echo "   • Landing Page:     http://localhost"
echo "   • React App:        http://app.trainerhubb.local"
echo "   • React App:        http://app.localhost"
echo ""
echo "🚀 Starting Docker containers..."

# Start the development environment
docker-compose down 2>/dev/null
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Docker containers are running!"
    echo ""
    echo "🎯 Test the hybrid architecture:"
    echo "   1. Visit landing page: http://trainerhubb.local"
    echo "   2. Click 'Get Started Free' → React modal appears"
    echo "   3. Register/Login → Redirects to http://app.trainerhubb.local/dashboard"
    echo "   4. Full React SPA experience in the app subdomain"
    echo ""
    echo "📊 Container Status:"
    docker-compose ps
else
    echo "❌ Docker containers failed to start"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "🛠️  Development Commands:"
echo "   • View logs:          docker-compose logs -f"
echo "   • Stop services:      docker-compose down"
echo "   • Rebuild:           docker-compose up --build"
echo ""
echo "🎉 Setup complete! Happy coding! 🏋️‍♀️💪"
