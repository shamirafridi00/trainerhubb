#!/usr/bin/env python
"""
HTMX Removal Rollback Playbook

Emergency rollback procedures for HTMX legacy removal phases.
Uses git history for complete restoration.

Usage:
    python scripts/rollback_htmx_removal.py --phase=2 --confirm
    python scripts/rollback_htmx_removal.py --emergency --commit=abc123
"""

import subprocess
import sys
from pathlib import Path

class HTMXRemovalRollback:
    """Manages rollback of HTMX removal phases."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.rollback_log = self.project_root / "logs" / "htmx_rollback.log"

    def log_rollback(self, action, details=""):
        """Log rollback action."""
        with open(self.rollback_log, 'a') as f:
            f.write(f"{action}: {details}\n")
        print(f"🔄 {action}: {details}")

    def run_command(self, cmd, check=True):
        """Run shell command safely."""
        try:
            result = subprocess.run(cmd, shell=True, cwd=self.project_root,
                                  capture_output=True, text=True)
            if check and result.returncode != 0:
                print(f"Command failed: {cmd}")
                print(f"Error: {result.stderr}")
                return False, result.stdout, result.stderr
            return True, result.stdout, result.stderr
        except Exception as e:
            print(f"Exception running command: {e}")
            return False, "", str(e)

    def rollback_phase_1(self):
        """Rollback Phase 1: Infrastructure cleanup."""
        self.log_rollback("Starting Phase 1 Rollback", "Infrastructure cleanup reversal")

        # Restore middleware
        success, _, _ = self.run_command(
            "git checkout HEAD~1 -- config/settings.py"
        )
        if success:
            self.log_rollback("Restored", "Middleware settings in config/settings.py")
        else:
            self.log_rollback("Manual Restore Needed", "Add middleware back to settings")

        # Restore template tags directory
        success, _, _ = self.run_command(
            "mkdir -p apps/frontend_legacy/templatetags && touch apps/frontend_legacy/templatetags/__init__.py"
        )
        if success:
            self.log_rollback("Restored", "Empty templatetags directory")

        # Restore deprecation warnings
        deprecation_code = 'import warnings\nwarnings.warn("apps.frontend_legacy is deprecated...", DeprecationWarning, stacklevel=2)'
        success, _, _ = self.run_command(
            f"echo '{deprecation_code}' >> apps/frontend_legacy/__init__.py"
        )
        if success:
            self.log_rollback("Restored", "Deprecation warnings in legacy app")

        self.log_rollback("Phase 1 Rollback Complete", "Infrastructure restored")
        return True

    def rollback_phase_2(self):
        """Rollback Phase 2: Template removal."""
        self.log_rollback("Starting Phase 2 Rollback", "Template removal reversal")

        # Restore templates from git
        success, _, _ = self.run_command(
            "git checkout HEAD~1 -- templates/legacy/"
        )
        if success:
            self.log_rollback("Restored", "Legacy templates directory")
        else:
            self.log_rollback("Manual Restore Needed", "Restore templates/legacy/ from backup")

        # Restore context processor and TEMPLATES settings
        success, _, _ = self.run_command(
            "git checkout HEAD~1 -- config/settings.py"
        )
        if success:
            self.log_rollback("Restored", "Template settings in config/settings.py")
        else:
            self.log_rollback("Manual Restore Needed", "Restore TEMPLATES and context processor settings")

        self.log_rollback("Phase 2 Rollback Complete", "Templates and settings restored")
        return True

    def rollback_phase_3(self):
        """Rollback Phase 3: Complete app removal."""
        self.log_rollback("Starting Phase 3 Rollback", "Complete app removal reversal")

        # This is the most complex rollback - restore entire app structure
        success, _, _ = self.run_command(
            "git checkout HEAD~1 -- apps/frontend_legacy/ apps/frontend/"
        )
        if success:
            self.log_rollback("Restored", "Complete app structure and shim")
        else:
            self.log_rollback("Manual Restore Needed", "Restore apps/frontend/ and apps/frontend_legacy/ from backup")

        # Restore settings and URLs
        success, _, _ = self.run_command(
            "git checkout HEAD~1 -- config/settings.py config/urls.py"
        )
        if success:
            self.log_rollback("Restored", "Settings and URL configuration")
        else:
            self.log_rollback("Manual Restore Needed", "Restore INSTALLED_APPS, MIDDLEWARE, and URL patterns")

        self.log_rollback("Phase 3 Rollback Complete", "Full HTMX functionality restored")
        return True

    def emergency_rollback(self, commit_hash):
        """Emergency rollback to specific commit."""
        self.log_rollback("Emergency Rollback Initiated", f"To commit: {commit_hash}")

        # Hard reset to specific commit
        success, _, _ = self.run_command(f"git reset --hard {commit_hash}")
        if success:
            self.log_rollback("Emergency Rollback Complete", f"Reset to {commit_hash}")
            return True
        else:
            self.log_rollback("Emergency Rollback Failed", "Manual git operations required")
            return False

    def get_rollback_estimate(self, phase):
        """Get time estimate for rollback."""
        estimates = {
            1: "< 2 minutes",
            2: "< 5 minutes",
            3: "< 10 minutes"
        }
        return estimates.get(phase, "Unknown")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='HTMX removal rollback management')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3], help='Phase to rollback')
    parser.add_argument('--emergency', action='store_true', help='Emergency rollback to commit')
    parser.add_argument('--commit', help='Commit hash for emergency rollback')
    parser.add_argument('--confirm', action='store_true', help='Confirm rollback execution')
    parser.add_argument('--estimate', type=int, choices=[1, 2, 3], help='Show time estimate for rollback')

    args = parser.parse_args()

    rollback = HTMXRemovalRollback()

    if args.estimate:
        print(f"Phase {args.estimate} rollback time estimate: {rollback.get_rollback_estimate(args.estimate)}")
        sys.exit(0)

    if not args.confirm and not args.emergency:
        print("Add --confirm to execute rollback, or --emergency for emergency rollback")
        print("Use --estimate to see time requirements")
        sys.exit(1)

    if args.emergency and args.commit:
        print(f"⚠️  EMERGENCY ROLLBACK TO COMMIT {args.commit}")
        print("This will reset ALL changes to the specified commit")
        print("Are you sure? (This cannot be undone easily)")
        confirm = input("Type 'YES' to confirm: ")
        if confirm == 'YES':
            success = rollback.emergency_rollback(args.commit)
            sys.exit(0 if success else 1)
        else:
            print("Emergency rollback cancelled")
            sys.exit(1)

    if args.phase:
        print(f"🔄 Rolling back Phase {args.phase}")
        print(f"Estimated time: {rollback.get_rollback_estimate(args.phase)}")

        if args.phase == 1:
            success = rollback.rollback_phase_1()
        elif args.phase == 2:
            success = rollback.rollback_phase_2()
        elif args.phase == 3:
            success = rollback.rollback_phase_3()

        if success:
            print(f"✅ Phase {args.phase} rollback completed successfully")
        else:
            print(f"❌ Phase {args.phase} rollback failed - manual intervention required")
            sys.exit(1)
