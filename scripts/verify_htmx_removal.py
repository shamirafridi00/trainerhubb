#!/usr/bin/env python
"""
HTMX Removal Verification Script

Automated verification for each removal phase.
Tests React functionality, Django integrity, and HTMX legacy status.

Usage:
    python scripts/verify_htmx_removal.py --phase=1
    python scripts/verify_htmx_removal.py --phase=2 --react-url=http://localhost:3000
"""

import os
import sys
import requests
import subprocess
import time
from pathlib import Path

class HTMXRemovalVerifier:
    """Verifies HTMX removal phases and React functionality."""

    def __init__(self, react_url="http://localhost:3000", django_port=8000):
        self.react_url = react_url.rstrip('/')
        self.django_url = f"http://localhost:{django_port}"
        self.project_root = Path(__file__).parent.parent
        self.results = []

    def log_result(self, test_name, status, details=""):
        """Log verification result."""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.results.append(result)

        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")

    def run_command(self, cmd, cwd=None):
        """Run shell command and return result."""
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=cwd or self.project_root,
                capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def verify_django_integrity(self):
        """Verify Django settings and migrations."""
        # Test Django check
        success, stdout, stderr = self.run_command("python manage.py check")
        if success:
            self.log_result("Django Check", "PASS", "No configuration errors")
        else:
            self.log_result("Django Check", "FAIL", f"Errors: {stderr}")

        # Test migrations
        success, stdout, stderr = self.run_command("python manage.py showmigrations")
        if success and "[ ]" not in stdout:
            self.log_result("Django Migrations", "PASS", "No pending migrations")
        else:
            self.log_result("Django Migrations", "FAIL", "Pending migrations found")

    def verify_react_functionality(self):
        """Verify React app loads and key pages work."""
        try:
            # Test main React app load
            response = requests.get(self.react_url, timeout=10)
            if response.status_code == 200:
                self.log_result("React App Load", "PASS", f"Status: {response.status_code}")
            else:
                self.log_result("React App Load", "FAIL", f"Status: {response.status_code}")

            # Test key React pages (these would need to be customized based on actual routes)
            react_pages = [
                '/',
                '/clients',
                '/bookings',
                '/packages',
                '/settings'
            ]

            for page in react_pages:
                try:
                    response = requests.get(f"{self.react_url}{page}", timeout=5)
                    if response.status_code == 200:
                        self.log_result(f"React Page: {page}", "PASS")
                    else:
                        self.log_result(f"React Page: {page}", "WARN", f"Status: {response.status_code}")
                except requests.RequestException as e:
                    self.log_result(f"React Page: {page}", "FAIL", str(e))

        except requests.RequestException as e:
            self.log_result("React Connectivity", "FAIL", f"Cannot reach React app: {e}")

    def verify_htmx_legacy_status(self, expected_removed=False):
        """Verify HTMX legacy status based on phase."""
        # Test HTMX routes (should fail if removed)
        htmx_routes = [
            '/dashboard/',
            '/clients/',
            '/bookings/',
            '/packages/',
            '/settings/'
        ]

        for route in htmx_routes:
            try:
                response = requests.get(f"{self.django_url}{route}", timeout=5)
                if expected_removed:
                    if response.status_code == 404:
                        self.log_result(f"HTMX Route {route}", "PASS", "Correctly removed (404)")
                    else:
                        self.log_result(f"HTMX Route {route}", "FAIL", f"Still accessible: {response.status_code}")
                else:
                    # During early phases, routes should still work
                    if response.status_code in [200, 302]:
                        self.log_result(f"HTMX Route {route}", "PASS", f"Still accessible: {response.status_code}")
                    else:
                        self.log_result(f"HTMX Route {route}", "WARN", f"Unexpected status: {response.status_code}")
            except requests.RequestException as e:
                self.log_result(f"HTMX Route {route}", "ERROR", str(e))

    def verify_phase_1(self):
        """Verify Phase 1 completion."""
        self.log_result("Phase 1 Verification", "INFO", "Infrastructure cleanup verification")

        # Check empty templatetags removed
        templatetags_path = self.project_root / "apps" / "frontend_legacy" / "templatetags"
        if not templatetags_path.exists():
            self.log_result("Empty Template Tags", "PASS", "Directory removed")
        else:
            self.log_result("Empty Template Tags", "FAIL", "Directory still exists")

        self.verify_django_integrity()

    def verify_phase_2(self):
        """Verify Phase 2 completion."""
        self.log_result("Phase 2 Verification", "INFO", "Template removal verification")

        # Check templates/legacy removed
        legacy_templates_path = self.project_root / "templates" / "legacy"
        if not legacy_templates_path.exists():
            self.log_result("Legacy Templates", "PASS", "Directory removed")
        else:
            self.log_result("Legacy Templates", "FAIL", "Directory still exists")

        self.verify_django_integrity()
        self.verify_react_functionality()
        self.verify_htmx_legacy_status(expected_removed=True)

    def verify_phase_3(self):
        """Verify Phase 3 completion."""
        self.log_result("Phase 3 Verification", "INFO", "Complete app removal verification")

        # Check apps/frontend_legacy removed
        legacy_app_path = self.project_root / "apps" / "frontend_legacy"
        if not legacy_app_path.exists():
            self.log_result("Legacy App Directory", "PASS", "Directory removed")
        else:
            self.log_result("Legacy App Directory", "FAIL", "Directory still exists")

        # Check apps/frontend shim removed
        shim_path = self.project_root / "apps" / "frontend"
        if not shim_path.exists():
            self.log_result("Compatibility Shim", "PASS", "Directory removed")
        else:
            self.log_result("Compatibility Shim", "FAIL", "Directory still exists")

        self.verify_django_integrity()
        self.verify_react_functionality()
        self.verify_htmx_legacy_status(expected_removed=True)

    def run_verification(self, phase):
        """Run verification for specified phase."""
        print(f"\n🔍 HTMX Removal Phase {phase} Verification")
        print("=" * 50)

        if phase == 1:
            self.verify_phase_1()
        elif phase == 2:
            self.verify_phase_2()
        elif phase == 3:
            self.verify_phase_3()

        # Summary
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        warnings = sum(1 for r in self.results if r['status'] == 'WARN')

        print("
📊 Verification Summary:"        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⚠️  Warnings: {warnings}")

        return failed == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Verify HTMX removal phases')
    parser.add_argument('--phase', type=int, required=True, choices=[1, 2, 3])
    parser.add_argument('--react-url', default='http://localhost:3000')
    parser.add_argument('--django-port', type=int, default=8000)

    args = parser.parse_args()

    verifier = HTMXRemovalVerifier(args.react_url, args.django_port)
    success = verifier.run_verification(args.phase)

    sys.exit(0 if success else 1)
