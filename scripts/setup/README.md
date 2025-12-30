# Setup & Initialization Scripts

This folder contains scripts for setting up and initializing the application.

## Scripts

- `create_superuser.py` - Create Django superuser account
- `create_trainer_profile.py` - Create trainer profiles for users
- `reset_admin_password.py` - Reset admin user passwords

## Usage

```bash
# Create initial superuser
python scripts/setup/create_superuser.py

# Create trainer profile for existing user
python scripts/setup/create_trainer_profile.py

# Reset admin password
python scripts/setup/reset_admin_password.py
```

## Purpose

These scripts help with:
- Initial application setup
- User account management
- Profile creation and maintenance
- Password recovery and reset
