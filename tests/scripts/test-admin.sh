#!/bin/bash

# Admin Login Test Script
echo "🔑 Testing Admin Login..."
echo "=========================="
echo ""

# Try to login to admin
RESPONSE=$(curl -s -c cookies.txt -b cookies.txt \
  -d "username=admin&password=admin123" \
  http://localhost:8000/admin/login/?next=/admin/)

if [[ $RESPONSE == *"Log in"* ]]; then
    echo "❌ Admin login failed - incorrect credentials"
    echo ""
    echo "Resetting admin password..."
    cd /home/shamir/trainerhubb
    source venv/bin/activate
    python manage.py shell << 'EOF'
from apps.users.models import User
admin = User.objects.get(username='admin')
admin.set_password('admin123')
admin.is_staff = True
admin.is_superuser = True
admin.save()
print("✅ Password reset complete!")
EOF
    echo ""
    echo "Please try again: http://localhost:8000/admin/"
    echo "Username: admin"
    echo "Password: admin123"
else
    echo "✅ Admin interface accessible!"
fi

rm -f cookies.txt
echo ""
echo "=========================="
echo "Admin Panel: http://localhost:8000/admin/"
echo "Username: admin"
echo "Password: admin123"
echo "=========================="

