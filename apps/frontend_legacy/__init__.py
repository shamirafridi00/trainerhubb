"""
HTMX LEGACY FRONTEND APP - DEPRECATED

This Django app contains legacy HTMX-based web interface components.
It is deprecated and will be removed after React migration is complete.

WARNING: This code is isolated and should not be used for new development.
Use React frontend (trainer-app/) instead.

For backward compatibility during transition:
- All imports are maintained through apps/frontend/__init__.py
- Templates are available in templates/legacy/
- Functionality is gated by USE_HTMX setting
"""

import warnings
warnings.warn(
    "apps.frontend_legacy is deprecated. Migrate to React frontend.",
    DeprecationWarning,
    stacklevel=2
)

