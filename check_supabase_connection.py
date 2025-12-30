#!/usr/bin/env python
"""
Supabase Connection Diagnostic Tool
Checks if Supabase credentials are configured and connection is working.
"""
import os
import sys
from decouple import config

print("="*70)
print("SUPABASE CONNECTION DIAGNOSTIC")
print("="*70)

# Check environment variables
print("\n1. Checking Environment Variables...")
print("-"*70)

required_vars = {
    'DB_NAME': 'Database name',
    'DB_USER': 'Database user',
    'DB_PASSWORD': 'Database password',
    'DB_HOST': 'Database host',
    'DB_PORT': 'Database port',
    'SUPABASE_URL': 'Supabase URL',
    'SUPABASE_ANON_KEY': 'Supabase anonymous key',
}

missing_vars = []
found_vars = {}

for var, description in required_vars.items():
    try:
        value = config(var)
        if value:
            # Mask sensitive data
            if 'PASSWORD' in var or 'KEY' in var:
                display_value = value[:10] + '...' if len(value) > 10 else '***'
            else:
                display_value = value
            print(f"✓ {var:20s} = {display_value}")
            found_vars[var] = value
        else:
            print(f"✗ {var:20s} = (empty)")
            missing_vars.append(var)
    except Exception as e:
        print(f"✗ {var:20s} = NOT FOUND")
        missing_vars.append(var)

if missing_vars:
    print(f"\n❌ Missing variables: {', '.join(missing_vars)}")
    print("\nPlease add these to your .env file:")
    print("\nExample .env configuration:")
    print("""
# Supabase Database
DB_NAME=postgres
DB_USER=postgres.your-project-ref
DB_PASSWORD=your-database-password
DB_HOST=aws-0-us-west-1.pooler.supabase.com
DB_PORT=6543

# Supabase API
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_PROJECT_ID=your-project-ref
    """)
    sys.exit(1)

# Test network connectivity
print("\n2. Testing Network Connectivity...")
print("-"*70)

import socket

try:
    host = found_vars.get('DB_HOST', '')
    port = int(found_vars.get('DB_PORT', 5432))
    
    print(f"Attempting to connect to {host}:{port}...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    sock.close()
    
    if result == 0:
        print(f"✓ Network connection successful to {host}:{port}")
    else:
        print(f"✗ Cannot reach {host}:{port}")
        print("\nPossible issues:")
        print("  - No internet connection")
        print("  - Firewall blocking connection")
        print("  - Supabase project paused or deleted")
        print("  - Wrong host or port")
        sys.exit(1)
except Exception as e:
    print(f"✗ Network test failed: {e}")
    sys.exit(1)

# Test database connection
print("\n3. Testing Database Connection...")
print("-"*70)

try:
    import psycopg2
    
    conn_params = {
        'dbname': found_vars['DB_NAME'],
        'user': found_vars['DB_USER'],
        'password': found_vars['DB_PASSWORD'],
        'host': found_vars['DB_HOST'],
        'port': found_vars['DB_PORT'],
        'sslmode': 'require',
        'connect_timeout': 10
    }
    
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print(f"✓ Database connection successful!")
    print(f"  PostgreSQL version: {version[:50]}...")
    
    # Check if tables exist
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    table_count = cursor.fetchone()[0]
    print(f"  Tables in database: {table_count}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ All checks passed! Supabase connection is working.")
    
except ImportError:
    print("✗ psycopg2 not installed")
    print("\nInstall it with: pip install psycopg2-binary")
    sys.exit(1)
except psycopg2.OperationalError as e:
    print(f"✗ Database connection failed: {e}")
    print("\nPossible issues:")
    print("  - Wrong database credentials")
    print("  - Database user doesn't have access")
    print("  - Supabase project paused")
    print("  - Connection pooler settings incorrect")
    print("\nTo fix:")
    print("  1. Go to https://supabase.com/dashboard")
    print("  2. Select your project")
    print("  3. Go to Settings → Database")
    print("  4. Copy the connection string")
    print("  5. Update your .env file")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("1. Run migrations: python manage.py migrate")
print("2. Create superuser: python manage.py createsuperuser")
print("3. Start server: python manage.py runserver")
print("4. Test admin panel: python test_admin_panel.py")
print("="*70)

