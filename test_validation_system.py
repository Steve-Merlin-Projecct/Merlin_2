#!/usr/bin/env python3
"""
Test Pre-Send Validation System

This script tests the pre-send validation system with various scenarios
to ensure it correctly identifies valid and invalid documents.

Usage:
    python test_validation_system.py

Author: Automated Job Application System
Version: 1.0.0
Created: 2025-10-24
"""

import os
import sys
import logging
import tempfile
import zipfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.content.document_generation.pre_send_validator import (
    PreSendValidator,
    ValidationConfig,
    quick_validate
)
from modules.content.document_generation.validation_config import (
    ValidationProfiles,
    get_validation_stats
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationTestSuite:
    """Test suite for pre-send validation system"""

    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def run_all_tests(self):
        """Run all validation tests"""
        logger.info("=" * 80)
        logger.info("PRE-SEND VALIDATION SYSTEM - TEST SUITE")
        logger.info("=" * 80)

        # Test 1: Configuration tests
        self.test_configuration_loading()

        # Test 2: Validation profiles
        self.test_validation_profiles()

        # Test 3: File existence checks
        self.test_file_existence_validation()

        # Test 4: File structure validation
        self.test_file_structure_validation()

        # Test 5: File size validation
        self.test_file_size_validation()

        # Test 6: Quick validate function
        self.test_quick_validate()

        # Test 7: Validation logging
        self.test_validation_logging()

        # Print summary
        self.print_summary()

    def test_configuration_loading(self):
        """Test configuration loading from environment"""
        logger.info("\nTest 1: Configuration Loading")
        logger.info("-" * 80)

        try:
            # Test default configuration
            config = ValidationConfig()
            assert config.enable_file_existence == True
            assert config.enable_security_scan == True
            assert config.strict_mode == True
            logger.info("✓ Default configuration loaded successfully")

            # Test environment-based configuration
            os.environ["VALIDATION_STRICT_MODE"] = "false"
            config_env = ValidationConfig.from_env()
            assert config_env.strict_mode == False
            logger.info("✓ Environment-based configuration loaded successfully")

            # Reset environment
            del os.environ["VALIDATION_STRICT_MODE"]

            self.record_test("Configuration Loading", True)

        except Exception as e:
            logger.error(f"✗ Configuration loading test failed: {str(e)}")
            self.record_test("Configuration Loading", False, str(e))

    def test_validation_profiles(self):
        """Test predefined validation profiles"""
        logger.info("\nTest 2: Validation Profiles")
        logger.info("-" * 80)

        try:
            # Test production profile
            prod_profile = ValidationProfiles.get_production_profile()
            assert prod_profile["strict_mode"] == True
            assert prod_profile["enable_security_scan"] == True
            logger.info("✓ Production profile loaded successfully")

            # Test development profile
            dev_profile = ValidationProfiles.get_development_profile()
            assert dev_profile["strict_mode"] == False
            logger.info("✓ Development profile loaded successfully")

            # Test testing profile
            test_profile = ValidationProfiles.get_testing_profile()
            assert test_profile["enable_file_existence"] == True
            assert test_profile["enable_security_scan"] == False
            logger.info("✓ Testing profile loaded successfully")

            # Test get_profile method
            profile = ValidationProfiles.get_profile("production")
            assert profile["profile_name"] == "production"
            logger.info("✓ Profile retrieval by name works")

            self.record_test("Validation Profiles", True)

        except Exception as e:
            logger.error(f"✗ Validation profiles test failed: {str(e)}")
            self.record_test("Validation Profiles", False, str(e))

    def test_file_existence_validation(self):
        """Test file existence validation checks"""
        logger.info("\nTest 3: File Existence Validation")
        logger.info("-" * 80)

        try:
            config = ValidationConfig()
            validator = PreSendValidator(config=config)

            # Test 1: Non-existent file
            result = validator.validate_document("/nonexistent/file.docx", "test")
            assert result["safe_to_send"] == False
            assert result["checks"]["file_exists"] == False
            logger.info("✓ Non-existent file correctly identified")

            # Test 2: Check error details
            assert len(result["errors"]) > 0
            assert result["errors"][0]["check_name"] == "file_exists"
            logger.info("✓ Error details correctly populated")

            self.record_test("File Existence Validation", True)

        except Exception as e:
            logger.error(f"✗ File existence validation test failed: {str(e)}")
            self.record_test("File Existence Validation", False, str(e))

    def test_file_structure_validation(self):
        """Test file structure validation (ZIP format)"""
        logger.info("\nTest 4: File Structure Validation")
        logger.info("-" * 80)

        try:
            config = ValidationConfig()
            validator = PreSendValidator(config=config)

            # Create a temporary non-ZIP file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
                f.write("This is not a valid DOCX file")
                temp_file = f.name

            try:
                # Test validation
                result = validator.validate_document(temp_file, "test")
                assert result["safe_to_send"] == False
                assert result["checks"]["valid_structure"] == False
                logger.info("✓ Invalid ZIP structure correctly identified")

                # Check error details
                structure_errors = [e for e in result["errors"] if e["check_name"] == "valid_structure"]
                assert len(structure_errors) > 0
                logger.info("✓ Structure validation errors correctly reported")

            finally:
                # Cleanup
                os.unlink(temp_file)

            self.record_test("File Structure Validation", True)

        except Exception as e:
            logger.error(f"✗ File structure validation test failed: {str(e)}")
            self.record_test("File Structure Validation", False, str(e))

    def test_file_size_validation(self):
        """Test file size validation"""
        logger.info("\nTest 5: File Size Validation")
        logger.info("-" * 80)

        try:
            config = ValidationConfig(
                min_file_size_bytes=100,
                max_file_size_bytes=1000
            )
            validator = PreSendValidator(config=config)

            # Create a temporary file that's too small
            with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
                f.write("tiny")  # Less than 100 bytes
                temp_file = f.name

            try:
                # Test validation
                result = validator.validate_document(temp_file, "test")

                # File exists check should pass
                assert result["checks"]["file_exists"] == True
                logger.info("✓ File existence check passed for small file")

                # File size check should fail
                assert result["checks"]["file_size_ok"] == False
                logger.info("✓ File size check correctly failed for small file")

                # Check error details
                size_errors = [e for e in result["errors"] if e["check_name"] == "file_size_ok"]
                assert len(size_errors) > 0
                assert "too small" in size_errors[0]["message"].lower()
                logger.info("✓ File size error message is descriptive")

            finally:
                # Cleanup
                os.unlink(temp_file)

            self.record_test("File Size Validation", True)

        except Exception as e:
            logger.error(f"✗ File size validation test failed: {str(e)}")
            self.record_test("File Size Validation", False, str(e))

    def test_quick_validate(self):
        """Test quick_validate convenience function"""
        logger.info("\nTest 6: Quick Validate Function")
        logger.info("-" * 80)

        try:
            # Test with non-existent file
            result = quick_validate("/nonexistent/file.docx")
            assert result == False
            logger.info("✓ quick_validate returns False for non-existent file")

            self.record_test("Quick Validate Function", True)

        except Exception as e:
            logger.error(f"✗ Quick validate function test failed: {str(e)}")
            self.record_test("Quick Validate Function", False, str(e))

    def test_validation_logging(self):
        """Test validation logging system"""
        logger.info("\nTest 7: Validation Logging")
        logger.info("-" * 80)

        try:
            # Create temporary log directory
            with tempfile.TemporaryDirectory() as temp_log_dir:
                config = ValidationConfig()
                validator = PreSendValidator(config=config, log_dir=temp_log_dir)

                # Run a validation (will fail)
                result = validator.validate_document("/nonexistent/file.docx", "test")

                # Check if log file was created
                log_files = list(Path(temp_log_dir).glob("*.json"))
                assert len(log_files) > 0
                logger.info(f"✓ Validation log file created: {log_files[0].name}")

                # Read log file and verify contents
                import json
                with open(log_files[0], 'r') as f:
                    logged_result = json.load(f)

                assert logged_result["safe_to_send"] == False
                assert "errors" in logged_result
                logger.info("✓ Validation log contains expected data")

                # Test validation stats
                stats = get_validation_stats(temp_log_dir)
                assert stats["total_validations"] == 1
                assert stats["failed_validations"] == 1
                logger.info(f"✓ Validation stats: {stats['total_validations']} total, {stats['failed_validations']} failed")

            self.record_test("Validation Logging", True)

        except Exception as e:
            logger.error(f"✗ Validation logging test failed: {str(e)}")
            self.record_test("Validation Logging", False, str(e))

    def record_test(self, test_name: str, passed: bool, error: str = None):
        """Record test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "error": error
        })

        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)

        total = len(self.test_results)
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {self.passed} ({self.passed/total*100:.1f}%)")
        logger.info(f"Failed: {self.failed} ({self.failed/total*100:.1f}%)")

        if self.failed > 0:
            logger.info("\nFailed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    logger.info(f"  ✗ {result['test']}: {result['error']}")

        logger.info("\n" + "=" * 80)
        if self.failed == 0:
            logger.info("✓ ALL TESTS PASSED - Validation system is working correctly!")
        else:
            logger.info("✗ SOME TESTS FAILED - Review failures above")
        logger.info("=" * 80)


def main():
    """Run validation system tests"""
    suite = ValidationTestSuite()
    suite.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if suite.failed == 0 else 1)


if __name__ == "__main__":
    main()
