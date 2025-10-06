#!/usr/bin/env python3
"""
Test script to validate complete legacy system deprecation and new template-based system integration
This test ensures that:
1. All legacy modular generators are properly archived
2. Steve Glen's default content is preserved and accessible 
3. New template-based system works with extracted content
4. Application runs without legacy dependencies
"""

import os
import json
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegacyDeprecationTester:
    def __init__(self):
        self.test_results = {}
        self.passed_tests = 0
        self.total_tests = 0
        
    def run_all_tests(self):
        """Run all deprecation validation tests"""
        print("=== Legacy System Deprecation Validation ===\n")
        
        # Test 1: Verify legacy files are archived
        self.test_legacy_files_archived()
        
        # Test 2: Verify legacy files are removed from modules
        self.test_legacy_files_removed()
        
        # Test 3: Verify Steve Glen default content is preserved
        self.test_steve_glen_content_preserved()
        
        # Test 4: Verify new template system works with extracted content
        self.test_template_system_integration()
        
        # Test 5: Verify application runs without legacy dependencies
        self.test_application_runs()
        
        # Test 6: Verify webhook endpoints updated
        self.test_webhook_endpoints_updated()
        
        # Test 7: Verify test data is accessible
        self.test_template_test_data()
        
        self.print_summary()
        
    def test_legacy_files_archived(self):
        """Test 1: Verify legacy files are properly archived"""
        print("Test 1: Verifying legacy files are archived...")
        self.total_tests += 1
        
        try:
            expected_files = [
                'archived_files/resume_generator.py',
                'archived_files/cover_letter_generator.py', 
                'archived_files/base_generator.py',
                'archived_files/makecom-document-generator.py'
            ]
            
            missing_files = []
            for file_path in expected_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                print(f"❌ Missing archived files: {missing_files}")
                self.test_results['test_1'] = {'status': 'FAIL', 'message': f'Missing files: {missing_files}'}
            else:
                print("✅ All legacy files properly archived")
                self.test_results['test_1'] = {'status': 'PASS', 'message': 'All legacy files archived'}
                self.passed_tests += 1
                
        except Exception as e:
            print(f"❌ Error checking archived files: {e}")
            self.test_results['test_1'] = {'status': 'FAIL', 'message': f'Error: {e}'}
    
    def test_legacy_files_removed(self):
        """Test 2: Verify legacy files are removed from modules directory"""
        print("\nTest 2: Verifying legacy files removed from modules...")
        self.total_tests += 1
        
        try:
            legacy_files_in_modules = [
                'modules/resume_generator.py',
                'modules/cover_letter_generator.py',
                'modules/base_generator.py'
            ]
            
            existing_files = []
            for file_path in legacy_files_in_modules:
                if os.path.exists(file_path):
                    existing_files.append(file_path)
            
            if existing_files:
                print(f"❌ Legacy files still exist in modules: {existing_files}")
                self.test_results['test_2'] = {'status': 'FAIL', 'message': f'Files not removed: {existing_files}'}
            else:
                print("✅ Legacy files successfully removed from modules")
                self.test_results['test_2'] = {'status': 'PASS', 'message': 'Legacy files removed'}
                self.passed_tests += 1
                
        except Exception as e:
            print(f"❌ Error checking modules directory: {e}")
            self.test_results['test_2'] = {'status': 'FAIL', 'message': f'Error: {e}'}
    
    def test_steve_glen_content_preserved(self):
        """Test 3: Verify Steve Glen's default content is preserved"""
        print("\nTest 3: Verifying Steve Glen's content preservation...")
        self.total_tests += 1
        
        try:
            # Check comprehensive defaults file
            comprehensive_file = 'steve_glen_comprehensive_defaults.json'
            if not os.path.exists(comprehensive_file):
                print(f"❌ Comprehensive defaults file missing: {comprehensive_file}")
                self.test_results['test_3'] = {'status': 'FAIL', 'message': 'Comprehensive defaults missing'}
                return
            
            # Load and validate content
            with open(comprehensive_file, 'r') as f:
                defaults = json.load(f)
            
            required_sections = ['resume_data', 'cover_letter_data', 'template_variable_mappings', 'generation_notes']
            missing_sections = []
            
            for section in required_sections:
                if section not in defaults:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"❌ Missing sections in defaults: {missing_sections}")
                self.test_results['test_3'] = {'status': 'FAIL', 'message': f'Missing sections: {missing_sections}'}
            else:
                # Verify specific Steve Glen content
                resume_data = defaults['resume_data']
                if (resume_data['personal']['first_name'] == 'Steve' and 
                    resume_data['personal']['last_name'] == 'Glen' and
                    'Odvod Media' in str(resume_data['experience'])):
                    print("✅ Steve Glen's content successfully preserved")
                    self.test_results['test_3'] = {'status': 'PASS', 'message': 'Content preserved'}
                    self.passed_tests += 1
                else:
                    print("❌ Steve Glen content not properly preserved")
                    self.test_results['test_3'] = {'status': 'FAIL', 'message': 'Content corrupted'}
                    
        except Exception as e:
            print(f"❌ Error validating preserved content: {e}")
            self.test_results['test_3'] = {'status': 'FAIL', 'message': f'Error: {e}'}
    
    def test_template_system_integration(self):
        """Test 4: Verify new template system works with extracted content"""
        print("\nTest 4: Verifying template system integration...")
        self.total_tests += 1
        
        try:
            # Check if template library tests still pass
            import subprocess
            result = subprocess.run(['python', 'content_template_library/document_generator_tests.py'], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0 and "11/11 tests passed" in result.stdout:
                print("✅ Template system integration successful")
                self.test_results['test_4'] = {'status': 'PASS', 'message': 'Template system works'}
                self.passed_tests += 1
            else:
                print("❌ Template system integration failed")
                print(f"Output: {result.stdout}")
                print(f"Error: {result.stderr}")
                self.test_results['test_4'] = {'status': 'FAIL', 'message': 'Template tests failed'}
                
        except Exception as e:
            print(f"❌ Error testing template integration: {e}")
            self.test_results['test_4'] = {'status': 'FAIL', 'message': f'Error: {e}'}
    
    def test_application_runs(self):
        """Test 5: Verify application runs without legacy dependencies"""
        print("\nTest 5: Verifying application runs without legacy dependencies...")
        self.total_tests += 1
        
        try:
            # Test import of main application components
            sys.path.append('.')
            from document_generator import DocumentGenerator
            from modules.webhook_handler import webhook_bp
            
            # Test instantiation
            generator = DocumentGenerator()
            
            print("✅ Application runs successfully without legacy dependencies")
            self.test_results['test_5'] = {'status': 'PASS', 'message': 'Application runs'}
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Error running application: {e}")
            self.test_results['test_5'] = {'status': 'FAIL', 'message': f'Error: {e}'}
    
    def test_webhook_endpoints_updated(self):
        """Test 6: Verify webhook endpoints are updated to use new system"""
        print("\nTest 6: Verifying webhook endpoints updated...")
        self.total_tests += 1
        
        try:
            # Check webhook handler file for new DocumentGenerator usage
            with open('modules/webhook_handler.py', 'r') as f:
                webhook_content = f.read()
            
            if ('from document_generator import DocumentGenerator' in webhook_content and 
                'document_generator.generate_document' in webhook_content and
                'Legacy generators have been deprecated' in webhook_content):
                print("✅ Webhook endpoints successfully updated")
                self.test_results['test_6'] = {'status': 'PASS', 'message': 'Webhooks updated'}
                self.passed_tests += 1
            else:
                print("❌ Webhook endpoints not properly updated")
                self.test_results['test_6'] = {'status': 'FAIL', 'message': 'Webhooks not updated'}
                
        except Exception as e:
            print(f"❌ Error checking webhook updates: {e}")
            self.test_results['test_6'] = {'status': 'FAIL', 'message': f'Error: {e}'}
    
    def test_template_test_data(self):
        """Test 7: Verify template test data is accessible"""
        print("\nTest 7: Verifying template test data accessibility...")
        self.total_tests += 1
        
        try:
            test_data_files = [
                'content_template_library/test_data/steve_glen_resume_template_data.json',
                'content_template_library/test_data/steve_glen_cover_letter_template_data.json'
            ]
            
            missing_files = []
            for file_path in test_data_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                print(f"❌ Missing test data files: {missing_files}")
                self.test_results['test_7'] = {'status': 'FAIL', 'message': f'Missing files: {missing_files}'}
            else:
                # Verify content
                with open(test_data_files[0], 'r') as f:
                    resume_test_data = json.load(f)
                
                if (resume_test_data['first_name'] == 'Steve' and 
                    resume_test_data['last_name'] == 'Glen'):
                    print("✅ Template test data accessible and valid")
                    self.test_results['test_7'] = {'status': 'PASS', 'message': 'Test data accessible'}
                    self.passed_tests += 1
                else:
                    print("❌ Template test data corrupted")
                    self.test_results['test_7'] = {'status': 'FAIL', 'message': 'Test data corrupted'}
                    
        except Exception as e:
            print(f"❌ Error checking test data: {e}")
            self.test_results['test_7'] = {'status': 'FAIL', 'message': f'Error: {e}'}
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("LEGACY DEPRECATION TEST SUMMARY")
        print(f"{'='*60}")
        
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{status_icon} {test_name}: {result['message']}")
        
        print(f"\nOverall: {self.passed_tests}/{self.total_tests} tests passed")
        
        if self.passed_tests == self.total_tests:
            print("🎉 Legacy system deprecation completed successfully!")
            print("\nDeprecation Summary:")
            print("• Legacy modular generators archived in archived_files/")
            print("• Steve Glen's default content preserved in comprehensive backup")
            print("• Template-based system fully integrated and tested")
            print("• Application runs without legacy dependencies")
            print("• Webhook endpoints updated to use new template system")
            print("• Test data available for ongoing development")
        else:
            print("⚠️  Some deprecation tasks need attention")
            
        return self.passed_tests == self.total_tests

def main():
    """Run legacy deprecation validation tests"""
    tester = LegacyDeprecationTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n📝 Documentation updates recommended:")
        print("• Update replit.md with deprecation completion date")
        print("• Note transition from modular to template-based system")
        print("• Update system architecture documentation")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)