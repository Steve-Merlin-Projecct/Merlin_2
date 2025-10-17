#!/usr/bin/env python3
"""Check prompt protection status and view audit log"""

import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.ai_job_description_analysis.prompt_security_manager import (
    PromptSecurityManager,
)


def main():
    security_mgr = PromptSecurityManager()

    print("=" * 80)
    print("🔐 PROMPT PROTECTION STATUS")
    print("=" * 80)
    print()

    # Check registry
    registry_file = Path("storage/prompt_hashes.json")
    if not registry_file.exists():
        print("⚠️  No prompts registered yet!")
        print("   Run app startup to initialize protection system.")
        print()
        return

    with open(registry_file, "r") as f:
        registry = json.load(f)

    print(f"📊 Total Registered Prompts: {len(registry)}")
    print()

    # Display each prompt
    for prompt_name, info in registry.items():
        print(f"📄 {prompt_name}")
        print(f"   Hash: {info['hash'][:16]}...")
        print(f"   Registered: {info['registered_at']}")
        print(f"   Last Updated: {info['last_updated']}")
        print(f"   Updated By: {info['last_updated_by']}")
        print()

    # Check change log
    change_log_file = Path("storage/prompt_changes.jsonl")
    if change_log_file.exists():
        print("-" * 80)
        print("📝 RECENT CHANGES (Last 10):")
        print("-" * 80)
        print()

        with open(change_log_file, "r") as f:
            changes = [json.loads(line) for line in f]

        for change in changes[-10:]:
            icon = "✅" if change["change_source"] == "user" else "⚠️"
            print(f"{icon} {change['timestamp']}")
            print(f"   Prompt: {change['prompt_name']}")
            print(f"   Action: {change['action_taken']}")
            print(f"   Source: {change['change_source']}")
            print()

    print("=" * 80)


if __name__ == "__main__":
    main()
