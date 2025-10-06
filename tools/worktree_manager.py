#!/usr/bin/env python3
"""
Git Worktree Manager
A lightweight tool for managing git worktrees in the project

Usage:
    python tools/worktree_manager.py create <name> [--type feature|bugfix|hotfix|experimental]
    python tools/worktree_manager.py list
    python tools/worktree_manager.py remove <name>
    python tools/worktree_manager.py sync <name>
    python tools/worktree_manager.py cleanup
    python tools/worktree_manager.py status
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import json


class WorktreeManager:
    def __init__(self, project_root=None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.worktree_base = self.project_root / ".trees"
        self.config_file = self.project_root / ".claude" / "worktree-config.json"

        # Ensure .trees directory exists
        self.worktree_base.mkdir(exist_ok=True)

        # Load or create config
        self.config = self.load_config()

    def load_config(self):
        """Load worktree configuration"""
        default_config = {
            "worktree_base_dir": ".trees",
            "branch_prefix": {
                "feature": "feature/",
                "bugfix": "bugfix/",
                "hotfix": "hotfix/",
                "experimental": "experimental/"
            },
            "naming_convention": "kebab-case",
            "auto_create_prd": True,
            "prd_location": "tasks/",
            "created_worktrees": {}
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**default_config, **config}
            except Exception as e:
                print(f"⚠️ Error loading config: {e}")
                return default_config

        return default_config

    def save_config(self):
        """Save worktree configuration"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving config: {e}")

    def run_command(self, command, capture_output=True):
        """Run a shell command"""
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                return result.returncode == 0, result.stdout, result.stderr
            else:
                result = subprocess.run(command, shell=True, cwd=self.project_root)
                return result.returncode == 0, "", ""
        except Exception as e:
            return False, "", str(e)

    def create_worktree(self, name, worktree_type="feature"):
        """Create a new worktree"""
        # Normalize name to kebab-case
        normalized_name = name.lower().replace("_", "-").replace(" ", "-")

        # Get branch prefix
        branch_prefix = self.config["branch_prefix"].get(worktree_type, "feature/")
        branch_name = f"{branch_prefix}{normalized_name}"

        # Worktree path
        worktree_path = self.worktree_base / normalized_name

        # Check if worktree already exists
        if worktree_path.exists():
            print(f"❌ Worktree already exists: {worktree_path}")
            return False

        # Check if branch already exists
        success, output, _ = self.run_command(f"git branch --list {branch_name}")
        if branch_name in output:
            print(f"⚠️ Branch already exists: {branch_name}")
            response = input("Delete existing branch and continue? (y/N): ")
            if response.lower() != 'y':
                return False
            self.run_command(f"git branch -D {branch_name}")

        print(f"📁 Creating worktree: {normalized_name}")
        print(f"🌿 Branch: {branch_name}")
        print(f"📂 Path: {worktree_path}")

        # Create worktree
        success, output, error = self.run_command(
            f"git worktree add {worktree_path} -b {branch_name}",
            capture_output=False
        )

        if not success:
            print(f"❌ Failed to create worktree: {error}")
            return False

        # Track in config
        self.config["created_worktrees"][normalized_name] = {
            "branch": branch_name,
            "path": str(worktree_path),
            "type": worktree_type,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        self.save_config()

        # Create PRD if configured
        if self.config.get("auto_create_prd", False):
            prd_file = worktree_path / self.config["prd_location"] / f"prd-{normalized_name}.md"
            if not prd_file.parent.exists():
                print(f"⚠️ PRD location not found in worktree, skipping PRD creation")
            else:
                self.create_prd_stub(prd_file, normalized_name, worktree_type)

        print(f"✅ Worktree created successfully!")
        print(f"\nTo start working:")
        print(f"  cd {worktree_path}")

        return True

    def create_prd_stub(self, prd_file, name, worktree_type):
        """Create a PRD stub for the worktree"""
        prd_content = f"""# PRD: {name.replace('-', ' ').title()}

## Introduction/Overview

[Describe the feature and the problem it solves]

## Goals

1. [Primary goal]
2. [Secondary goal]

## User Stories

1. **As a [user type]**, I want to [action], so that [benefit].

## Functional Requirements

### 1. [Requirement Category]
1.1. [Specific requirement]

## Non-Goals (Out of Scope)

1. [What this feature will NOT include]

## Design Considerations

[Link to mockups or describe UI/UX requirements]

## Technical Considerations

[Known technical constraints or dependencies]

## Success Metrics

[How will success be measured?]

## Open Questions

1. [Remaining questions]

---

**Document Version:** 1.0
**Created:** {datetime.now().strftime("%Y-%m-%d")}
**Type:** {worktree_type}
**Status:** Draft
"""
        try:
            prd_file.write_text(prd_content, encoding='utf-8')
            print(f"📝 Created PRD stub: {prd_file}")
        except Exception as e:
            print(f"⚠️ Failed to create PRD: {e}")

    def list_worktrees(self):
        """List all worktrees"""
        success, output, error = self.run_command("git worktree list")

        if not success:
            print(f"❌ Failed to list worktrees: {error}")
            return

        print("\n📋 Git Worktrees:")
        print("=" * 80)
        print(output)

        # Show tracked worktrees from config
        if self.config["created_worktrees"]:
            print("\n📊 Managed Worktrees:")
            print("=" * 80)
            for name, info in self.config["created_worktrees"].items():
                status_icon = "✅" if info["status"] == "active" else "🔒"
                print(f"{status_icon} {name}")
                print(f"   Branch: {info['branch']}")
                print(f"   Type: {info['type']}")
                print(f"   Created: {info['created_at']}")
                print(f"   Path: {info['path']}")
                print()

    def remove_worktree(self, name, force=False):
        """Remove a worktree"""
        worktree_path = self.worktree_base / name

        if not worktree_path.exists():
            print(f"❌ Worktree not found: {worktree_path}")
            return False

        # Check for uncommitted changes
        success, output, _ = self.run_command(
            f"git -C {worktree_path} status --porcelain"
        )

        if output.strip() and not force:
            print(f"⚠️ Worktree has uncommitted changes:")
            print(output)
            response = input("Force remove? (y/N): ")
            if response.lower() != 'y':
                return False
            force = True

        # Remove worktree
        force_flag = "--force" if force else ""
        success, output, error = self.run_command(
            f"git worktree remove {worktree_path} {force_flag}",
            capture_output=False
        )

        if not success:
            print(f"❌ Failed to remove worktree: {error}")
            return False

        # Update config
        if name in self.config["created_worktrees"]:
            self.config["created_worktrees"][name]["status"] = "removed"
            self.config["created_worktrees"][name]["removed_at"] = datetime.now().isoformat()
            self.save_config()

        print(f"✅ Worktree removed: {name}")
        return True

    def sync_worktree(self, name):
        """Sync a worktree with main branch"""
        worktree_path = self.worktree_base / name

        if not worktree_path.exists():
            print(f"❌ Worktree not found: {worktree_path}")
            return False

        print(f"🔄 Syncing worktree: {name}")

        # Fetch latest from origin
        print("  Fetching from origin...")
        success, _, error = self.run_command(f"git -C {worktree_path} fetch origin")
        if not success:
            print(f"❌ Fetch failed: {error}")
            return False

        # Rebase on origin/main
        print("  Rebasing on origin/main...")
        success, output, error = self.run_command(
            f"git -C {worktree_path} rebase origin/main",
            capture_output=False
        )

        if not success:
            print(f"⚠️ Rebase may have conflicts. Please resolve manually in worktree.")
            return False

        print(f"✅ Worktree synced successfully")
        return True

    def cleanup_worktrees(self):
        """Clean up stale worktree references"""
        print("🧹 Cleaning up stale worktree references...")

        success, output, error = self.run_command("git worktree prune -v")

        if success:
            print("✅ Cleanup complete")
            if output:
                print(output)
        else:
            print(f"❌ Cleanup failed: {error}")

    def status(self):
        """Show status of all worktrees"""
        print("\n📊 Worktree Status Report")
        print("=" * 80)

        # Count worktrees
        success, output, _ = self.run_command("git worktree list")
        worktree_count = len([line for line in output.split('\n') if line.strip()])

        print(f"Total worktrees: {worktree_count}")
        print(f"Base directory: {self.worktree_base}")
        print(f"Managed worktrees: {len([w for w in self.config['created_worktrees'].values() if w['status'] == 'active'])}")

        # Show disk usage
        if self.worktree_base.exists():
            size_cmd = f"du -sh {self.worktree_base}"
            success, output, _ = self.run_command(size_cmd)
            if success:
                print(f"Disk usage: {output.strip()}")

        print("\n")
        self.list_worktrees()


def main():
    parser = argparse.ArgumentParser(
        description="Git Worktree Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new worktree')
    create_parser.add_argument('name', help='Name of the worktree/feature')
    create_parser.add_argument(
        '--type',
        choices=['feature', 'bugfix', 'hotfix', 'experimental'],
        default='feature',
        help='Type of worktree'
    )

    # List command
    subparsers.add_parser('list', help='List all worktrees')

    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a worktree')
    remove_parser.add_argument('name', help='Name of the worktree to remove')
    remove_parser.add_argument('--force', action='store_true', help='Force remove even with uncommitted changes')

    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync worktree with main branch')
    sync_parser.add_argument('name', help='Name of the worktree to sync')

    # Cleanup command
    subparsers.add_parser('cleanup', help='Clean up stale worktree references')

    # Status command
    subparsers.add_parser('status', help='Show status of all worktrees')

    args = parser.parse_args()

    manager = WorktreeManager()

    if args.command == 'create':
        manager.create_worktree(args.name, args.type)
    elif args.command == 'list':
        manager.list_worktrees()
    elif args.command == 'remove':
        manager.remove_worktree(args.name, args.force)
    elif args.command == 'sync':
        manager.sync_worktree(args.name)
    elif args.command == 'cleanup':
        manager.cleanup_worktrees()
    elif args.command == 'status':
        manager.status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
