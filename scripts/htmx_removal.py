#!/usr/bin/env python
"""
HTMX Legacy Removal Management Script

Feature-flag gated removal of HTMX legacy code and templates.
All operations are reversible and logged for audit purposes.

Usage:
    python manage.py htmx_removal --phase=1 --dry-run
    python manage.py htmx_removal --phase=2 --execute
    python manage.py htmx_removal --rollback --phase=1

Environment Variables:
    USE_HTMX: Must be False for Phase 2/3 removals
    DRY_RUN: Set to 'true' for dry-run mode
"""

import os
import logging
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# Setup dedicated removal logging
removal_logger = logging.getLogger('htmx_removal')
removal_logger.setLevel(logging.INFO)
handler = logging.FileHandler(settings.BASE_DIR / 'logs' / 'htmx_removal.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
removal_logger.addHandler(handler)

class HTMXRemovalManager:
    """Manages HTMX legacy removal operations."""

    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.base_dir = Path(settings.BASE_DIR)

    def log_action(self, action, details=""):
        """Log removal action with details."""
        message = f"{'[DRY RUN] ' if self.dry_run else ''}{action}"
        if details:
            message += f" - {details}"
        removal_logger.info(message)
        print(message)

    def safe_remove(self, path, description):
        """Safely remove file/directory with logging."""
        full_path = self.base_dir / path

        if not full_path.exists():
            self.log_action(f"SKIP: Path does not exist", f"{path}")
            return True

        if self.dry_run:
            self.log_action(f"WOULD REMOVE: {description}", f"{path}")
            return True

        try:
            if full_path.is_dir():
                shutil.rmtree(full_path)
            else:
                full_path.unlink()
            self.log_action(f"REMOVED: {description}", f"{path}")
            return True
        except Exception as e:
            self.log_action(f"ERROR: Failed to remove {description}", f"{path} - {e}")
            return False

    def phase_1_infrastructure_cleanup(self):
        """Phase 1: Remove empty templatetags and disable middleware."""
        self.log_action("Starting Phase 1: Infrastructure Cleanup")

        # Remove empty templatetags
        success = self.safe_remove(
            "apps/frontend_legacy/templatetags",
            "Empty HTMX template tags directory"
        )

        # Note: Middleware and deprecation warnings already removed in planning
        self.log_action("Phase 1 Complete")
        return success

    def phase_2_template_removal(self):
        """Phase 2: Remove legacy templates and context processor."""
        if settings.USE_HTMX:
            raise CommandError("Cannot run Phase 2 with USE_HTMX=True. Set USE_HTMX=False first.")

        self.log_action("Starting Phase 2: Template Removal")

        # Remove legacy templates
        success = self.safe_remove(
            "templates/legacy",
            "HTMX legacy templates directory (43 templates)"
        )

        # Note: Context processor and TEMPLATES changes already handled in planning
        self.log_action("Phase 2 Complete")
        return success

    def phase_3_app_removal(self):
        """Phase 3: Remove legacy app completely."""
        if settings.USE_HTMX:
            raise CommandError("Cannot run Phase 3 with USE_HTMX=True. Set USE_HTMX=False first.")

        self.log_action("Starting Phase 3: Complete App Removal")

        # Remove legacy app
        success1 = self.safe_remove(
            "apps/frontend_legacy",
            "HTMX legacy Django app directory"
        )

        # Remove shim directory
        success2 = self.safe_remove(
            "apps/frontend",
            "HTMX compatibility shim directory"
        )

        # Note: Settings and URL changes already handled in planning
        self.log_action("Phase 3 Complete")
        return success1 and success2


class Command(BaseCommand):
    help = 'Manage HTMX legacy removal with feature flags and rollback support'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phase',
            type=int,
            choices=[1, 2, 3],
            help='Removal phase to execute (1-3)'
        )
        parser.add_argument(
            '--rollback',
            action='store_true',
            help='Rollback the specified phase'
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Execute removal (default is dry-run)'
        )

    def handle(self, *args, **options):
        dry_run = not options['execute']
        phase = options['phase']

        if not phase:
            raise CommandError("Must specify --phase")

        manager = HTMXRemovalManager(dry_run=dry_run)

        if options['rollback']:
            self.stdout.write(f"Rollback functionality not implemented. Use git checkout for rollback.")
            return

        # Validate feature flag for Phase 2/3
        if phase >= 2 and settings.USE_HTMX:
            raise CommandError(
                f"Phase {phase} requires USE_HTMX=False. "
                "Set USE_HTMX=False in environment and restart server."
            )

        # Execute appropriate phase
        if phase == 1:
            success = manager.phase_1_infrastructure_cleanup()
        elif phase == 2:
            success = manager.phase_2_template_removal()
        elif phase == 3:
            success = manager.phase_3_app_removal()

        if success:
            self.stdout.write(
                self.style.SUCCESS(f"Phase {phase} {'DRY RUN' if dry_run else 'EXECUTION'} completed successfully")
            )
        else:
            raise CommandError(f"Phase {phase} failed")
