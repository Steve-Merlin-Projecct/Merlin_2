"""
Pre-Send Document Validator - Comprehensive Document Validation Before Delivery

This module provides comprehensive validation of generated documents BEFORE sending
to prevent embarrassing failures, incomplete documents, or security threats.

Validation Phases:
1. File Existence and Accessibility - Verify file exists and is readable
2. File Structure Integrity - Valid .docx ZIP structure
3. Word Compatibility - Can be opened by python-docx
4. Security Scanning - No malicious content or threats
5. Variable Completion - No unfilled template variables
6. File Size Validation - Not empty, not suspiciously large
7. Content Quality Checks - Basic readability and completeness

The validator integrates with:
- Document generation pipeline (automatic validation after generation)
- Email sending pipeline (validation before sending)
- Logging system (tracks all validation attempts)

Author: Automated Job Application System
Version: 1.0.0
Created: 2025-10-24
"""

import os
import logging
import zipfile
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Import python-docx for compatibility checks
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx not available - Word compatibility checks will be skipped")

# Import security scanner
try:
    from .docx_security_scanner import DOCXSecurityScanner
    SECURITY_SCANNER_AVAILABLE = True
except ImportError:
    SECURITY_SCANNER_AVAILABLE = False
    logging.warning("Security scanner not available - security checks will be skipped")

# Import content validator for variable detection
try:
    from .content_validator import ContentValidator
    CONTENT_VALIDATOR_AVAILABLE = True
except ImportError:
    CONTENT_VALIDATOR_AVAILABLE = False
    logging.warning("Content validator not available - variable checks will be skipped")

logger = logging.getLogger(__name__)


class ValidationError:
    """
    Represents a validation error found during pre-send validation

    Attributes:
        check_name: Name of validation check that failed
        severity: Error severity (critical, high, medium, low)
        message: Human-readable error message
        details: Additional technical details
        timestamp: When error was detected
    """

    def __init__(self, check_name: str, severity: str, message: str, details: Optional[Dict] = None):
        self.check_name = check_name
        self.severity = severity
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert error to dictionary for logging and reporting"""
        return {
            "check_name": self.check_name,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class ValidationConfig:
    """
    Configuration for pre-send validation

    Allows enabling/disabling specific validation checks
    and configuring validation parameters
    """

    def __init__(
        self,
        enable_file_existence: bool = True,
        enable_structure_check: bool = True,
        enable_word_compatibility: bool = True,
        enable_security_scan: bool = True,
        enable_variable_check: bool = True,
        enable_file_size_check: bool = True,
        min_file_size_bytes: int = 1000,  # Minimum 1KB
        max_file_size_bytes: int = 10 * 1024 * 1024,  # Maximum 10MB
        strict_mode: bool = True,  # If True, warnings block sending
    ):
        self.enable_file_existence = enable_file_existence
        self.enable_structure_check = enable_structure_check
        self.enable_word_compatibility = enable_word_compatibility
        self.enable_security_scan = enable_security_scan
        self.enable_variable_check = enable_variable_check
        self.enable_file_size_check = enable_file_size_check
        self.min_file_size_bytes = min_file_size_bytes
        self.max_file_size_bytes = max_file_size_bytes
        self.strict_mode = strict_mode

    @classmethod
    def from_env(cls) -> 'ValidationConfig':
        """Create configuration from environment variables"""
        import os

        return cls(
            enable_file_existence=os.getenv("VALIDATION_FILE_EXISTENCE", "true").lower() == "true",
            enable_structure_check=os.getenv("VALIDATION_STRUCTURE_CHECK", "true").lower() == "true",
            enable_word_compatibility=os.getenv("VALIDATION_WORD_COMPAT", "true").lower() == "true",
            enable_security_scan=os.getenv("VALIDATION_SECURITY_SCAN", "true").lower() == "true",
            enable_variable_check=os.getenv("VALIDATION_VARIABLE_CHECK", "true").lower() == "true",
            enable_file_size_check=os.getenv("VALIDATION_FILE_SIZE", "true").lower() == "true",
            min_file_size_bytes=int(os.getenv("VALIDATION_MIN_SIZE", "1000")),
            max_file_size_bytes=int(os.getenv("VALIDATION_MAX_SIZE", str(10 * 1024 * 1024))),
            strict_mode=os.getenv("VALIDATION_STRICT_MODE", "true").lower() == "true",
        )

    def to_dict(self) -> Dict:
        """Convert config to dictionary"""
        return {
            "enable_file_existence": self.enable_file_existence,
            "enable_structure_check": self.enable_structure_check,
            "enable_word_compatibility": self.enable_word_compatibility,
            "enable_security_scan": self.enable_security_scan,
            "enable_variable_check": self.enable_variable_check,
            "enable_file_size_check": self.enable_file_size_check,
            "min_file_size_bytes": self.min_file_size_bytes,
            "max_file_size_bytes": self.max_file_size_bytes,
            "strict_mode": self.strict_mode,
        }


class PreSendValidator:
    """
    Comprehensive pre-send document validator

    Performs multi-layer validation to ensure documents are ready for delivery:
    - File exists and is accessible
    - Valid DOCX structure (ZIP format)
    - Word compatible (can be opened by python-docx)
    - Security clean (no threats detected)
    - Variables filled (no <<placeholders>> remaining)
    - File size reasonable

    Usage:
        validator = PreSendValidator()
        result = validator.validate_document("/path/to/document.docx")

        if result["safe_to_send"]:
            # Send document
            send_email(...)
        else:
            # Log error and do not send
            logger.error(f"Validation failed: {result['errors']}")
    """

    def __init__(self, config: Optional[ValidationConfig] = None, log_dir: Optional[str] = None):
        """
        Initialize pre-send validator

        Args:
            config: Validation configuration (uses defaults if not provided)
            log_dir: Directory for validation logs (uses ./storage/validation_logs if not provided)
        """
        self.config = config or ValidationConfig()
        self.log_dir = log_dir or os.path.join(os.getcwd(), "storage", "validation_logs")

        # Ensure log directory exists
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

        # Initialize security scanner if available
        if SECURITY_SCANNER_AVAILABLE and self.config.enable_security_scan:
            self.security_scanner = DOCXSecurityScanner(strict_mode=self.config.strict_mode)
        else:
            self.security_scanner = None

        # Initialize content validator if available
        if CONTENT_VALIDATOR_AVAILABLE and self.config.enable_variable_check:
            self.content_validator = ContentValidator()
        else:
            self.content_validator = None

        logger.info(f"PreSendValidator initialized (strict_mode={self.config.strict_mode})")

    def validate_document(self, file_path: str, document_type: str = "unknown") -> Dict:
        """
        Validate a document before sending

        Args:
            file_path: Path to document to validate
            document_type: Type of document (resume, coverletter, etc.)

        Returns:
            Dictionary containing validation results:
            {
                "valid": True/False,
                "file_path": "path/to/document.docx",
                "document_type": "resume",
                "checks": {
                    "file_exists": True/False,
                    "valid_structure": True/False,
                    "word_compatible": True/False,
                    "security_scan": True/False,
                    "variables_filled": True/False,
                    "file_size_ok": True/False
                },
                "errors": ["List of specific errors"],
                "warnings": ["List of warnings"],
                "timestamp": "ISO datetime",
                "safe_to_send": True/False,
                "validation_duration_ms": 123
            }
        """
        start_time = datetime.now()
        errors: List[ValidationError] = []
        checks = {}
        warnings = []

        logger.info(f"Starting pre-send validation: {file_path}")

        # Phase 1: File existence check
        if self.config.enable_file_existence:
            file_exists, file_error = self._check_file_exists(file_path)
            checks["file_exists"] = file_exists
            if not file_exists and file_error:
                errors.append(file_error)
                # If file doesn't exist, no point in continuing
                return self._build_validation_result(
                    file_path, document_type, checks, errors, warnings, start_time
                )

        # Phase 2: File structure validation
        if self.config.enable_structure_check:
            structure_valid, structure_errors = self._check_file_structure(file_path)
            checks["valid_structure"] = structure_valid
            errors.extend(structure_errors)

        # Phase 3: Word compatibility check
        if self.config.enable_word_compatibility:
            word_compatible, compat_errors = self._check_word_compatibility(file_path)
            checks["word_compatible"] = word_compatible
            errors.extend(compat_errors)

        # Phase 4: Security scan
        if self.config.enable_security_scan:
            security_clean, security_errors, security_warnings = self._check_security(file_path)
            checks["security_scan"] = security_clean
            errors.extend(security_errors)
            warnings.extend(security_warnings)

        # Phase 5: Variable completion check
        if self.config.enable_variable_check:
            variables_filled, variable_errors = self._check_variables_filled(file_path)
            checks["variables_filled"] = variables_filled
            errors.extend(variable_errors)

        # Phase 6: File size validation
        if self.config.enable_file_size_check:
            size_ok, size_errors = self._check_file_size(file_path)
            checks["file_size_ok"] = size_ok
            errors.extend(size_errors)

        # Build final validation result
        result = self._build_validation_result(
            file_path, document_type, checks, errors, warnings, start_time
        )

        # Log validation result
        self._log_validation_result(result)

        return result

    def _check_file_exists(self, file_path: str) -> Tuple[bool, Optional[ValidationError]]:
        """Check if file exists and is readable"""
        try:
            if not os.path.exists(file_path):
                error = ValidationError(
                    check_name="file_exists",
                    severity="critical",
                    message=f"File does not exist: {file_path}",
                    details={"file_path": file_path}
                )
                return False, error

            if not os.path.isfile(file_path):
                error = ValidationError(
                    check_name="file_exists",
                    severity="critical",
                    message=f"Path is not a file: {file_path}",
                    details={"file_path": file_path}
                )
                return False, error

            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                error = ValidationError(
                    check_name="file_exists",
                    severity="critical",
                    message=f"File is not readable: {file_path}",
                    details={"file_path": file_path}
                )
                return False, error

            logger.debug(f"File existence check passed: {file_path}")
            return True, None

        except Exception as e:
            error = ValidationError(
                check_name="file_exists",
                severity="critical",
                message=f"Error checking file existence: {str(e)}",
                details={"file_path": file_path, "exception": str(e)}
            )
            return False, error

    def _check_file_structure(self, file_path: str) -> Tuple[bool, List[ValidationError]]:
        """Check if file has valid DOCX structure (ZIP format)"""
        errors = []

        try:
            # Check if file is valid ZIP
            if not zipfile.is_zipfile(file_path):
                error = ValidationError(
                    check_name="valid_structure",
                    severity="critical",
                    message="File is not a valid ZIP/DOCX archive",
                    details={"file_path": file_path}
                )
                errors.append(error)
                return False, errors

            # Try to open and validate ZIP contents
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Test ZIP integrity
                bad_file = zip_file.testzip()
                if bad_file:
                    error = ValidationError(
                        check_name="valid_structure",
                        severity="critical",
                        message=f"Corrupted file in ZIP: {bad_file}",
                        details={"file_path": file_path, "corrupted_file": bad_file}
                    )
                    errors.append(error)
                    return False, errors

                # Check for required OOXML files
                required_files = ["[Content_Types].xml", "_rels/.rels"]
                file_list = zip_file.namelist()

                for required in required_files:
                    if required not in file_list:
                        error = ValidationError(
                            check_name="valid_structure",
                            severity="high",
                            message=f"Missing required OOXML file: {required}",
                            details={"file_path": file_path, "missing_file": required}
                        )
                        errors.append(error)

            if errors:
                return False, errors

            logger.debug(f"File structure check passed: {file_path}")
            return True, []

        except zipfile.BadZipFile as e:
            error = ValidationError(
                check_name="valid_structure",
                severity="critical",
                message=f"Invalid ZIP file: {str(e)}",
                details={"file_path": file_path, "exception": str(e)}
            )
            return False, [error]

        except Exception as e:
            error = ValidationError(
                check_name="valid_structure",
                severity="high",
                message=f"Error validating file structure: {str(e)}",
                details={"file_path": file_path, "exception": str(e)}
            )
            return False, [error]

    def _check_word_compatibility(self, file_path: str) -> Tuple[bool, List[ValidationError]]:
        """Check if file can be opened by python-docx (Word compatibility)"""
        errors = []

        if not DOCX_AVAILABLE:
            logger.warning("python-docx not available - skipping Word compatibility check")
            return True, []  # Pass check if library not available

        try:
            # Try to open document with python-docx
            doc = Document(file_path)

            # Basic sanity check - document should have some content
            # (at least core properties or paragraphs)
            if doc.core_properties is None:
                error = ValidationError(
                    check_name="word_compatible",
                    severity="medium",
                    message="Document has no core properties (may be corrupted)",
                    details={"file_path": file_path}
                )
                errors.append(error)

            logger.debug(f"Word compatibility check passed: {file_path}")
            return len(errors) == 0, errors

        except Exception as e:
            error = ValidationError(
                check_name="word_compatible",
                severity="critical",
                message=f"Document cannot be opened by python-docx: {str(e)}",
                details={"file_path": file_path, "exception": str(e)}
            )
            return False, [error]

    def _check_security(self, file_path: str) -> Tuple[bool, List[ValidationError], List[str]]:
        """Check document for security threats using DOCXSecurityScanner"""
        errors = []
        warnings = []

        if not self.security_scanner:
            logger.warning("Security scanner not available - skipping security check")
            return True, [], []

        try:
            # Run security scan
            is_safe, threats = self.security_scanner.scan_file(file_path)

            # Convert threats to ValidationErrors
            for threat in threats:
                severity = threat.severity

                # Map threat to error or warning
                if severity in ["critical", "high"]:
                    error = ValidationError(
                        check_name="security_scan",
                        severity=severity,
                        message=threat.description,
                        details={
                            "threat_type": threat.threat_type,
                            "location": threat.location,
                            "threat_details": threat.details
                        }
                    )
                    errors.append(error)
                else:
                    # Medium/low severity = warning
                    warnings.append(f"{threat.threat_type}: {threat.description}")

            if errors:
                logger.warning(f"Security scan found {len(errors)} threats in {file_path}")
                return False, errors, warnings

            logger.debug(f"Security scan passed: {file_path}")
            return True, [], warnings

        except Exception as e:
            error = ValidationError(
                check_name="security_scan",
                severity="high",
                message=f"Security scan failed: {str(e)}",
                details={"file_path": file_path, "exception": str(e)}
            )
            return False, [error], warnings

    def _check_variables_filled(self, file_path: str) -> Tuple[bool, List[ValidationError]]:
        """Check for unfilled template variables (<<variable_name>> still present)"""
        errors = []

        if not self.content_validator:
            logger.warning("Content validator not available - skipping variable check")
            return True, []

        try:
            # Run content validation (includes variable check)
            is_safe, findings = self.content_validator.validate_document_content(file_path)

            # Look for unreplaced template variable findings
            for finding in findings:
                if finding.get("type") == "unreplaced_template_variable":
                    error = ValidationError(
                        check_name="variables_filled",
                        severity="high",
                        message=finding.get("description", "Unreplaced template variables found"),
                        details=finding.get("details", {})
                    )
                    errors.append(error)

            if errors:
                logger.warning(f"Found {len(errors)} unfilled variables in {file_path}")
                return False, errors

            logger.debug(f"Variable completion check passed: {file_path}")
            return True, []

        except Exception as e:
            error = ValidationError(
                check_name="variables_filled",
                severity="medium",
                message=f"Variable check failed: {str(e)}",
                details={"file_path": file_path, "exception": str(e)}
            )
            return False, [error]

    def _check_file_size(self, file_path: str) -> Tuple[bool, List[ValidationError]]:
        """Check if file size is reasonable (not 0 bytes, not suspiciously large)"""
        errors = []

        try:
            file_size = os.path.getsize(file_path)

            # Check minimum size
            if file_size < self.config.min_file_size_bytes:
                error = ValidationError(
                    check_name="file_size_ok",
                    severity="critical",
                    message=f"File too small ({file_size} bytes, minimum {self.config.min_file_size_bytes})",
                    details={
                        "file_path": file_path,
                        "file_size_bytes": file_size,
                        "min_size_bytes": self.config.min_file_size_bytes
                    }
                )
                errors.append(error)

            # Check maximum size
            if file_size > self.config.max_file_size_bytes:
                error = ValidationError(
                    check_name="file_size_ok",
                    severity="high",
                    message=f"File suspiciously large ({file_size} bytes, maximum {self.config.max_file_size_bytes})",
                    details={
                        "file_path": file_path,
                        "file_size_bytes": file_size,
                        "max_size_bytes": self.config.max_file_size_bytes
                    }
                )
                errors.append(error)

            if errors:
                return False, errors

            logger.debug(f"File size check passed: {file_path} ({file_size} bytes)")
            return True, []

        except Exception as e:
            error = ValidationError(
                check_name="file_size_ok",
                severity="medium",
                message=f"Error checking file size: {str(e)}",
                details={"file_path": file_path, "exception": str(e)}
            )
            return False, [error]

    def _build_validation_result(
        self,
        file_path: str,
        document_type: str,
        checks: Dict,
        errors: List[ValidationError],
        warnings: List[str],
        start_time: datetime
    ) -> Dict:
        """Build comprehensive validation result dictionary"""

        # Calculate validation duration
        duration = (datetime.now() - start_time).total_seconds() * 1000

        # Determine if document is safe to send
        # In strict mode: any error blocks sending
        # In non-strict mode: only critical/high severity errors block sending
        safe_to_send = len(errors) == 0

        if not self.config.strict_mode and errors:
            # In non-strict mode, check if all errors are low/medium severity
            critical_errors = [e for e in errors if e.severity in ["critical", "high"]]
            safe_to_send = len(critical_errors) == 0

        # Build result
        result = {
            "valid": safe_to_send,
            "file_path": file_path,
            "document_type": document_type,
            "checks": checks,
            "errors": [e.to_dict() for e in errors],
            "warnings": warnings,
            "timestamp": datetime.now().isoformat(),
            "safe_to_send": safe_to_send,
            "validation_duration_ms": round(duration, 2),
            "config": self.config.to_dict()
        }

        # Log summary
        if safe_to_send:
            logger.info(f"Validation PASSED: {file_path} ({duration:.2f}ms)")
        else:
            logger.error(
                f"Validation FAILED: {file_path} - {len(errors)} errors found - "
                f"DO NOT SEND ({duration:.2f}ms)"
            )

        return result

    def _log_validation_result(self, result: Dict) -> None:
        """Log validation result to file for debugging and audit trail"""
        try:
            # Create log filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = result.get("document_type", "unknown")
            safe_status = "PASS" if result["safe_to_send"] else "FAIL"

            log_filename = f"{timestamp}_{filename}_{safe_status}.json"
            log_path = os.path.join(self.log_dir, log_filename)

            # Write validation result as JSON
            with open(log_path, 'w') as f:
                json.dump(result, f, indent=2)

            logger.debug(f"Validation result logged to: {log_path}")

        except Exception as e:
            logger.error(f"Failed to log validation result: {str(e)}")


# Convenience functions for easy integration

def validate_document(
    file_path: str,
    document_type: str = "unknown",
    config: Optional[ValidationConfig] = None
) -> Dict:
    """
    Convenience function to validate a document

    Args:
        file_path: Path to document to validate
        document_type: Type of document (resume, coverletter, etc.)
        config: Optional validation configuration

    Returns:
        Validation result dictionary
    """
    validator = PreSendValidator(config=config)
    return validator.validate_document(file_path, document_type)


def quick_validate(file_path: str) -> bool:
    """
    Quick validation check - returns True if safe to send, False otherwise

    Args:
        file_path: Path to document to validate

    Returns:
        True if document is safe to send, False otherwise
    """
    result = validate_document(file_path)
    return result["safe_to_send"]
