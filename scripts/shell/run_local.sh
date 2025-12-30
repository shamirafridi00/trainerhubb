#!/bin/bash

# TrainerHub Local Development Runner
# Runs both Django backend (port 8000) and React frontend (port 3000)

echo "🏋️‍♀️ Starting TrainerHub Local Development Environment"
echo "===================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Check if React app exists
if [ ! -d "trainer-app" ]; then
    echo "❌ React app not found. Please check your project structure."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings.development
export DEBUG=True

# Create database if it doesn't exist
echo "🗄️  Setting up database..."
python manage.py migrate --settings=config.settings.development

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.development

echo ""
echo "🚀 Starting servers..."
echo "   • Django Backend: http://localhost:8000 (HTMX Landing)"
echo "   • React Frontend:  http://localhost:3000 (React Dashboard)"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start Django server in background
echo "Starting Django server on port 8000..."
python manage.py runserver 8000 --settings=config.settings.development &
DJANGO_PID=$!

# Wait a bit for Django to start
sleep 3

# Start React development server in background
echo "Starting React development server on port 3000..."
cd trainer-app
npm run dev &
REACT_PID=$!

# Wait for React to start
sleep 5

echo ""
echo "✅ Both servers are running!"
echo ""
echo "🌐 Access your application:"
echo "   • Landing Page:    http://localhost:8000"
echo "   • React Dashboard: http://localhost:3000 (after login)"
echo ""
echo "💡 Test the flow:"
echo "   1. Visit http://localhost:8000"
echo "   2. Click 'Get Started' → React modal appears"
echo "   3. Register/Login → Redirects to http://localhost:3000/dashboard"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for background processes
wait
