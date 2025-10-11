"""
Content Validator - Content-Based Security Validation

This module provides content-based validation for DOCX documents to detect:
- JavaScript/VBScript/PowerShell in text and hyperlinks
- Malicious URL schemes and obfuscated links
- Unreplaced template variables
- Suspicious patterns (base64, hex, HTML injection)
- Content integrity issues

Author: Automated Job Application System
Version: 1.0.0
Security Level: DEFENSIVE ONLY
"""

import re
import logging
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple
from urllib.parse import urlparse, unquote

logger = logging.getLogger(__name__)


class ContentValidator:
    """
    Validates document content for security threats

    Performs multi-layer content analysis:
    - Script detection in text and hyperlinks
    - Hyperlink URL scheme validation
    - Template variable verification
    - Suspicious pattern detection
    """

    # Script detection patterns
    SCRIPT_PATTERNS = {
        "javascript_protocol": re.compile(r"javascript:\s*", re.IGNORECASE),
        "vbscript_protocol": re.compile(r"vbscript:\s*", re.IGNORECASE),
        "script_tag": re.compile(r"<script[^>]*>", re.IGNORECASE),
        "event_handler": re.compile(
            r"on(load|error|click|mouse|key)\s*=", re.IGNORECASE
        ),
        "vb_functions": re.compile(
            r"(msgbox|createobject|wscript\.shell)", re.IGNORECASE
        ),
        "powershell": re.compile(
            r"(Invoke-Expression|IEX|Invoke-Command|Invoke-WebRequest|"
            r"Get-Process|Start-Process|New-Object\s+System\.)",
            re.IGNORECASE,
        ),
        "command_injection": re.compile(r"[;|&]{2,}|\$\([^)]+\)"),
    }

    # Suspicious content patterns
    SUSPICIOUS_PATTERNS = {
        "base64_payload": re.compile(r"(?:[A-Za-z0-9+/]{40,}={0,2})"),
        "hex_string": re.compile(r"(?:0x[0-9A-Fa-f]{8,})"),
        "clsid": re.compile(
            r"clsid:[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
            re.IGNORECASE,
        ),
        "html_injection": re.compile(r"<\w+[^>]*>"),
    }

    # Template variable patterns
    TEMPLATE_PATTERNS = {
        "double_angle": re.compile(r"<<([^>]+)>>"),  # <<variable>>
        "single_brace": re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"),  # {variable}
        "double_brace": re.compile(r"\{\{([^}]+)\}\}"),  # {{variable}}
    }

    # Dangerous URL schemes
    DANGEROUS_URL_SCHEMES = [
        "javascript",
        "vbscript",
        "file",
        "data",
        "about",
        "vnd.ms-excel",
    ]

    # Allowed URL schemes
    ALLOWED_URL_SCHEMES = ["http", "https", "mailto", "tel", "ftp"]

    def __init__(self):
        """Initialize Content Validator"""
        logger.info("ContentValidator initialized")

    def validate_document_content(self, file_path: str) -> Tuple[bool, List[Dict]]:
        """
        Validate document content for security threats

        Args:
            file_path: Path to DOCX file

        Returns:
            Tuple of (is_safe, list_of_findings)
        """
        findings = []

        try:
            # Extract text content
            text_content = self._extract_text_content(file_path)

            # Extract hyperlinks
            hyperlinks = self._extract_hyperlinks(file_path)

            # Phase 1: Detect scripts in text
            script_findings = self._detect_script_patterns(text_content)
            findings.extend(script_findings)

            # Phase 2: Validate hyperlinks
            link_findings = self._validate_hyperlinks(hyperlinks)
            findings.extend(link_findings)

            # Phase 3: Check for unreplaced template variables
            template_findings = self._check_template_variables(text_content)
            findings.extend(template_findings)

            # Phase 4: Detect suspicious patterns
            pattern_findings = self._detect_suspicious_patterns(text_content)
            findings.extend(pattern_findings)

            is_safe = len(findings) == 0

            logger.info(
                f"Content validation complete: "
                f"{'SAFE' if is_safe else 'UNSAFE'} "
                f"({len(findings)} findings)"
            )

            return is_safe, findings

        except Exception as e:
            logger.error(f"Error validating document content: {str(e)}")
            return False, [
                {
                    "type": "content_validation_error",
                    "severity": "medium",
                    "description": f"Error validating content: {str(e)}",
                }
            ]

    def _extract_text_content(self, file_path: str) -> str:
        """
        Extract all text content from document

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

        except Exception as e:
            logger.error(f"Error extracting text content: {str(e)}")

        return "\n".join(text_parts)

    def _extract_hyperlinks(self, file_path: str) -> List[Dict]:
        """
        Extract all hyperlinks from document

        Args:
            file_path: Path to DOCX file

        Returns:
            List of hyperlink dictionaries with 'text' and 'url'
        """
        hyperlinks = []

        try:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                # Extract from relationship files
                rels_files = [f for f in zip_file.namelist() if f.endswith(".rels")]

                for rels_file in rels_files:
                    rels_content = zip_file.read(rels_file).decode(
                        "utf-8", errors="ignore"
                    )
                    root = ET.fromstring(rels_content)

                    for rel in root.findall(
                        ".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
                    ):
                        rel_type = rel.get("Type", "")
                        target = rel.get("Target", "")

                        if "hyperlink" in rel_type.lower() and target:
                            hyperlinks.append(
                                {
                                    "url": target,
                                    "id": rel.get("Id", ""),
                                    "location": rels_file,
                                }
                            )

        except Exception as e:
            logger.error(f"Error extracting hyperlinks: {str(e)}")

        return hyperlinks

    def _detect_script_patterns(self, text: str) -> List[Dict]:
        """
        Detect script patterns in text content

        Args:
            text: Text content to analyze

        Returns:
            List of findings
        """
        findings = []

        for pattern_name, pattern_regex in self.SCRIPT_PATTERNS.items():
            matches = pattern_regex.finditer(text)

            for match in matches:
                # Extract context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]

                finding = {
                    "type": "script_pattern_detected",
                    "severity": "high",
                    "description": f"Script pattern detected: {pattern_name}",
                    "details": {
                        "pattern": pattern_name,
                        "match": match.group(0),
                        "context": context,
                        "position": match.start(),
                    },
                }

                findings.append(finding)
                logger.warning(
                    f"Script pattern detected: {pattern_name} at position {match.start()}"
                )

        return findings

    def _validate_hyperlinks(self, hyperlinks: List[Dict]) -> List[Dict]:
        """
        Validate hyperlink URLs for malicious schemes

        Args:
            hyperlinks: List of hyperlink dictionaries

        Returns:
            List of findings
        """
        findings = []

        for link in hyperlinks:
            url = link["url"]

            try:
                # Parse URL
                parsed = urlparse(url)
                scheme = parsed.scheme.lower() if parsed.scheme else ""

                # Check for dangerous schemes
                if scheme in self.DANGEROUS_URL_SCHEMES:
                    finding = {
                        "type": "malicious_hyperlink",
                        "severity": "critical",
                        "description": f"Dangerous URL scheme detected: {scheme}",
                        "details": {
                            "url": url,
                            "scheme": scheme,
                            "location": link["location"],
                            "link_id": link["id"],
                        },
                    }
                    findings.append(finding)
                    logger.warning(f"Dangerous URL scheme: {scheme} in {url}")

                # Check for obfuscation
                if self._is_obfuscated_url(url):
                    finding = {
                        "type": "obfuscated_url",
                        "severity": "high",
                        "description": "Obfuscated URL detected",
                        "details": {
                            "url": url,
                            "location": link["location"],
                        },
                    }
                    findings.append(finding)
                    logger.warning(f"Obfuscated URL detected: {url}")

            except Exception as e:
                logger.error(f"Error validating hyperlink {url}: {str(e)}")

        return findings

    def _is_obfuscated_url(self, url: str) -> bool:
        """Check if URL appears obfuscated"""
        # Check for HTML entities
        if re.search(r"&#\d+;", url):
            return True

        # Check for excessive URL encoding
        if url.count("%") > 5:
            return True

        # Check for Unicode escapes
        if re.search(r"\\u[0-9A-Fa-f]{4}", url):
            return True

        return False

    def _check_template_variables(self, text: str) -> List[Dict]:
        """
        Check for unreplaced template variables

        Args:
            text: Text content to analyze

        Returns:
            List of findings
        """
        findings = []

        for pattern_name, pattern_regex in self.TEMPLATE_PATTERNS.items():
            matches = pattern_regex.findall(text)

            if matches:
                # Remove duplicates
                unique_vars = list(set(matches))

                finding = {
                    "type": "unreplaced_template_variable",
                    "severity": "medium",
                    "description": f"Unreplaced template variables found ({pattern_name})",
                    "details": {
                        "pattern_type": pattern_name,
                        "variable_count": len(unique_vars),
                        "variables": unique_vars[:10],  # First 10
                    },
                }

                findings.append(finding)
                logger.warning(
                    f"Unreplaced variables ({pattern_name}): {len(unique_vars)}"
                )

        return findings

    def _detect_suspicious_patterns(self, text: str) -> List[Dict]:
        """
        Detect suspicious patterns in text

        Args:
            text: Text content to analyze

        Returns:
            List of findings
        """
        findings = []

        for pattern_name, pattern_regex in self.SUSPICIOUS_PATTERNS.items():
            matches = list(pattern_regex.finditer(text))

            # Only report if multiple matches or very long matches
            significant_matches = [
                m for m in matches if len(m.group(0)) > 50 or len(matches) > 3
            ]

            if significant_matches:
                finding = {
                    "type": "suspicious_content_pattern",
                    "severity": "medium",
                    "description": f"Suspicious pattern detected: {pattern_name}",
                    "details": {
                        "pattern": pattern_name,
                        "match_count": len(significant_matches),
                        "samples": [m.group(0)[:100] for m in significant_matches[:3]],
                    },
                }

                findings.append(finding)
                logger.info(
                    f"Suspicious pattern detected: {pattern_name} "
                    f"({len(significant_matches)} matches)"
                )

        return findings


# Module-level convenience function


def validate_document_content(file_path: str) -> Tuple[bool, List[Dict]]:
    """
    Convenience function to validate document content

    Args:
        file_path: Path to DOCX file

    Returns:
        Tuple of (is_safe, list_of_findings)
    """
    validator = ContentValidator()
    return validator.validate_document_content(file_path)
