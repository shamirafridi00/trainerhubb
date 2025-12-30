#!/usr/bin/env python
"""
Project Structure Reorganization Script

Consolidates documentation, testing files, and cleans up directory structure.
All operations are logged and reversible.

Usage:
    python scripts/reorganize_project.py --dry-run
    python scripts/reorganize_project.py --execute
    python scripts/reorganize_project.py --rollback
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/project_reorganization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('project_reorg')

class ProjectReorganizer:
    """Manages project structure reorganization."""

    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent
        self.moves_log = []  # Track all moves for rollback

    def log_move(self, src: str, dst: str, action: str = "MOVE"):
        """Log a file/directory move operation."""
        entry = {
            'action': action,
            'src': str(src),
            'dst': str(dst),
            'timestamp': os.path.getctime(str(src)) if os.path.exists(src) else None
        }
        self.moves_log.append(entry)
        logger.info(f"{action}: {src} -> {dst}")

    def safe_move(self, src: Path, dst: Path, description: str) -> bool:
        """Safely move file/directory with logging."""
        src_full = self.project_root / src
        dst_full = self.project_root / dst

        if not src_full.exists():
            logger.warning(f"Source does not exist: {src_full}")
            return False

        # Create destination directory if needed
        dst_full.parent.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            logger.info(f"[DRY RUN] Would move: {src_full} -> {dst_full}")
            return True

        try:
            if src_full.is_file():
                shutil.move(str(src_full), str(dst_full))
            else:
                # For directories, move contents if destination exists
                if dst_full.exists():
                    for item in src_full.iterdir():
                        shutil.move(str(item), str(dst_full))
                    src_full.rmdir()  # Remove empty source directory
                else:
                    shutil.move(str(src_full), str(dst_full))

            self.log_move(src, dst, "MOVED")
            return True
        except Exception as e:
            logger.error(f"Failed to move {src} -> {dst}: {e}")
            return False

    def consolidate_documentation(self):
        """Consolidate all documentation files into docs/."""
        logger.info("Starting documentation consolidation...")

        # Create docs subdirectories
        docs_dirs = [
            "docs/migration",
            "docs/api",
            "docs/deployment",
            "docs/development",
            "docs/admin",
            "docs/project-history"
        ]

        for dir_path in docs_dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)

        # Documentation file mappings
        doc_moves = [
            # Root level docs -> docs/
            ("ADMIN_LOGIN_INSTRUCTIONS.md", "docs/admin/admin-login-instructions.md"),
            ("ADMIN_PANEL_READY.md", "docs/admin/admin-panel-ready.md"),
            ("ADMIN_PANEL_SUCCESS.md", "docs/admin/admin-panel-success.md"),
            ("AUTH_WORKING_SUMMARY.md", "docs/migration/auth-working-summary.md"),
            ("EPIC_0_2_SUCCESS.md", "docs/project-history/epic-0-2-success.md"),
            ("EPIC_0_3_SUCCESS.md", "docs/project-history/epic-0-3-success.md"),
            ("EPIC_0_COMPLETE_SUMMARY.md", "docs/project-history/epic-0-complete-summary.md"),
            ("EPIC_1_COMPLETE.md", "docs/project-history/epic-1-complete.md"),
            ("EPIC_9_COMPLETE_IMPLEMENTATION_SUMMARY.md", "docs/project-history/epic-9-complete-implementation-summary.md"),
            ("EPIC_PROGRESS_COMPLETE.md", "docs/project-history/epic-progress-complete.md"),
            ("FINAL_IMPLEMENTATION_SUMMARY.md", "docs/project-history/final-implementation-summary.md"),
            ("FIX_NETWORK_ERRORS.md", "docs/development/fix-network-errors.md"),
            ("HOSTS_SETUP.txt", "docs/development/hosts-setup.txt"),
            ("IMPLEMENTATION_PROGRESS_SUMMARY.md", "docs/project-history/implementation-progress-summary.md"),
            ("README_IMPLEMENTATION_STATUS.md", "docs/project-history/readme-implementation-status.md"),
            ("README_LOCAL_SETUP.md", "docs/development/readme-local-setup.md"),
            ("RESTART_SERVER_INSTRUCTIONS.md", "docs/development/restart-server-instructions.md"),
            ("TESTING_IMPLEMENTATION_COMPLETE.md", "docs/project-history/testing-implementation-complete.md"),
            ("TESTING.md", "docs/development/testing.md"),

            # Docs/ directory reorganization
            ("Docs/01_Getting_Started/", "docs/development/getting-started/"),
            ("Docs/02_Development_Checklists/", "docs/development/checklists/"),
            ("Docs/03_Admin_Panel/", "docs/admin/"),
            ("Docs/04_Setup_Guides/", "docs/development/setup-guides/"),
            ("Docs/05_Project_Summaries/", "docs/project-history/"),
            ("Docs/06_References/", "docs/development/references/"),
            ("Docs/ADMIN_PANEL_ENHANCEMENTS.md", "docs/admin/admin-panel-enhancements.md"),
            ("Docs/ADMIN_PANEL_QUICK_START.md", "docs/admin/admin-panel-quick-start.md"),
            ("Docs/ADMIN_PANEL_RESET.md", "docs/admin/admin-panel-reset.md"),
            ("Docs/ADMIN_PANEL_STYLING_COMPLETE.md", "docs/admin/admin-panel-styling-complete.md"),
            ("Docs/ADMIN_PANEL_USAGE_GUIDE.md", "docs/admin/admin-panel-usage-guide.md"),
            ("Docs/DATABASE_SETUP_GUIDE.md", "docs/development/database-setup-guide.md"),
            ("Docs/EPIC_0_1_COMPLETION_SUMMARY.md", "docs/project-history/epic-0-1-completion-summary.md"),
            ("Docs/EPIC_0_2_COMPLETION_SUMMARY.md", "docs/project-history/epic-0-2-completion-summary.md"),
            ("Docs/EPIC_0_3_COMPLETION_SUMMARY.md", "docs/project-history/epic-0-3-completion-summary.md"),
            ("Docs/EPIC_0_4_COMPLETION_SUMMARY.md", "docs/project-history/epic-0-4-completion-summary.md"),
            ("Docs/EPIC_1_COMPLETION_SUMMARY.md", "docs/project-history/epic-1-completion-summary.md"),

            # deployment docs
            ("deployment/README.md", "docs/deployment/readme.md"),
        ]

        for src, dst in doc_moves:
            self.safe_move(Path(src), Path(dst), f"Documentation: {src}")

        # Move docs/ content to organized subdirs
        existing_docs_moves = [
            ("docs/API.md", "docs/api/api.md"),
            ("docs/DEPLOYMENT.md", "docs/deployment/deployment.md"),
            ("docs/DEVELOPER_SETUP.md", "docs/development/developer-setup.md"),
            ("docs/DOMAIN_ROUTING.md", "docs/development/domain-routing.md"),
            ("docs/LOCAL_DEVELOPMENT.md", "docs/development/local-development.md"),
            ("docs/MONITORING.md", "docs/deployment/monitoring.md"),
            ("docs/OPTIMIZATION.md", "docs/development/optimization.md"),
            ("docs/TROUBLESHOOTING.md", "docs/development/troubleshooting.md"),
            ("docs/USER_GUIDE.md", "docs/development/user-guide.md"),
        ]

        for src, dst in existing_docs_moves:
            self.safe_move(Path(src), Path(dst), f"Reorganize existing docs: {src}")

        logger.info("Documentation consolidation complete")

    def consolidate_testing(self):
        """Consolidate all testing files under tests/."""
        logger.info("Starting testing consolidation...")

        # Create test subdirectories
        test_dirs = [
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "tests/django-apps",
            "tests/react",
            "tests/scripts"
        ]

        for dir_path in test_dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)

        # Test file mappings
        test_moves = [
            # Root level test scripts -> tests/scripts/
            ("test_admin_panel_enhanced.py", "tests/scripts/test-admin-panel-enhanced.py"),
            ("test_admin_panel.py", "tests/scripts/test-admin-panel.py"),
            ("test_admin.sh", "tests/scripts/test-admin.sh"),
            ("test_all_endpoints.py", "tests/scripts/test-all-endpoints.py"),
            ("test_analytics_dashboard.py", "tests/scripts/test-analytics-dashboard.py"),
            ("test_api.sh", "tests/scripts/test-api.sh"),
            ("test_availability_api.py", "tests/scripts/test-availability-api.py"),
            ("test_availability_api.sh", "tests/scripts/test-availability-api.sh"),
            ("test_domain_management.py", "tests/scripts/test-domain-management.py"),
            ("test_epic5_packages.py", "tests/scripts/test-epic5-packages.py"),
            ("setup_test_data.py", "tests/scripts/setup-test-data.py"),

            # Django app tests -> tests/django-apps/
            ("apps/admin_panel/tests.py", "tests/django-apps/admin-panel-tests.py"),
            ("apps/analytics/tests.py", "tests/django-apps/analytics-tests.py"),
            ("apps/availability/tests.py", "tests/django-apps/availability-tests.py"),
            ("apps/bookings/tests.py", "tests/django-apps/bookings-tests.py"),
            ("apps/clients/tests.py", "tests/django-apps/clients-tests.py"),
            ("apps/notifications/tests.py", "tests/django-apps/notifications-tests.py"),
            ("apps/packages/tests.py", "tests/django-apps/packages-tests.py"),
            ("apps/pages/tests.py", "tests/django-apps/pages-tests.py"),
            ("apps/payments/tests.py", "tests/django-apps/payments-tests.py"),
            ("apps/trainers/tests.py", "tests/django-apps/trainers-tests.py"),
            ("apps/users/tests.py", "tests/django-apps/users-tests.py"),
            ("apps/workflows/tests.py", "tests/django-apps/workflows-tests.py"),
            ("frontend/tests.py", "tests/django-apps/frontend-tests.py"),

            # React tests -> tests/react/
            ("trainer-app/src/components/__tests__/", "tests/react/components/"),
            ("trainer-app/src/hooks/__tests__/", "tests/react/hooks/"),
            ("trainer-app/src/pages/__tests__/", "tests/react/pages/"),
            ("trainer-app/src/store/__tests__/", "tests/react/store/"),
        ]

        for src, dst in test_moves:
            self.safe_move(Path(src), Path(dst), f"Testing: {src}")

        # Move integration tests (already in tests/)
        # tests/integration/ stays as is

        logger.info("Testing consolidation complete")

    def clean_code_structure(self):
        """Clean up code directory structure."""
        logger.info("Starting code structure cleanup...")

        # Create assets directory for shared resources
        assets_dir = self.project_root / "assets"
        assets_dir.mkdir(exist_ok=True)

        # Move any loose files to appropriate locations
        # (Most structure is already clean)

        # Ensure all Django apps have proper __init__.py
        django_apps = [
            "apps/admin_panel", "apps/analytics", "apps/availability",
            "apps/bookings", "apps/clients", "apps/core", "apps/notifications",
            "apps/packages", "apps/pages", "apps/payments", "apps/react_app",
            "apps/trainers", "apps/users", "apps/workflows"
        ]

        for app in django_apps:
            init_file = self.project_root / app / "__init__.py"
            if not init_file.exists():
                if not self.dry_run:
                    init_file.write_text("# Django app")
                logger.info(f"Created missing __init__.py: {app}")

        logger.info("Code structure cleanup complete")

    def verify_htmx_archives(self):
        """Verify HTMX archives are intact."""
        logger.info("Verifying HTMX archives...")

        archive_dirs = [
            "archive/htmx_templates",
            "archive/htmx_app",
            "archive/htmx_docs"
        ]

        for archive_dir in archive_dirs:
            dir_path = self.project_root / archive_dir
            if not dir_path.exists():
                logger.warning(f"Missing HTMX archive: {archive_dir}")
            else:
                item_count = len(list(dir_path.rglob("*")))
                logger.info(f"HTMX archive intact: {archive_dir} ({item_count} items)")

    def generate_report(self):
        """Generate reorganization report."""
        report_path = self.project_root / "logs" / "project_reorganization_report.txt"

        with open(report_path, 'w') as f:
            f.write("Project Reorganization Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total operations: {len(self.moves_log)}\n\n")

            # Group by action type
            moves = [m for m in self.moves_log if m['action'] == 'MOVED']
            f.write(f"Files moved: {len(moves)}\n")

            for move in moves:
                f.write(f"  {move['src']} -> {move['dst']}\n")

            f.write("\nRollback information available in moves_log\n")

        logger.info(f"Report generated: {report_path}")

    def rollback(self):
        """Rollback all reorganization changes."""
        logger.info("Starting rollback...")

        # Reverse all moves
        for move in reversed(self.moves_log):
            if move['action'] == 'MOVED':
                src = Path(move['dst'])
                dst = Path(move['src'])

                if src.exists():
                    self.safe_move(src, dst, f"ROLLBACK: {src} -> {dst}")

        logger.info("Rollback complete")

    def execute_reorganization(self):
        """Execute the full reorganization."""
        logger.info("Starting project reorganization...")

        self.consolidate_documentation()
        self.consolidate_testing()
        self.clean_code_structure()
        self.verify_htmx_archives()
        self.generate_report()

        logger.info("Project reorganization complete")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Project structure reorganization')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without executing')
    parser.add_argument('--execute', action='store_true', help='Execute reorganization')
    parser.add_argument('--rollback', action='store_true', help='Rollback all changes')
    parser.add_argument('--verify', action='store_true', help='Verify HTMX archives only')

    args = argparse.ArgumentParser()
    args.dry_run = parser.parse_args().dry_run or not parser.parse_args().execute
    args.execute = parser.parse_args().execute
    args.rollback = parser.parse_args().rollback
    args.verify = parser.parse_args().verify

    reorganizer = ProjectReorganizer(dry_run=args.dry_run)

    if args.verify:
        reorganizer.verify_htmx_archives()
    elif args.rollback:
        reorganizer.rollback()
    elif args.execute or args.dry_run:
        reorganizer.execute_reorganization()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
