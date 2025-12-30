#!/usr/bin/env python
"""
Project Reorganization Rollback Script

Reverses all project structure reorganization changes using logged operations.
Safe and automated rollback process.

Usage:
    python scripts/rollback_reorganization.py --execute
    python scripts/rollback_reorganization.py --dry-run
"""

import os
import shutil
import json
from pathlib import Path

class ReorganizationRollback:
    """Manages rollback of project reorganization."""

    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent
        self.log_file = self.project_root / "logs" / "project_reorganization.log"

    def parse_log_entries(self):
        """Parse the reorganization log to extract move operations."""
        moves = []

        if not self.log_file.exists():
            print("No reorganization log found. Nothing to rollback.")
            return moves

        with open(self.log_file, 'r') as f:
            for line in f:
                if 'MOVED:' in line:
                    # Extract source and destination from log line
                    # Format: timestamp - level - MOVED: src -> dst
                    parts = line.split('MOVED: ')
                    if len(parts) > 1:
                        move_part = parts[1].strip()
                        if ' -> ' in move_part:
                            src, dst = move_part.split(' -> ')
                            moves.append({
                                'src': dst.strip(),
                                'dst': src.strip()
                            })

        return moves

    def safe_move(self, src: Path, dst: Path, description: str) -> bool:
        """Safely move file/directory with logging."""
        src_full = self.project_root / src
        dst_full = self.project_root / dst

        if not src_full.exists():
            print(f"Source does not exist: {src_full}")
            return False

        if self.dry_run:
            print(f"[DRY RUN] Would move: {src_full} -> {dst_full}")
            return True

        try:
            dst_full.parent.mkdir(parents=True, exist_ok=True)

            if src_full.is_file():
                shutil.move(str(src_full), str(dst_full))
            else:
                # For directories
                if dst_full.exists():
                    for item in src_full.iterdir():
                        shutil.move(str(item), str(dst_full))
                    src_full.rmdir()
                else:
                    shutil.move(str(src_full), str(dst_full))

            print(f"✅ ROLLBACK: {description}")
            return True
        except Exception as e:
            print(f"❌ Failed to rollback {src} -> {dst}: {e}")
            return False

    def rollback_moves(self):
        """Rollback all move operations in reverse order."""
        moves = self.parse_log_entries()

        if not moves:
            print("No moves to rollback.")
            return

        print(f"Found {len(moves)} moves to rollback...")

        # Reverse the moves (destination becomes source, source becomes destination)
        for move in reversed(moves):
            src_path = Path(move['src'])
            dst_path = Path(move['dst'])

            description = f"Rollback: {src_path} -> {dst_path}"
            self.safe_move(src_path, dst_path, description)

    def rollback_created_directories(self):
        """Remove directories created during reorganization."""
        dirs_to_remove = [
            "docs/migration",
            "docs/api",
            "docs/deployment",
            "docs/development",
            "docs/admin",
            "docs/project-history",
            "tests/unit",
            "tests/e2e",
            "tests/django-apps",
            "tests/react",
            "tests/scripts",
            "assets"
        ]

        for dir_path in dirs_to_remove:
            full_path = self.project_root / dir_path
            if full_path.exists() and not any(full_path.iterdir()):
                # Only remove if empty
                if not self.dry_run:
                    full_path.rmdir()
                print(f"{'[DRY RUN]' if self.dry_run else '✅'} Removed empty directory: {dir_path}")

    def execute_rollback(self):
        """Execute the complete rollback process."""
        print("🔄 Starting Project Reorganization Rollback")
        print("=" * 50)

        self.rollback_moves()
        self.rollback_created_directories()

        print("\n" + "=" * 50)
        print("🔄 Project reorganization rollback complete")
        print("\nNext steps:")
        print("1. Verify Django: python manage.py check")
        print("2. Verify React: cd trainer-app && npm run build")
        print("3. Check for any missing files manually")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Project reorganization rollback')
    parser.add_argument('--dry-run', action='store_true', help='Preview rollback without executing')
    parser.add_argument('--execute', action='store_true', help='Execute rollback')

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        args.dry_run = True  # Default to dry-run

    rollback = ReorganizationRollback(dry_run=args.dry_run)
    rollback.execute_rollback()
