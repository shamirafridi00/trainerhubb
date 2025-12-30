"""
Settings package for TrainerHub.
Dynamically imports the appropriate settings based on DJANGO_SETTINGS_MODULE.
"""

import os
import importlib

# Get the settings module name from environment
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings')

# Extract the specific settings file (e.g., 'development', 'production')
if 'development' in settings_module:
    from .development import *
elif 'production' in settings_module:
    from .production import *
else:
    # Default to base settings (the current settings.py moved to base.py)
    from .base import *
