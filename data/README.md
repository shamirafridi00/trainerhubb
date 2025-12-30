# Data Directory

This folder contains application data files and databases.

## Contents

- `db.sqlite3` - SQLite database file (development only)

## Important Notes

- This directory is included in `.gitignore`
- Contains sensitive application data
- SQLite database should not be used in production
- For production, use PostgreSQL (Supabase)

## Database Management

```bash
# Run migrations
python manage.py migrate

# Create database backup
cp data/db.sqlite3 data/db_backup.sqlite3

# Reset database (CAUTION: destroys all data)
rm data/db.sqlite3
python manage.py migrate
```

## Security

- Never commit database files to version control
- Keep backups in secure locations
- Use environment-specific database configurations
