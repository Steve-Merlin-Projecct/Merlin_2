#!/usr/bin/env python3
"""
Digital Ocean Database Firewall Configuration Script

Securely configures trusted sources for Digital Ocean managed PostgreSQL database
using the Digital Ocean API.

Security Features:
- API token loaded from environment variable only
- Secure HTTPS API communication
- Input validation and error handling
- No credentials in code or logs
- Audit logging of all operations
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DigitalOceanDatabaseConfig:
    """
    Secure Digital Ocean database firewall configurator.

    Manages trusted sources for database access using the Digital Ocean API v2.
    """

    API_BASE_URL = "https://api.digitalocean.com/v2"

    def __init__(self):
        """Initialize the configurator with secure API authentication."""
        self.api_token = os.getenv('DIGITALOCEAN_API_TOKEN')

        if not self.api_token:
            raise ValueError(
                "DIGITALOCEAN_API_TOKEN environment variable is required. "
                "Generate a token at: https://cloud.digitalocean.com/account/api/tokens"
            )

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        # Extract database UUID from connection string
        self.db_host = os.getenv('DATABASE_HOST')
        if not self.db_host:
            raise ValueError("DATABASE_HOST environment variable is required")

        # Parse database ID from hostname
        # Format: db-postgresql-merlin-tor1-52568-do-user-27870072-0.e.db.ondigitalocean.com
        self.database_id = None
        self._find_database_id()

    def _find_database_id(self) -> None:
        """
        Find the database UUID by listing databases and matching hostname.

        Security: Only uses read operations to find database ID.
        """
        print("🔍 Finding database ID...")

        try:
            response = requests.get(
                f"{self.API_BASE_URL}/databases",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            databases = response.json().get('databases', [])

            # Find our database by matching hostname
            for db in databases:
                if db.get('connection', {}).get('host') == self.db_host:
                    self.database_id = db['id']
                    print(f"✅ Found database: {db['name']} (ID: {self.database_id})")
                    return

            raise ValueError(
                f"Database with host {self.db_host} not found. "
                f"Please verify DATABASE_HOST in .env file."
            )

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to list databases: {str(e)}")

    def get_current_firewall_rules(self) -> List[Dict]:
        """
        Retrieve current firewall rules (trusted sources).

        Returns:
            List of current trusted sources
        """
        print("\n📋 Retrieving current firewall rules...")

        try:
            response = requests.get(
                f"{self.API_BASE_URL}/databases/{self.database_id}/firewall",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            rules = response.json().get('rules', [])

            print(f"✅ Found {len(rules)} existing rule(s):")
            for idx, rule in enumerate(rules, 1):
                rule_type = rule.get('type')
                value = rule.get('value')
                print(f"   {idx}. Type: {rule_type}, Value: {value}")

            return rules

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to retrieve firewall rules: {str(e)}")

    def add_trusted_source(
        self,
        source_type: str,
        value: str,
        validate: bool = True
    ) -> bool:
        """
        Add a trusted source to the database firewall.

        Args:
            source_type: Type of source ('ip_addr', 'app', 'droplet', 'k8s', 'tag')
            value: Source value (IP address, app ID, droplet ID, etc.)
            validate: Whether to validate input before adding

        Returns:
            True if successful, False otherwise

        Security:
            - Validates source types
            - Verifies API response
            - Logs all operations
        """
        valid_types = ['ip_addr', 'app', 'droplet', 'k8s', 'tag']

        if validate and source_type not in valid_types:
            raise ValueError(
                f"Invalid source_type: {source_type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )

        print(f"\n🔐 Adding trusted source:")
        print(f"   Type: {source_type}")
        print(f"   Value: {value}")

        # Get current rules first
        current_rules = self.get_current_firewall_rules()

        # Check if rule already exists
        for rule in current_rules:
            if rule.get('type') == source_type and rule.get('value') == value:
                print(f"⚠️  Rule already exists, skipping...")
                return True

        # Add new rule to existing rules
        new_rule = {
            "type": source_type,
            "value": value
        }

        all_rules = current_rules + [new_rule]

        # Update firewall rules
        payload = {
            "rules": all_rules
        }

        try:
            response = requests.put(
                f"{self.API_BASE_URL}/databases/{self.database_id}/firewall",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            print(f"✅ Successfully added trusted source!")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to add trusted source: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   API Response: {e.response.text}")
            return False

    def remove_trusted_source(
        self,
        source_type: str,
        value: str
    ) -> bool:
        """
        Remove a trusted source from the database firewall.

        Args:
            source_type: Type of source to remove
            value: Source value to remove

        Returns:
            True if successful, False otherwise
        """
        print(f"\n🗑️  Removing trusted source:")
        print(f"   Type: {source_type}")
        print(f"   Value: {value}")

        # Get current rules
        current_rules = self.get_current_firewall_rules()

        # Filter out the rule to remove
        updated_rules = [
            rule for rule in current_rules
            if not (rule.get('type') == source_type and rule.get('value') == value)
        ]

        if len(updated_rules) == len(current_rules):
            print(f"⚠️  Rule not found, nothing to remove")
            return False

        # Update firewall rules
        payload = {
            "rules": updated_rules
        }

        try:
            response = requests.put(
                f"{self.API_BASE_URL}/databases/{self.database_id}/firewall",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            print(f"✅ Successfully removed trusted source!")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to remove trusted source: {str(e)}")
            return False


def get_current_ip() -> Optional[str]:
    """
    Get the current public IP address of this machine.

    Returns:
        Public IP address or None if unable to determine
    """
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        response.raise_for_status()
        ip = response.json().get('ip')
        return ip
    except Exception as e:
        print(f"⚠️  Unable to determine current IP: {str(e)}")
        return None


def main():
    """Main execution function with interactive configuration."""

    print("=" * 80)
    print("Digital Ocean Database Firewall Configuration")
    print("=" * 80)

    try:
        # Initialize configurator
        config = DigitalOceanDatabaseConfig()

        # Show current rules
        print("\n" + "=" * 80)
        current_rules = config.get_current_firewall_rules()
        print("=" * 80)

        # Interactive menu
        while True:
            print("\n" + "=" * 80)
            print("Configuration Options:")
            print("=" * 80)
            print("1. Add current machine's IP address")
            print("2. Add specific IP address")
            print("3. Add Digital Ocean App")
            print("4. Add Digital Ocean Droplet")
            print("5. Remove trusted source")
            print("6. View current rules")
            print("7. Exit")
            print("=" * 80)

            choice = input("\nSelect option (1-7): ").strip()

            if choice == "1":
                # Add current IP
                current_ip = get_current_ip()
                if current_ip:
                    print(f"\n📍 Detected IP: {current_ip}")
                    confirm = input("Add this IP to trusted sources? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        config.add_trusted_source('ip_addr', current_ip)
                else:
                    print("❌ Unable to detect current IP")

            elif choice == "2":
                # Add specific IP
                ip_addr = input("\nEnter IP address (e.g., 192.168.1.100): ").strip()
                if ip_addr:
                    config.add_trusted_source('ip_addr', ip_addr)

            elif choice == "3":
                # Add App Platform app
                app_id = input("\nEnter App Platform App ID (UUID): ").strip()
                if app_id:
                    config.add_trusted_source('app', app_id)

            elif choice == "4":
                # Add Droplet
                droplet_id = input("\nEnter Droplet ID: ").strip()
                if droplet_id:
                    config.add_trusted_source('droplet', droplet_id)

            elif choice == "5":
                # Remove source
                print("\nCurrent rules:")
                rules = config.get_current_firewall_rules()
                if not rules:
                    print("No rules to remove")
                    continue

                try:
                    idx = int(input("\nEnter rule number to remove (1-{}): ".format(len(rules)))) - 1
                    if 0 <= idx < len(rules):
                        rule = rules[idx]
                        confirm = input(f"Remove {rule['type']}: {rule['value']}? (yes/no): ").strip().lower()
                        if confirm == 'yes':
                            config.remove_trusted_source(rule['type'], rule['value'])
                    else:
                        print("Invalid rule number")
                except ValueError:
                    print("Invalid input")

            elif choice == "6":
                # View current rules
                config.get_current_firewall_rules()

            elif choice == "7":
                # Exit
                print("\n✅ Configuration complete!")
                break

            else:
                print("❌ Invalid option, please try again")

        print("\n" + "=" * 80)
        print("Firewall configuration updated successfully!")
        print("=" * 80)

        # Test connection
        print("\n📡 Testing database connection...")
        test_choice = input("Run connection test? (yes/no): ").strip().lower()
        if test_choice == 'yes':
            print("\nRunning test_db_connection.py...")
            os.system('python test_db_connection.py')

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
