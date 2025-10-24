#!/usr/bin/env python3
"""
DOCX Template Validation System

Comprehensive validation system for .docx template files that checks:
1. File integrity (valid ZIP structure, required OOXML files, well-formed XML)
2. Compatibility (can be opened by python-docx/Microsoft Word)
3. Security (no malicious content, remote templates, macros, or OLE objects)
4. Template variables (properly formatted, no orphaned variables)

Usage:
    python validate_docx_templates.py                    # Validate all templates
    python validate_docx_templates.py --json             # Output JSON report
    python validate_docx_templates.py --strict           # Strict mode (fail on warnings)
    python validate_docx_templates.py --path <dir>       # Validate specific directory
    python validate_docx_templates.py --file <file.docx> # Validate single file

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import json
import argparse
import zipfile
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import xml.etree.ElementTree as ET

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Import security scanner and content validator
from modules.content.document_generation.docx_security_scanner import (
    DOCXSecurityScanner,
    SecurityThreat,
)
from modules.content.document_generation.content_validator import ContentValidator

# Try to import python-docx for compatibility testing
try:
    import docx
    from docx import Document

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("WARNING: python-docx not available. Compatibility checks will be skipped.")


class ValidationResult:
    """
    Result of a single validation check
    """

    def __init__(
        self,
        check_name: str,
        passed: bool,
        message: str = "",
        details: Optional[Dict] = None,
        severity: str = "info",
    ):
        self.check_name = check_name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.severity = severity  # critical, high, medium, low, info

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "severity": self.severity,
        }


class TemplateValidationReport:
    """
    Complete validation report for a single template file
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.timestamp = datetime.now().isoformat()
        self.results: List[ValidationResult] = []
        self.overall_status = "pending"
        self.error_message = None

    def add_result(self, result: ValidationResult):
        """Add validation result"""
        self.results.append(result)

    def compute_status(self):
        """Compute overall status based on all results"""
        if self.error_message:
            self.overall_status = "error"
            return

        # Check if any critical failures
        critical_failures = [
            r for r in self.results if not r.passed and r.severity == "critical"
        ]
        if critical_failures:
            self.overall_status = "invalid"
            return

        # Check if any high severity failures
        high_failures = [
            r for r in self.results if not r.passed and r.severity == "high"
        ]
        if high_failures:
            self.overall_status = "warning"
            return

        # Check if any medium/low failures
        other_failures = [r for r in self.results if not r.passed]
        if other_failures:
            self.overall_status = "warning"
            return

        self.overall_status = "valid"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "timestamp": self.timestamp,
            "overall_status": self.overall_status,
            "error_message": self.error_message,
            "results": [r.to_dict() for r in self.results],
        }


class DOCXTemplateValidator:
    """
    Comprehensive DOCX template validator
    """

    # Expected CSV variable pattern: <<variable_name>>
    VARIABLE_PATTERN = re.compile(r"<<([a-zA-Z0-9_\s]+)>>")

    # Malformed variable patterns (common mistakes)
    MALFORMED_PATTERNS = {
        "single_angle": re.compile(r"<([a-zA-Z0-9_\s]+)>(?!>)"),  # <var> not <<var>>
        "triple_angle": re.compile(r"<<<([a-zA-Z0-9_\s]+)>>>"),  # <<<var>>>
        "missing_closing": re.compile(r"<<([a-zA-Z0-9_\s]+)(?!>>)"),  # <<var not <<var>>
        "wrong_brackets": re.compile(r"\{\{([a-zA-Z0-9_\s]+)\}\}"),  # {{var}} jinja style
    }

    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator

        Args:
            strict_mode: If True, treat warnings as failures
        """
        self.strict_mode = strict_mode
        self.security_scanner = DOCXSecurityScanner(strict_mode=strict_mode)
        self.content_validator = ContentValidator()

    def validate_file(self, file_path: str) -> TemplateValidationReport:
        """
        Validate a single DOCX template file

        Args:
            file_path: Path to DOCX file

        Returns:
            TemplateValidationReport with all validation results
        """
        report = TemplateValidationReport(file_path)

        try:
            # Phase 1: File integrity validation
            print(f"  [1/5] Checking file integrity...")
            integrity_results = self._validate_file_integrity(file_path)
            for result in integrity_results:
                report.add_result(result)

            # If file integrity fails critically, stop here
            critical_failures = [
                r for r in integrity_results if not r.passed and r.severity == "critical"
            ]
            if critical_failures:
                report.compute_status()
                return report

            # Phase 2: Compatibility validation
            print(f"  [2/5] Checking compatibility...")
            compatibility_results = self._validate_compatibility(file_path)
            for result in compatibility_results:
                report.add_result(result)

            # Phase 3: Security validation
            print(f"  [3/5] Running security scan...")
            security_results = self._validate_security(file_path)
            for result in security_results:
                report.add_result(result)

            # Phase 4: Template variable validation
            print(f"  [4/5] Validating template variables...")
            variable_results = self._validate_template_variables(file_path)
            for result in variable_results:
                report.add_result(result)

            # Phase 5: Content validation
            print(f"  [5/5] Validating content...")
            content_results = self._validate_content(file_path)
            for result in content_results:
                report.add_result(result)

            report.compute_status()

        except Exception as e:
            report.error_message = f"Validation error: {str(e)}"
            report.overall_status = "error"

        return report

    def _validate_file_integrity(self, file_path: str) -> List[ValidationResult]:
        """
        Validate file integrity (ZIP structure, required files, XML validity)

        Args:
            file_path: Path to DOCX file

        Returns:
            List of ValidationResult objects
        """
        results = []

        # Check 1: File exists
        if not os.path.exists(file_path):
            results.append(
                ValidationResult(
                    check_name="file_exists",
                    passed=False,
                    message=f"File does not exist: {file_path}",
                    severity="critical",
                )
            )
            return results

        results.append(
            ValidationResult(
                check_name="file_exists",
                passed=True,
                message="File exists",
                severity="info",
            )
        )

        # Check 2: File is valid ZIP
        try:
            if not zipfile.is_zipfile(file_path):
                results.append(
                    ValidationResult(
                        check_name="valid_zip",
                        passed=False,
                        message="File is not a valid ZIP archive (DOCX files must be ZIP)",
                        severity="critical",
                    )
                )
                return results

            results.append(
                ValidationResult(
                    check_name="valid_zip",
                    passed=True,
                    message="File is valid ZIP archive",
                    severity="info",
                )
            )
        except Exception as e:
            results.append(
                ValidationResult(
                    check_name="valid_zip",
                    passed=False,
                    message=f"ZIP validation error: {str(e)}",
                    severity="critical",
                )
            )
            return results

        # Check 3: ZIP integrity
        try:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                bad_file = zip_file.testzip()
                if bad_file:
                    results.append(
                        ValidationResult(
                            check_name="zip_integrity",
                            passed=False,
                            message=f"Corrupted file in ZIP: {bad_file}",
                            details={"corrupted_file": bad_file},
                            severity="critical",
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            check_name="zip_integrity",
                            passed=True,
                            message="ZIP integrity check passed",
                            severity="info",
                        )
                    )
        except Exception as e:
            results.append(
                ValidationResult(
                    check_name="zip_integrity",
                    passed=False,
                    message=f"ZIP integrity check failed: {str(e)}",
                    severity="critical",
                )
            )
            return results

        # Check 4: Required OOXML structure
        try:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                required_files = [
                    "[Content_Types].xml",
                    "_rels/.rels",
                    "word/document.xml",
                ]
                file_list = zip_file.namelist()

                missing_files = [f for f in required_files if f not in file_list]

                if missing_files:
                    results.append(
                        ValidationResult(
                            check_name="ooxml_structure",
                            passed=False,
                            message=f"Missing required OOXML files: {', '.join(missing_files)}",
                            details={"missing_files": missing_files},
                            severity="critical",
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            check_name="ooxml_structure",
                            passed=True,
                            message="All required OOXML files present",
                            details={"total_files": len(file_list)},
                            severity="info",
                        )
                    )
        except Exception as e:
            results.append(
                ValidationResult(
                    check_name="ooxml_structure",
                    passed=False,
                    message=f"OOXML structure check failed: {str(e)}",
                    severity="critical",
                )
            )

        # Check 5: XML well-formedness
        try:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                xml_files = [f for f in zip_file.namelist() if f.endswith(".xml")]
                malformed_files = []

                for xml_file in xml_files:
                    try:
                        content = zip_file.read(xml_file)
                        ET.fromstring(content)
                    except ET.ParseError as e:
                        malformed_files.append(
                            {"file": xml_file, "error": str(e)}
                        )

                if malformed_files:
                    results.append(
                        ValidationResult(
                            check_name="xml_well_formed",
                            passed=False,
                            message=f"Malformed XML in {len(malformed_files)} file(s)",
                            details={"malformed_files": malformed_files},
                            severity="critical",
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            check_name="xml_well_formed",
                            passed=True,
                            message=f"All {len(xml_files)} XML files are well-formed",
                            details={"xml_file_count": len(xml_files)},
                            severity="info",
                        )
                    )
        except Exception as e:
            results.append(
                ValidationResult(
                    check_name="xml_well_formed",
                    passed=False,
                    message=f"XML validation error: {str(e)}",
                    severity="high",
                )
            )

        return results

    def _validate_compatibility(self, file_path: str) -> List[ValidationResult]:
        """
        Validate compatibility with python-docx (Microsoft Word compatibility)

        Args:
            file_path: Path to DOCX file

        Returns:
            List of ValidationResult objects
        """
        results = []

        if not DOCX_AVAILABLE:
            results.append(
                ValidationResult(
                    check_name="python_docx_available",
                    passed=False,
                    message="python-docx not installed, compatibility checks skipped",
                    severity="low",
                )
            )
            return results

        # Check 1: Can open with python-docx
        try:
            doc = Document(file_path)
            results.append(
                ValidationResult(
                    check_name="opens_in_python_docx",
                    passed=True,
                    message="Document opens successfully in python-docx",
                    severity="info",
                )
            )

            # Check 2: Can access paragraphs
            try:
                paragraph_count = len(doc.paragraphs)
                results.append(
                    ValidationResult(
                        check_name="paragraph_access",
                        passed=True,
                        message=f"Can access paragraphs ({paragraph_count} found)",
                        details={"paragraph_count": paragraph_count},
                        severity="info",
                    )
                )
            except Exception as e:
                results.append(
                    ValidationResult(
                        check_name="paragraph_access",
                        passed=False,
                        message=f"Cannot access paragraphs: {str(e)}",
                        severity="high",
                    )
                )

            # Check 3: Can access styles
            try:
                style_count = len(doc.styles)
                results.append(
                    ValidationResult(
                        check_name="style_access",
                        passed=True,
                        message=f"Can access styles ({style_count} found)",
                        details={"style_count": style_count},
                        severity="info",
                    )
                )
            except Exception as e:
                results.append(
                    ValidationResult(
                        check_name="style_access",
                        passed=False,
                        message=f"Cannot access styles: {str(e)}",
                        severity="medium",
                    )
                )

            # Check 4: Validate relationships
            try:
                with zipfile.ZipFile(file_path, "r") as zip_file:
                    rels_files = [
                        f for f in zip_file.namelist() if f.endswith(".rels")
                    ]
                    broken_refs = []

                    for rels_file in rels_files:
                        rels_content = zip_file.read(rels_file).decode(
                            "utf-8", errors="ignore"
                        )
                        root = ET.fromstring(rels_content)

                        for rel in root.findall(
                            ".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
                        ):
                            target = rel.get("Target", "")
                            target_mode = rel.get("TargetMode", "Internal")

                            # Only check internal references
                            if target_mode == "Internal":
                                # Resolve relative path
                                rels_dir = os.path.dirname(rels_file)
                                target_path = os.path.normpath(
                                    os.path.join(rels_dir, target)
                                )

                                if target_path not in zip_file.namelist():
                                    broken_refs.append(
                                        {
                                            "rels_file": rels_file,
                                            "target": target,
                                            "resolved_path": target_path,
                                        }
                                    )

                    if broken_refs:
                        results.append(
                            ValidationResult(
                                check_name="relationship_integrity",
                                passed=False,
                                message=f"Found {len(broken_refs)} broken internal reference(s)",
                                details={"broken_references": broken_refs},
                                severity="high",
                            )
                        )
                    else:
                        results.append(
                            ValidationResult(
                                check_name="relationship_integrity",
                                passed=True,
                                message="All internal relationships valid",
                                severity="info",
                            )
                        )
            except Exception as e:
                results.append(
                    ValidationResult(
                        check_name="relationship_integrity",
                        passed=False,
                        message=f"Relationship validation error: {str(e)}",
                        severity="medium",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    check_name="opens_in_python_docx",
                    passed=False,
                    message=f"Cannot open document with python-docx: {str(e)}",
                    severity="critical",
                )
            )

        return results

    def _validate_security(self, file_path: str) -> List[ValidationResult]:
        """
        Validate security using DOCXSecurityScanner

        Args:
            file_path: Path to DOCX file

        Returns:
            List of ValidationResult objects
        """
        results = []

        try:
            is_safe, threats = self.security_scanner.scan_file(file_path)

            if is_safe:
                results.append(
                    ValidationResult(
                        check_name="security_scan",
                        passed=True,
                        message="No security threats detected",
                        severity="info",
                    )
                )
            else:
                # Group threats by severity
                critical_threats = [t for t in threats if t.severity == "critical"]
                high_threats = [t for t in threats if t.severity == "high"]
                medium_threats = [t for t in threats if t.severity == "medium"]
                low_threats = [t for t in threats if t.severity == "low"]

                threat_summary = {
                    "critical": len(critical_threats),
                    "high": len(high_threats),
                    "medium": len(medium_threats),
                    "low": len(low_threats),
                }

                # Determine severity based on most severe threat
                if critical_threats:
                    severity = "critical"
                elif high_threats:
                    severity = "high"
                elif medium_threats:
                    severity = "medium"
                else:
                    severity = "low"

                results.append(
                    ValidationResult(
                        check_name="security_scan",
                        passed=False,
                        message=f"Security threats detected: {len(threats)} total",
                        details={
                            "threat_count": len(threats),
                            "by_severity": threat_summary,
                            "threats": [t.to_dict() for t in threats[:10]],  # First 10
                        },
                        severity=severity,
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    check_name="security_scan",
                    passed=False,
                    message=f"Security scan error: {str(e)}",
                    severity="high",
                )
            )

        return results

    def _validate_template_variables(self, file_path: str) -> List[ValidationResult]:
        """
        Validate template variables (<<variable_name>> format)

        Args:
            file_path: Path to DOCX file

        Returns:
            List of ValidationResult objects
        """
        results = []

        try:
            # Extract text content
            text_content = self._extract_text_from_docx(file_path)

            # Find all valid variables
            valid_variables = self.VARIABLE_PATTERN.findall(text_content)
            unique_valid = list(set(valid_variables))

            if valid_variables:
                results.append(
                    ValidationResult(
                        check_name="template_variables",
                        passed=True,
                        message=f"Found {len(unique_valid)} valid template variable(s)",
                        details={
                            "variable_count": len(unique_valid),
                            "variables": sorted(unique_valid),
                            "total_occurrences": len(valid_variables),
                        },
                        severity="info",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        check_name="template_variables",
                        passed=True,
                        message="No template variables found (static template)",
                        details={"variable_count": 0},
                        severity="info",
                    )
                )

            # Check for malformed variables
            all_malformed = {}
            for pattern_name, pattern_regex in self.MALFORMED_PATTERNS.items():
                matches = pattern_regex.findall(text_content)
                if matches:
                    all_malformed[pattern_name] = list(set(matches))

            if all_malformed:
                total_malformed = sum(len(v) for v in all_malformed.values())
                results.append(
                    ValidationResult(
                        check_name="malformed_variables",
                        passed=False,
                        message=f"Found {total_malformed} malformed variable(s)",
                        details={"malformed_variables": all_malformed},
                        severity="medium",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        check_name="malformed_variables",
                        passed=True,
                        message="No malformed variables detected",
                        severity="info",
                    )
                )

            # Check variable naming conventions
            invalid_names = []
            for var in unique_valid:
                # Check if variable contains only alphanumeric, underscore, and spaces
                if not re.match(r"^[a-zA-Z0-9_\s]+$", var):
                    invalid_names.append(var)

            if invalid_names:
                results.append(
                    ValidationResult(
                        check_name="variable_naming",
                        passed=False,
                        message=f"Found {len(invalid_names)} variable(s) with invalid characters",
                        details={"invalid_variables": invalid_names},
                        severity="low",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        check_name="variable_naming",
                        passed=True,
                        message="All variables follow naming conventions",
                        severity="info",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    check_name="template_variables",
                    passed=False,
                    message=f"Variable validation error: {str(e)}",
                    severity="medium",
                )
            )

        return results

    def _validate_content(self, file_path: str) -> List[ValidationResult]:
        """
        Validate document content using ContentValidator

        Args:
            file_path: Path to DOCX file

        Returns:
            List of ValidationResult objects
        """
        results = []

        try:
            is_safe, findings = self.content_validator.validate_document_content(
                file_path
            )

            if is_safe:
                results.append(
                    ValidationResult(
                        check_name="content_validation",
                        passed=True,
                        message="Content validation passed",
                        severity="info",
                    )
                )
            else:
                # Group findings by severity
                critical_findings = [
                    f for f in findings if f.get("severity") == "critical"
                ]
                high_findings = [f for f in findings if f.get("severity") == "high"]
                medium_findings = [
                    f for f in findings if f.get("severity") == "medium"
                ]

                # Determine severity
                if critical_findings:
                    severity = "critical"
                elif high_findings:
                    severity = "high"
                elif medium_findings:
                    severity = "medium"
                else:
                    severity = "low"

                results.append(
                    ValidationResult(
                        check_name="content_validation",
                        passed=False,
                        message=f"Content validation failed: {len(findings)} issue(s)",
                        details={"findings": findings[:10]},  # First 10
                        severity=severity,
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    check_name="content_validation",
                    passed=False,
                    message=f"Content validation error: {str(e)}",
                    severity="medium",
                )
            )

        return results

    def _extract_text_from_docx(self, file_path: str) -> str:
        """
        Extract all text content from DOCX file

        Args:
            file_path: Path to DOCX file

        Returns:
            Combined text content
        """
        text_parts = []

        try:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                # Extract from document.xml
                doc_path = "word/document.xml"
                if doc_path in zip_file.namelist():
                    doc_content = zip_file.read(doc_path).decode(
                        "utf-8", errors="ignore"
                    )
                    root = ET.fromstring(doc_content)

                    # Extract all text elements
                    for text_elem in root.iter(
                        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
                    ):
                        if text_elem.text:
                            text_parts.append(text_elem.text)

                # Also check headers and footers
                for part in ["header", "footer"]:
                    for i in range(1, 10):  # Check up to 10 headers/footers
                        part_path = f"word/{part}{i}.xml"
                        if part_path in zip_file.namelist():
                            part_content = zip_file.read(part_path).decode(
                                "utf-8", errors="ignore"
                            )
                            root = ET.fromstring(part_content)
                            for text_elem in root.iter(
                                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
                            ):
                                if text_elem.text:
                                    text_parts.append(text_elem.text)

        except Exception as e:
            print(f"Warning: Error extracting text: {str(e)}")

        return "\n".join(text_parts)


class ValidationReportGenerator:
    """
    Generate formatted validation reports
    """

    def __init__(self):
        pass

    def generate_console_report(
        self, reports: List[TemplateValidationReport], show_details: bool = False
    ) -> str:
        """
        Generate console-friendly report

        Args:
            reports: List of TemplateValidationReport objects
            show_details: Whether to show detailed results for each file

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("DOCX TEMPLATE VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Summary statistics
        total_files = len(reports)
        valid_files = len([r for r in reports if r.overall_status == "valid"])
        invalid_files = len([r for r in reports if r.overall_status == "invalid"])
        warning_files = len([r for r in reports if r.overall_status == "warning"])
        error_files = len([r for r in reports if r.overall_status == "error"])

        lines.append(f"Scanned: {total_files} file(s)")
        lines.append(f"Valid:   {valid_files} file(s) ✓")
        if warning_files > 0:
            lines.append(f"Warning: {warning_files} file(s) ⚠")
        if invalid_files > 0:
            lines.append(f"Invalid: {invalid_files} file(s) ✗")
        if error_files > 0:
            lines.append(f"Error:   {error_files} file(s) ⚠")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

        # Individual file reports
        for report in reports:
            self._add_file_report(lines, report, show_details)

        # Summary
        lines.append("")
        lines.append("=" * 80)
        lines.append("SUMMARY")
        lines.append("=" * 80)
        lines.append(f"Total files scanned: {total_files}")
        lines.append(f"Valid: {valid_files}")
        lines.append(f"Invalid: {invalid_files}")
        lines.append(f"Warnings: {warning_files}")
        lines.append(f"Errors: {error_files}")

        # Security summary
        security_threats = 0
        for report in reports:
            security_results = [
                r for r in report.results if r.check_name == "security_scan"
            ]
            for result in security_results:
                if not result.passed:
                    threat_count = result.details.get("threat_count", 0)
                    security_threats += threat_count

        if security_threats > 0:
            lines.append(f"Security threats detected: {security_threats}")
        else:
            lines.append("Security threats: 0")

        lines.append("")

        return "\n".join(lines)

    def _add_file_report(
        self, lines: List[str], report: TemplateValidationReport, show_details: bool
    ):
        """Add individual file report to lines"""

        # Status symbol
        if report.overall_status == "valid":
            status_symbol = "✓"
            status_text = "VALID"
        elif report.overall_status == "warning":
            status_symbol = "⚠"
            status_text = "WARNING"
        elif report.overall_status == "invalid":
            status_symbol = "✗"
            status_text = "INVALID"
        else:
            status_symbol = "⚠"
            status_text = "ERROR"

        lines.append(f"File: {report.file_name}")
        lines.append(f"Path: {report.file_path}")
        lines.append(f"Status: {status_symbol} {status_text}")

        if report.error_message:
            lines.append(f"Error: {report.error_message}")

        # Quick summary of checks
        passed_checks = len([r for r in report.results if r.passed])
        total_checks = len(report.results)
        lines.append(f"Checks: {passed_checks}/{total_checks} passed")

        # Show failures
        failures = [r for r in report.results if not r.passed]
        if failures:
            lines.append("")
            lines.append("  Issues found:")
            for failure in failures:
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵",
                }.get(failure.severity, "⚪")

                lines.append(
                    f"  {severity_icon} [{failure.severity.upper()}] {failure.check_name}: {failure.message}"
                )

                if show_details and failure.details:
                    for key, value in failure.details.items():
                        if isinstance(value, (list, dict)):
                            lines.append(f"      {key}: {json.dumps(value, indent=2)}")
                        else:
                            lines.append(f"      {key}: {value}")

        # Show variable count if available
        var_results = [r for r in report.results if r.check_name == "template_variables"]
        for var_result in var_results:
            if var_result.passed:
                var_count = var_result.details.get("variable_count", 0)
                if var_count > 0:
                    lines.append(f"  Variables: {var_count} found")

        lines.append("")
        lines.append("-" * 80)
        lines.append("")

    def generate_json_report(
        self, reports: List[TemplateValidationReport]
    ) -> Dict:
        """
        Generate JSON report

        Args:
            reports: List of TemplateValidationReport objects

        Returns:
            Dictionary suitable for JSON serialization
        """
        # Summary statistics
        total_files = len(reports)
        valid_files = len([r for r in reports if r.overall_status == "valid"])
        invalid_files = len([r for r in reports if r.overall_status == "invalid"])
        warning_files = len([r for r in reports if r.overall_status == "warning"])
        error_files = len([r for r in reports if r.overall_status == "error"])

        # Security summary
        security_threats = 0
        for report in reports:
            security_results = [
                r for r in report.results if r.check_name == "security_scan"
            ]
            for result in security_results:
                if not result.passed:
                    threat_count = result.details.get("threat_count", 0)
                    security_threats += threat_count

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": total_files,
                "valid": valid_files,
                "invalid": invalid_files,
                "warnings": warning_files,
                "errors": error_files,
                "security_threats": security_threats,
            },
            "reports": [r.to_dict() for r in reports],
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate DOCX template files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Validate all templates
  %(prog)s --json                       # Output JSON report
  %(prog)s --strict                     # Strict mode (warnings = failures)
  %(prog)s --path /path/to/templates    # Custom directory
  %(prog)s --file template.docx         # Single file
  %(prog)s --details                    # Show detailed results
        """,
    )

    parser.add_argument(
        "--path",
        default="content_template_library",
        help="Directory containing templates (default: content_template_library)",
    )

    parser.add_argument(
        "--file",
        help="Validate a single file instead of directory",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON report instead of console format",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: treat warnings as failures",
    )

    parser.add_argument(
        "--details",
        action="store_true",
        help="Show detailed results for each check",
    )

    parser.add_argument(
        "--output",
        help="Write report to file instead of stdout",
    )

    args = parser.parse_args()

    # Determine files to validate
    files_to_validate = []

    if args.file:
        # Single file mode
        if not os.path.exists(args.file):
            print(f"ERROR: File not found: {args.file}")
            sys.exit(1)
        files_to_validate.append(args.file)
    else:
        # Directory mode
        if not os.path.exists(args.path):
            print(f"ERROR: Directory not found: {args.path}")
            sys.exit(1)

        # Find all .docx files recursively
        for root, dirs, files in os.walk(args.path):
            for file in files:
                if file.endswith(".docx") and not file.startswith("~$"):
                    files_to_validate.append(os.path.join(root, file))

    if not files_to_validate:
        print("ERROR: No .docx files found to validate")
        sys.exit(1)

    print(f"Found {len(files_to_validate)} file(s) to validate")
    print("")

    # Validate each file
    validator = DOCXTemplateValidator(strict_mode=args.strict)
    reports = []

    for file_path in sorted(files_to_validate):
        print(f"Validating: {os.path.basename(file_path)}")
        report = validator.validate_file(file_path)
        reports.append(report)
        print("")

    # Generate report
    report_generator = ValidationReportGenerator()

    if args.json:
        json_report = report_generator.generate_json_report(reports)
        output = json.dumps(json_report, indent=2)
    else:
        output = report_generator.generate_console_report(reports, show_details=args.details)

    # Output report
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to: {args.output}")
    else:
        print(output)

    # Exit code based on results
    invalid_count = len([r for r in reports if r.overall_status == "invalid"])
    if invalid_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
