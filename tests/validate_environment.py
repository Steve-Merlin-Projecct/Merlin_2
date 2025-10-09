#!/usr/bin/env python3
"""
Environment Variable Validation Script

Validates all required and optional environment variables for the
Automated Job Application System.

Usage:
    python tests/validate_environment.py
"""

import os
import sys
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class EnvironmentValidator:
    def __init__(self):
        self.results = []
        self.critical_failures = 0
        self.warnings = 0

    def validate_required(self, var_name: str, min_length: int = 0, description: str = "") -> bool:
        """Validate a required environment variable"""
        value = os.getenv(var_name)

        if not value:
            self.results.append({
                'var': var_name,
                'status': 'ERROR',
                'message': f'Missing required variable',
                'description': description
            })
            self.critical_failures += 1
            return False

        if value in ['your_secret_key_here', 'your_secure_api_key_here',
                     'your_database_password_here', 'your_gemini_api_key_here',
                     'your_apify_token_here']:
            self.results.append({
                'var': var_name,
                'status': 'ERROR',
                'message': f'Placeholder value not replaced',
                'description': description
            })
            self.critical_failures += 1
            return False

        if min_length > 0 and len(value) < min_length:
            self.results.append({
                'var': var_name,
                'status': 'WARNING',
                'message': f'Too short (min: {min_length}, actual: {len(value)})',
                'description': description
            })
            self.warnings += 1
            return True

        self.results.append({
            'var': var_name,
            'status': 'OK',
            'message': f'Set ({len(value)} chars)',
            'description': description
        })
        return True

    def validate_optional(self, var_name: str, description: str = "") -> bool:
        """Validate an optional environment variable"""
        value = os.getenv(var_name)

        if not value or value.startswith('your_'):
            self.results.append({
                'var': var_name,
                'status': 'INFO',
                'message': 'Not set (optional)',
                'description': description
            })
            return False

        self.results.append({
            'var': var_name,
            'status': 'OK',
            'message': f'Set ({len(value)} chars)',
            'description': description
        })
        return True

    def validate_database_config(self) -> bool:
        """Validate database configuration"""
        print("Validating Database Configuration...")
        print("-" * 70)

        # Check individual parameters
        self.validate_required('PGPASSWORD', min_length=8,
                             description='PostgreSQL password')
        self.validate_required('DATABASE_PASSWORD', min_length=8,
                             description='Database password (alias for PGPASSWORD)')
        self.validate_required('DATABASE_NAME',
                             description='Database name')
        self.validate_required('DATABASE_HOST',
                             description='Database host')
        self.validate_required('DATABASE_PORT',
                             description='Database port')
        self.validate_required('DATABASE_USER',
                             description='Database user')

        # Check DATABASE_URL (optional but recommended)
        self.validate_optional('DATABASE_URL',
                             description='Full connection string (recommended)')

        print()
        return self.critical_failures == 0

    def validate_security_config(self) -> bool:
        """Validate security configuration"""
        print("Validating Security Configuration...")
        print("-" * 70)

        self.validate_required('SESSION_SECRET', min_length=32,
                             description='Flask session encryption key')
        self.validate_required('SECRET_KEY', min_length=32,
                             description='Application secret key')
        self.validate_required('WEBHOOK_API_KEY', min_length=32,
                             description='API authentication key')

        print()
        return self.critical_failures == 0

    def validate_external_services(self) -> bool:
        """Validate external service configuration"""
        print("Validating External Services...")
        print("-" * 70)

        # Critical for AI features
        self.validate_optional('GEMINI_API_KEY',
                             description='Google Gemini AI API key')

        # Optional services
        self.validate_optional('APIFY_API_TOKEN',
                             description='Apify job scraping token')
        self.validate_optional('LINK_TRACKING_API_KEY',
                             description='Link tracking API key')

        print()
        return True

    def validate_storage_config(self) -> bool:
        """Validate storage configuration"""
        print("Validating Storage Configuration...")
        print("-" * 70)

        storage_backend = os.getenv('STORAGE_BACKEND', 'local')
        self.results.append({
            'var': 'STORAGE_BACKEND',
            'status': 'OK',
            'message': f'Set to: {storage_backend}',
            'description': 'Storage backend type'
        })

        if storage_backend == 'local':
            self.validate_optional('LOCAL_STORAGE_PATH',
                                 description='Local storage path')

        print()
        return True

    def print_results(self):
        """Print validation results"""
        for result in self.results:
            status_symbol = {
                'OK': '✅',
                'WARNING': '⚠️',
                'ERROR': '❌',
                'INFO': 'ℹ️'
            }.get(result['status'], '•')

            print(f"{status_symbol} {result['var']:30} {result['message']:40} {result['description']}")

    def generate_report(self) -> bool:
        """Generate final validation report"""
        print("\n" + "=" * 70)
        print("ENVIRONMENT VALIDATION SUMMARY")
        print("=" * 70)

        total = len([r for r in self.results if r['status'] in ['OK', 'ERROR', 'WARNING']])
        ok_count = len([r for r in self.results if r['status'] == 'OK'])

        print(f"Total Variables Checked: {total}")
        print(f"Valid: {ok_count}")
        print(f"Warnings: {self.warnings}")
        print(f"Critical Failures: {self.critical_failures}")
        print()

        if self.critical_failures > 0:
            print("❌ VALIDATION FAILED")
            print(f"   {self.critical_failures} critical issue(s) must be fixed")
            print()
            print("Action Required:")
            for result in self.results:
                if result['status'] == 'ERROR':
                    print(f"   • Set {result['var']}: {result['description']}")
            return False
        elif self.warnings > 0:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
            print(f"   {self.warnings} warning(s) should be addressed")
            print()
            print("Recommendations:")
            for result in self.results:
                if result['status'] == 'WARNING':
                    print(f"   • {result['var']}: {result['message']}")
            return True
        else:
            print("✅ VALIDATION PASSED")
            print("   All environment variables are properly configured")
            return True

def main():
    """Main validation function"""
    print("=" * 70)
    print("ENVIRONMENT VARIABLE VALIDATION")
    print("=" * 70)
    print()

    validator = EnvironmentValidator()

    # Run all validations
    validator.validate_database_config()
    validator.validate_security_config()
    validator.validate_external_services()
    validator.validate_storage_config()

    # Print results
    print("Validation Results:")
    print("-" * 70)
    validator.print_results()
    print()

    # Generate report
    success = validator.generate_report()

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
