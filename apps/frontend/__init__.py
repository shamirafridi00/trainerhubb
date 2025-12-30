# HTMX Legacy Frontend App - DEPRECATED
# This module is deprecated. Use React frontend instead.
# All code has been moved to apps/frontend_legacy/
#
# This file maintains import compatibility during transition.
# TODO: Remove after React migration complete

import warnings
warnings.warn(
    "apps.frontend is deprecated. Use React frontend instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from legacy location for compatibility
from apps.frontend_legacy import *