#!/usr/bin/env python3
"""Quick script to check current firewall configuration."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the configurator
from configure_do_firewall import DigitalOceanDatabaseConfig

try:
    print("Initializing Digital Ocean API connection...\n")
    config = DigitalOceanDatabaseConfig()

    print("\nCurrent Firewall Configuration:")
    print("=" * 80)
    rules = config.get_current_firewall_rules()
    print("=" * 80)

    if not rules:
        print("\n⚠️  No trusted sources configured - database is currently inaccessible!")
        print("You need to add at least one trusted source to connect to the database.")

except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)
