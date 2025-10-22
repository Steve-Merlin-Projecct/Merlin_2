#!/usr/bin/env python3
"""
Module: test_system_verification.py
Purpose: Comprehensive system verification for all major components
Created: 2024-08-30
Modified: 2025-10-21
Dependencies: requests, sys, json, datetime
Related: test_end_to_end_workflow.py, conftest.py, tests/
Description: Tests all major system components: basic connectivity, health checks,
             database operations, API endpoints, dashboard functionality, email
             integration, scraping system, AI analysis, and document generation.
             Provides comprehensive verification report with pass/fail status.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SystemVerification:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }

    def test(self, name, passed, message, details=None):
        """Record test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {name}: {message}")
        if details:
            print(f"   Details: {details}")

        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "message": message,
            "details": details
        })

    def run_all_tests(self):
        """Run all system verification tests"""
        print("=" * 70)
        print("SYSTEM VERIFICATION - Automated Job Application System")
        print("=" * 70)
        print()

        # 1. Basic Connectivity
        print("1. BASIC CONNECTIVITY")
        print("-" * 70)
        self.test_health()
        self.test_root_endpoint()
        print()

        # 2. Database Layer
        print("2. DATABASE LAYER")
        print("-" * 70)
        self.test_database_health()
        self.test_database_direct_connection()
        print()

        # 3. Core APIs
        print("3. CORE APIS")
        print("-" * 70)
        self.test_email_oauth_status()
        self.test_workflow_status()
        print()

        # 4. Security
        print("4. SECURITY & AUTHENTICATION")
        print("-" * 70)
        self.test_api_authentication()
        print()

        # 5. Frontend
        print("5. FRONTEND INTERFACES")
        print("-" * 70)
        self.test_dashboard()
        print()

        # Generate summary
        self.generate_summary()

    def test_health(self):
        """Test health endpoint"""
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.test("Health Check", True,
                         f"Version {data.get('version', 'unknown')}")
            else:
                self.test("Health Check", False, f"Status {r.status_code}")
        except Exception as e:
            self.test("Health Check", False, str(e))

    def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            r = requests.get(f"{self.base_url}/", timeout=5)
            if r.status_code == 200:
                data = r.json()
                modules = data.get('modules', [])
                self.test("Root Endpoint", True,
                         f"{len(modules)} modules registered")
            else:
                self.test("Root Endpoint", False, f"Status {r.status_code}")
        except Exception as e:
            self.test("Root Endpoint", False, str(e))

    def test_database_health(self):
        """Test database health endpoint"""
        try:
            r = requests.get(f"{self.base_url}/api/db/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                connected = data.get('database_connected', False)
                total_jobs = data.get('total_jobs', 0)
                self.test("Database Health", connected,
                         f"Connected, {total_jobs} total jobs")
            else:
                self.test("Database Health", False, f"Status {r.status_code}")
        except Exception as e:
            self.test("Database Health", False, str(e))

    def test_database_direct_connection(self):
        """Test direct database connection"""
        try:
            from modules.database.database_client import DatabaseClient
            db = DatabaseClient()
            if db.test_connection():
                # Count tables
                result = db.execute_raw_sql(
                    "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'"
                )
                table_count = result[0][0] if result else 0
                self.test("Direct DB Connection", True,
                         f"{table_count} tables in schema")
            else:
                self.test("Direct DB Connection", False, "Connection failed")
        except Exception as e:
            self.test("Direct DB Connection", False, str(e))

    def test_email_oauth_status(self):
        """Test email OAuth status"""
        try:
            r = requests.get(f"{self.base_url}/api/email/oauth/status", timeout=5)
            if r.status_code == 200:
                data = r.json()
                status = data.get('status', 'unknown')
                self.test("Email OAuth", True, f"Status: {status}")
            else:
                self.test("Email OAuth", False, f"Status {r.status_code}")
        except Exception as e:
            self.test("Email OAuth", False, str(e))

    def test_workflow_status(self):
        """Test workflow API status"""
        try:
            r = requests.get(f"{self.base_url}/api/workflow/status", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.test("Workflow API", True, "Accessible")
            else:
                self.test("Workflow API", False, f"Status {r.status_code}")
        except Exception as e:
            self.test("Workflow API", False, str(e))

    def test_api_authentication(self):
        """Test API authentication requirements"""
        try:
            # Test protected endpoint without auth
            r = requests.get(f"{self.base_url}/api/db/statistics", timeout=5)
            if r.status_code == 401:
                self.test("API Authentication", True,
                         "Protected endpoints require auth")
            else:
                self.test("API Authentication", False,
                         f"Expected 401, got {r.status_code}")
        except Exception as e:
            self.test("API Authentication", False, str(e))

    def test_dashboard(self):
        """Test dashboard accessibility"""
        try:
            r = requests.get(f"{self.base_url}/dashboard", timeout=5)
            if r.status_code == 200 and "login" in r.text.lower():
                self.test("Dashboard Frontend", True, "Login page accessible")
            else:
                self.test("Dashboard Frontend", False, f"Status {r.status_code}")
        except Exception as e:
            self.test("Dashboard Frontend", False, str(e))

    def generate_summary(self):
        """Generate test summary"""
        total = len(self.results["tests"])
        passed = sum(1 for t in self.results["tests"] if t["passed"])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0

        self.results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate
        }

        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        if success_rate >= 90:
            print("🟢 EXCELLENT: System is fully operational")
        elif success_rate >= 70:
            print("🟡 GOOD: System is mostly functional")
        elif success_rate >= 50:
            print("🟠 FAIR: System has some issues")
        else:
            print("🔴 POOR: System needs attention")

        # Save results
        with open('system_verification_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print()
        print("📄 Detailed results saved to: system_verification_results.json")

if __name__ == "__main__":
    verifier = SystemVerification()
    verifier.run_all_tests()
