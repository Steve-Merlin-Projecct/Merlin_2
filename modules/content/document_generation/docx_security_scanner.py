"""
DOCX Security Scanner - Malicious Content Detection and Prevention

This module provides comprehensive security scanning for DOCX files to detect and prevent:
1. Remote template injection (DOTM references)
2. Embedded OLE objects and ActiveX controls
3. Malformed ZIP structure and XML bombs
4. External content references and data exfiltration vectors

The scanner inspects DOCX files at the ZIP/XML level to identify security threats
before documents are generated or processed.

Author: Automated Job Application System
Version: 1.0.0
Security Level: DEFENSIVE ONLY
"""

import os
import re
import logging
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path
from io import BytesIO

logger = logging.getLogger(__name__)


class SecurityThreat:
    """
    Represents a detected security threat in a DOCX file

    Attributes:
        threat_type: Category of threat (remote_template, ole_object, xml_bomb, etc.)
        severity: Threat severity (critical, high, medium, low)
        description: Human-readable description
        location: Where threat was found (file path within ZIP)
        details: Additional technical details
    """

    def __init__(
        self,
        threat_type: str,
        severity: str,
        description: str,
        location: str = "",
        details: Optional[Dict] = None,
    ):
        self.threat_type = threat_type
        self.severity = severity
        self.description = description
        self.location = location
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert threat to dictionary for logging"""
        return {
            "threat_type": self.threat_type,
            "severity": self.severity,
            "description": self.description,
            "location": self.location,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class DOCXSecurityScanner:
    """
    Comprehensive security scanner for DOCX files

    Performs multi-layer security validation:
    - ZIP structure integrity
    - Remote template detection
    - OLE object inspection
    - XML bomb detection
    - External reference validation
    """

    # XML namespaces for OOXML
    NAMESPACES = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
        "v": "urn:schemas-microsoft-com:vml",
        "o": "urn:schemas-microsoft-com:office:office",
    }

    # Suspicious OLE ProgIDs that indicate executable content
    SUSPICIOUS_OLE_PROGIDS = [
        "Package",  # Can contain executable files
        "Excel.Sheet",  # Embedded Excel with macros
        "Word.Document",  # Embedded Word with macros
        "Scripting.FileSystemObject",  # File system access
        "Shell.Application",  # Command execution
        "WScript.Shell",  # Script execution
        "msxml2.XMLHTTP",  # Network requests
        "msxml2.DOMDocument",  # XML parsing (XXE attacks)
    ]

    # Suspicious file extensions in OLE objects
    SUSPICIOUS_EXTENSIONS = [
        ".exe",
        ".dll",
        ".scr",
        ".vbs",
        ".js",
        ".bat",
        ".cmd",
        ".ps1",
        ".hta",
        ".jar",
        ".msi",
        ".com",
        ".pif",
        ".lnk",
        ".docm",
        ".dotm",
        ".xlsm",
        ".xltm",
        ".pptm",
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize security scanner

        Args:
            strict_mode: If True, treat warnings as failures. If False, only block critical threats.
        """
        self.strict_mode = strict_mode
        self.threats: List[SecurityThreat] = []
        logger.info(f"DOCX Security Scanner initialized (strict_mode={strict_mode})")

    def scan_file(self, file_path: str) -> Tuple[bool, List[SecurityThreat]]:
        """
        Scan a DOCX file for security threats

        Args:
            file_path: Path to DOCX file to scan

        Returns:
            Tuple of (is_safe, list_of_threats)
            - is_safe: True if file passes security checks
            - list_of_threats: List of SecurityThreat objects found
        """
        self.threats = []

        logger.info(f"Starting security scan of: {file_path}")

        # Validate file exists
        if not os.path.exists(file_path):
            threat = SecurityThreat(
                threat_type="file_not_found",
                severity="critical",
                description=f"File does not exist: {file_path}",
                location=file_path,
            )
            self.threats.append(threat)
            return False, self.threats

        # Phase 1: ZIP structure validation
        if not self._validate_zip_structure(file_path):
            logger.error(f"ZIP structure validation failed: {file_path}")
            return False, self.threats

        # Phase 2: Remote template detection
        self._detect_remote_templates(file_path)

        # Phase 3: OLE object inspection
        self._inspect_ole_objects(file_path)

        # Phase 4: External reference detection
        self._detect_external_references(file_path)

        # Phase 5: XML bomb detection
        self._detect_xml_bombs(file_path)

        # Phase 6: Content validation
        self._validate_document_content(file_path)

        # Evaluate overall safety
        is_safe = self._evaluate_safety()

        logger.info(
            f"Security scan completed: {file_path} - "
            f"{'SAFE' if is_safe else 'UNSAFE'} - "
            f"{len(self.threats)} threats found"
        )

        return is_safe, self.threats

    def scan_bytes(
        self, docx_bytes: bytes, filename: str = "document.docx"
    ) -> Tuple[bool, List[SecurityThreat]]:
        """
        Scan DOCX content from bytes (for in-memory scanning)

        Args:
            docx_bytes: DOCX file content as bytes
            filename: Filename for logging purposes

        Returns:
            Tuple of (is_safe, list_of_threats)
        """
        self.threats = []

        logger.info(f"Starting security scan of bytes: {filename}")

        # Create BytesIO object for ZIP operations
        docx_io = BytesIO(docx_bytes)

        # Phase 1: ZIP structure validation
        if not self._validate_zip_structure_bytes(docx_io, filename):
            logger.error(f"ZIP structure validation failed: {filename}")
            return False, self.threats

        # Reset BytesIO position
        docx_io.seek(0)

        # Phase 2: Remote template detection
        self._detect_remote_templates_bytes(docx_io, filename)

        # Phase 3: OLE object inspection
        docx_io.seek(0)
        self._inspect_ole_objects_bytes(docx_io, filename)

        # Phase 4: External reference detection
        docx_io.seek(0)
        self._detect_external_references_bytes(docx_io, filename)

        # Phase 5: XML bomb detection
        docx_io.seek(0)
        self._detect_xml_bombs_bytes(docx_io, filename)

        # Evaluate overall safety
        is_safe = self._evaluate_safety()

        logger.info(
            f"Security scan completed: {filename} - "
            f"{'SAFE' if is_safe else 'UNSAFE'} - "
            f"{len(self.threats)} threats found"
        )

        return is_safe, self.threats

    def _validate_zip_structure(self, file_path: str) -> bool:
        """
        Validate ZIP structure integrity

        Checks:
        - File is valid ZIP
        - Contains required OOXML files
        - No suspicious file names
        - File size reasonable

        Args:
            file_path: Path to DOCX file

        Returns:
            True if structure is valid
        """
        try:
            # Check if file is valid ZIP
            if not zipfile.is_zipfile(file_path):
                threat = SecurityThreat(
                    threat_type="invalid_zip",
                    severity="critical",
                    description="File is not a valid ZIP/DOCX archive",
                    location=file_path,
                )
                self.threats.append(threat)
                return False

            # Open and validate ZIP contents
            with zipfile.ZipFile(file_path, "r") as zip_file:
                # Test ZIP integrity
                bad_file = zip_file.testzip()
                if bad_file:
                    threat = SecurityThreat(
                        threat_type="corrupted_zip",
                        severity="critical",
                        description=f"Corrupted file in ZIP: {bad_file}",
                        location=file_path,
                        details={"corrupted_file": bad_file},
                    )
                    self.threats.append(threat)
                    return False

                # Check for required OOXML files
                required_files = ["[Content_Types].xml", "_rels/.rels"]
                file_list = zip_file.namelist()

                for required in required_files:
                    if required not in file_list:
                        threat = SecurityThreat(
                            threat_type="missing_required_file",
                            severity="high",
                            description=f"Missing required OOXML file: {required}",
                            location=file_path,
                            details={"missing_file": required},
                        )
                        self.threats.append(threat)

                # Check for suspicious file names
                for filename in file_list:
                    # Check for path traversal attempts
                    if ".." in filename or filename.startswith("/"):
                        threat = SecurityThreat(
                            threat_type="path_traversal",
                            severity="critical",
                            description=f"Suspicious file path (path traversal): {filename}",
                            location=file_path,
                            details={"suspicious_file": filename},
                        )
                        self.threats.append(threat)

                    # Check for executable extensions
                    for ext in self.SUSPICIOUS_EXTENSIONS:
                        if filename.lower().endswith(ext):
                            threat = SecurityThreat(
                                threat_type="suspicious_file",
                                severity="high",
                                description=f"Suspicious file extension in ZIP: {filename}",
                                location=file_path,
                                details={"suspicious_file": filename},
                            )
                            self.threats.append(threat)

            return True

        except zipfile.BadZipFile as e:
            threat = SecurityThreat(
                threat_type="bad_zip_file",
                severity="critical",
                description=f"Invalid ZIP file: {str(e)}",
                location=file_path,
            )
            self.threats.append(threat)
            return False

        except Exception as e:
            threat = SecurityThreat(
                threat_type="zip_validation_error",
                severity="high",
                description=f"Error validating ZIP structure: {str(e)}",
                location=file_path,
            )
            self.threats.append(threat)
            return False

    def _validate_zip_structure_bytes(self, docx_io: BytesIO, filename: str) -> bool:
        """Validate ZIP structure from bytes"""
        try:
            # Check if bytes are valid ZIP
            if not zipfile.is_zipfile(docx_io):
                threat = SecurityThreat(
                    threat_type="invalid_zip",
                    severity="critical",
                    description="Content is not a valid ZIP/DOCX archive",
                    location=filename,
                )
                self.threats.append(threat)
                return False

            docx_io.seek(0)

            # Open and validate ZIP contents
            with zipfile.ZipFile(docx_io, "r") as zip_file:
                # Test ZIP integrity
                bad_file = zip_file.testzip()
                if bad_file:
                    threat = SecurityThreat(
                        threat_type="corrupted_zip",
                        severity="critical",
                        description=f"Corrupted file in ZIP: {bad_file}",
                        location=filename,
                        details={"corrupted_file": bad_file},
                    )
                    self.threats.append(threat)
                    return False

                # Check for required OOXML files
                required_files = ["[Content_Types].xml", "_rels/.rels"]
                file_list = zip_file.namelist()

                for required in required_files:
                    if required not in file_list:
                        threat = SecurityThreat(
                            threat_type="missing_required_file",
                            severity="high",
                            description=f"Missing required OOXML file: {required}",
                            location=filename,
                            details={"missing_file": required},
                        )
                        self.threats.append(threat)

            return True

        except Exception as e:
            threat = SecurityThreat(
                threat_type="zip_validation_error",
                severity="high",
                description=f"Error validating ZIP structure: {str(e)}",
                location=filename,
            )
            self.threats.append(threat)
            return False

    def _detect_remote_templates(self, file_path: str) -> None:
        """
        Detect remote template references (DOTM injection attacks)

        Remote templates are one of the most dangerous threats in DOCX files.
        When a document references a remote DOTM template, Word will automatically
        fetch and execute any macros in that template.

        Checks:
        - Settings.xml for attachedTemplate references
        - Relationship files for external template links
        - HTTP/HTTPS URLs in template paths

        Args:
            file_path: Path to DOCX file
        """
        try:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                # Check settings.xml for attachedTemplate
                settings_path = "word/settings.xml"
                if settings_path in zip_file.namelist():
                    settings_content = zip_file.read(settings_path).decode(
                        "utf-8", errors="ignore"
                    )

                    # Parse XML
                    root = ET.fromstring(settings_content)

                    # Look for attachedTemplate element
                    attached_template = root.find(
                        ".//w:attachedTemplate", self.NAMESPACES
                    )
                    if attached_template is not None:
                        template_ref = attached_template.get(
                            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
                        )

                        if template_ref:
                            # This is a critical threat - document references external template
                            threat = SecurityThreat(
                                threat_type="remote_template",
                                severity="critical",
                                description="Document contains remote template reference (DOTM injection risk)",
                                location=settings_path,
                                details={
                                    "template_id": template_ref,
                                    "mitigation": "Remove attachedTemplate element from settings.xml",
                                },
                            )
                            self.threats.append(threat)
                            logger.warning(f"Remote template detected: {template_ref}")

                # Check relationship files for external template links
                rels_files = [f for f in zip_file.namelist() if f.endswith(".rels")]
                for rels_file in rels_files:
                    rels_content = zip_file.read(rels_file).decode(
                        "utf-8", errors="ignore"
                    )

                    # Look for HTTP/HTTPS URLs
                    if re.search(r"https?://", rels_content, re.IGNORECASE):
                        # Check if it's a template reference
                        if (
                            "template" in rels_content.lower()
                            or ".dotm" in rels_content.lower()
                        ):
                            threat = SecurityThreat(
                                threat_type="remote_template_url",
                                severity="critical",
                                description="Remote template URL found in relationships",
                                location=rels_file,
                                details={
                                    "mitigation": "Remove external template references"
                                },
                            )
                            self.threats.append(threat)
                            logger.warning(f"Remote template URL in: {rels_file}")

        except Exception as e:
            logger.error(f"Error detecting remote templates: {str(e)}")
            threat = SecurityThreat(
                threat_type="template_scan_error",
                severity="medium",
                description=f"Error scanning for remote templates: {str(e)}",
                location=file_path,
            )
            self.threats.append(threat)

    def _detect_remote_templates_bytes(self, docx_io: BytesIO, filename: str) -> None:
        """Detect remote templates from bytes"""
        try:
            with zipfile.ZipFile(docx_io, "r") as zip_file:
                settings_path = "word/settings.xml"
                if settings_path in zip_file.namelist():
                    settings_content = zip_file.read(settings_path).decode(
                        "utf-8", errors="ignore"
                    )
                    root = ET.fromstring(settings_content)

                    attached_template = root.find(
                        ".//w:attachedTemplate", self.NAMESPACES
                    )
                    if attached_template is not None:
                        template_ref = attached_template.get(
                            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
                        )

                        if template_ref:
                            threat = SecurityThreat(
                                threat_type="remote_template",
                                severity="critical",
                                description="Document contains remote template reference (DOTM injection risk)",
                                location=settings_path,
                                details={"template_id": template_ref},
                            )
                            self.threats.append(threat)

        except Exception as e:
            logger.error(f"Error detecting remote templates: {str(e)}")

    def _inspect_ole_objects(self, file_path: str) -> None:
        """
        Inspect embedded OLE objects for malicious content

        OLE objects can contain:
        - ActiveX controls (executable code)
        - Embedded Office documents with macros
        - Package objects (arbitrary files including executables)
        - Scripting objects (VBS, JS)

        Args:
            file_path: Path to DOCX file
        """
        try:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                # Check for embeddings directory (OLE objects)
                ole_files = [
                    f
                    for f in zip_file.namelist()
                    if "embeddings/" in f or "oleObject" in f.lower()
                ]

                if ole_files:
                    threat = SecurityThreat(
                        threat_type="ole_object_detected",
                        severity="high",
                        description=f"Embedded OLE objects detected ({len(ole_files)} objects)",
                        location=file_path,
                        details={
                            "ole_files": ole_files,
                            "mitigation": "Review and remove unnecessary OLE objects",
                        },
                    )
                    self.threats.append(threat)
                    logger.warning(f"OLE objects detected: {len(ole_files)}")

                    # Perform deep OLE analysis if available
                    self._perform_deep_ole_analysis(zip_file, ole_files, file_path)

                # Check document.xml for OLE object references
                doc_path = "word/document.xml"
                if doc_path in zip_file.namelist():
                    doc_content = zip_file.read(doc_path).decode(
                        "utf-8", errors="ignore"
                    )

                    # Look for OLE object elements
                    if "<o:OLEObject" in doc_content or "<w:object" in doc_content:
                        threat = SecurityThreat(
                            threat_type="ole_object_reference",
                            severity="high",
                            description="OLE object references found in document XML",
                            location=doc_path,
                            details={"mitigation": "Remove OLE object elements"},
                        )
                        self.threats.append(threat)
                        logger.warning(f"OLE object reference in {doc_path}")

                    # Check for ActiveX controls
                    if "ActiveX" in doc_content or "control" in doc_content:
                        threat = SecurityThreat(
                            threat_type="activex_control",
                            severity="critical",
                            description="ActiveX control detected (executable code)",
                            location=doc_path,
                            details={"mitigation": "Remove ActiveX controls"},
                        )
                        self.threats.append(threat)
                        logger.warning(f"ActiveX control in {doc_path}")

        except Exception as e:
            logger.error(f"Error inspecting OLE objects: {str(e)}")
            threat = SecurityThreat(
                threat_type="ole_scan_error",
                severity="medium",
                description=f"Error scanning for OLE objects: {str(e)}",
                location=file_path,
            )
            self.threats.append(threat)

    def _perform_deep_ole_analysis(
        self, zip_file: zipfile.ZipFile, ole_files: List[str], file_path: str
    ) -> None:
        """
        Perform deep analysis of OLE files using oletools

        Args:
            zip_file: Opened ZIP file object
            ole_files: List of OLE file paths in ZIP
            file_path: Path to DOCX file for logging
        """
        try:
            # Import OLE analyzer
            from .ole_stream_analyzer import OLEStreamAnalyzer, OLETOOLS_AVAILABLE

            if not OLETOOLS_AVAILABLE:
                logger.debug("Deep OLE analysis skipped - oletools not available")
                return

            analyzer = OLEStreamAnalyzer()

            for ole_file_path in ole_files:
                try:
                    # Extract OLE file from ZIP
                    ole_bytes = zip_file.read(ole_file_path)

                    # Analyze OLE file
                    has_threats, findings = analyzer.analyze_ole_file(
                        ole_bytes, ole_file_path
                    )

                    # Convert findings to SecurityThreat objects
                    for finding in findings:
                        threat = SecurityThreat(
                            threat_type=finding.get("type", "ole_analysis_finding"),
                            severity=finding.get("severity", "medium"),
                            description=finding.get("description", "OLE analysis finding"),
                            location=f"{file_path}:{ole_file_path}",
                            details=finding.get("details", {}),
                        )
                        self.threats.append(threat)

                        if finding.get("severity") in ["critical", "high"]:
                            logger.warning(
                                f"Deep OLE analysis found: {finding.get('type')} "
                                f"in {ole_file_path}"
                            )

                except Exception as e:
                    logger.error(f"Error analyzing OLE file {ole_file_path}: {str(e)}")

        except ImportError:
            logger.debug("OLE stream analyzer not available")
        except Exception as e:
            logger.error(f"Error in deep OLE analysis: {str(e)}")

    def _inspect_ole_objects_bytes(self, docx_io: BytesIO, filename: str) -> None:
        """Inspect OLE objects from bytes"""
        try:
            with zipfile.ZipFile(docx_io, "r") as zip_file:
                ole_files = [
                    f
                    for f in zip_file.namelist()
                    if "embeddings/" in f or "oleObject" in f.lower()
                ]

                if ole_files:
                    threat = SecurityThreat(
                        threat_type="ole_object_detected",
                        severity="high",
                        description=f"Embedded OLE objects detected ({len(ole_files)} objects)",
                        location=filename,
                        details={"ole_files": ole_files},
                    )
                    self.threats.append(threat)

        except Exception as e:
            logger.error(f"Error inspecting OLE objects: {str(e)}")

    def _detect_external_references(self, file_path: str) -> None:
        """
        Detect external content references (data exfiltration vectors)

        External references can leak information about who opens the document:
        - External image URLs (tracking pixels)
        - External stylesheet references
        - Hyperlinks to external resources

        Args:
            file_path: Path to DOCX file
        """
        try:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                # Check all relationship files
                rels_files = [f for f in zip_file.namelist() if f.endswith(".rels")]

                external_refs = []
                for rels_file in rels_files:
                    rels_content = zip_file.read(rels_file).decode(
                        "utf-8", errors="ignore"
                    )

                    # Look for external HTTP/HTTPS URLs
                    urls = re.findall(
                        r'Target="(https?://[^"]+)"', rels_content, re.IGNORECASE
                    )
                    if urls:
                        external_refs.extend(urls)

                if external_refs:
                    threat = SecurityThreat(
                        threat_type="external_references",
                        severity="medium",
                        description=f"External content references detected ({len(external_refs)} URLs)",
                        location=file_path,
                        details={
                            "urls": external_refs[:5],  # First 5 URLs
                            "total_count": len(external_refs),
                            "note": "May leak information when document is opened",
                        },
                    )
                    self.threats.append(threat)
                    logger.info(f"External references: {len(external_refs)}")

        except Exception as e:
            logger.error(f"Error detecting external references: {str(e)}")

    def _detect_external_references_bytes(
        self, docx_io: BytesIO, filename: str
    ) -> None:
        """Detect external references from bytes"""
        try:
            with zipfile.ZipFile(docx_io, "r") as zip_file:
                rels_files = [f for f in zip_file.namelist() if f.endswith(".rels")]

                external_refs = []
                for rels_file in rels_files:
                    rels_content = zip_file.read(rels_file).decode(
                        "utf-8", errors="ignore"
                    )
                    urls = re.findall(
                        r'Target="(https?://[^"]+)"', rels_content, re.IGNORECASE
                    )
                    if urls:
                        external_refs.extend(urls)

                if external_refs:
                    threat = SecurityThreat(
                        threat_type="external_references",
                        severity="medium",
                        description=f"External content references detected ({len(external_refs)} URLs)",
                        location=filename,
                        details={
                            "urls": external_refs[:5],
                            "total_count": len(external_refs),
                        },
                    )
                    self.threats.append(threat)

        except Exception as e:
            logger.error(f"Error detecting external references: {str(e)}")

    def _detect_xml_bombs(self, file_path: str) -> None:
        """
        Detect XML bomb attacks (billion laughs, exponential entity expansion)

        XML bombs use entity expansion to create exponentially large documents
        that can exhaust memory and crash systems.

        Args:
            file_path: Path to DOCX file
        """
        try:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                # Check XML files for suspicious entity definitions
                xml_files = [f for f in zip_file.namelist() if f.endswith(".xml")]

                for xml_file in xml_files:
                    content = zip_file.read(xml_file).decode("utf-8", errors="ignore")

                    # Look for DOCTYPE with entity definitions
                    if "<!DOCTYPE" in content and "<!ENTITY" in content:
                        threat = SecurityThreat(
                            threat_type="xml_entities",
                            severity="high",
                            description="XML entity definitions detected (potential XML bomb)",
                            location=xml_file,
                            details={
                                "mitigation": "Remove DOCTYPE and entity definitions"
                            },
                        )
                        self.threats.append(threat)
                        logger.warning(f"XML entities in {xml_file}")

                    # Check for excessive nesting depth
                    nesting_depth = content.count("<") - content.count("</")
                    if nesting_depth > 100:
                        threat = SecurityThreat(
                            threat_type="excessive_xml_nesting",
                            severity="medium",
                            description=f"Excessive XML nesting depth ({nesting_depth})",
                            location=xml_file,
                            details={"nesting_depth": nesting_depth},
                        )
                        self.threats.append(threat)

        except Exception as e:
            logger.error(f"Error detecting XML bombs: {str(e)}")

    def _detect_xml_bombs_bytes(self, docx_io: BytesIO, filename: str) -> None:
        """Detect XML bombs from bytes"""
        try:
            with zipfile.ZipFile(docx_io, "r") as zip_file:
                xml_files = [f for f in zip_file.namelist() if f.endswith(".xml")]

                for xml_file in xml_files:
                    content = zip_file.read(xml_file).decode("utf-8", errors="ignore")

                    if "<!DOCTYPE" in content and "<!ENTITY" in content:
                        threat = SecurityThreat(
                            threat_type="xml_entities",
                            severity="high",
                            description="XML entity definitions detected (potential XML bomb)",
                            location=xml_file,
                        )
                        self.threats.append(threat)

        except Exception as e:
            logger.error(f"Error detecting XML bombs: {str(e)}")

    def _validate_document_content(self, file_path: str) -> None:
        """
        Validate document content for security threats

        Checks for:
        - Scripts in text and hyperlinks
        - Malicious URL schemes
        - Unreplaced template variables
        - Suspicious patterns

        Args:
            file_path: Path to DOCX file
        """
        try:
            from .content_validator import ContentValidator

            validator = ContentValidator()
            is_safe, findings = validator.validate_document_content(file_path)

            # Convert findings to SecurityThreat objects
            for finding in findings:
                threat = SecurityThreat(
                    threat_type=finding.get("type", "content_validation_finding"),
                    severity=finding.get("severity", "medium"),
                    description=finding.get("description", "Content validation finding"),
                    location=file_path,
                    details=finding.get("details", {}),
                )
                self.threats.append(threat)

                if finding.get("severity") in ["critical", "high"]:
                    logger.warning(
                        f"Content validation found: {finding.get('type')} in {file_path}"
                    )

        except ImportError:
            logger.debug("Content validator not available")
        except Exception as e:
            logger.error(f"Error in content validation: {str(e)}")

    def _evaluate_safety(self) -> bool:
        """
        Evaluate overall document safety based on detected threats

        Returns:
            True if document is safe (no critical threats)
        """
        if not self.threats:
            return True

        # Count threats by severity
        critical_count = sum(1 for t in self.threats if t.severity == "critical")
        high_count = sum(1 for t in self.threats if t.severity == "high")

        # Always block critical threats
        if critical_count > 0:
            logger.error(f"Document UNSAFE: {critical_count} critical threats detected")
            return False

        # In strict mode, block high severity threats too
        if self.strict_mode and high_count > 0:
            logger.warning(
                f"Document UNSAFE (strict mode): {high_count} high severity threats"
            )
            return False

        return True

    def get_scan_report(self) -> Dict:
        """
        Generate comprehensive scan report

        Returns:
            Dictionary containing scan results and statistics
        """
        threat_dict = [t.to_dict() for t in self.threats]

        severity_counts = {
            "critical": sum(1 for t in self.threats if t.severity == "critical"),
            "high": sum(1 for t in self.threats if t.severity == "high"),
            "medium": sum(1 for t in self.threats if t.severity == "medium"),
            "low": sum(1 for t in self.threats if t.severity == "low"),
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "total_threats": len(self.threats),
            "severity_counts": severity_counts,
            "is_safe": self._evaluate_safety(),
            "strict_mode": self.strict_mode,
            "threats": threat_dict,
        }


def scan_docx_file(file_path: str, strict_mode: bool = True) -> Tuple[bool, Dict]:
    """
    Convenience function to scan a DOCX file

    Args:
        file_path: Path to DOCX file
        strict_mode: Whether to use strict validation

    Returns:
        Tuple of (is_safe, scan_report)
    """
    scanner = DOCXSecurityScanner(strict_mode=strict_mode)
    is_safe, threats = scanner.scan_file(file_path)
    report = scanner.get_scan_report()
    return is_safe, report


def scan_docx_bytes(
    docx_bytes: bytes, filename: str = "document.docx", strict_mode: bool = True
) -> Tuple[bool, Dict]:
    """
    Convenience function to scan DOCX bytes

    Args:
        docx_bytes: DOCX content as bytes
        filename: Filename for logging
        strict_mode: Whether to use strict validation

    Returns:
        Tuple of (is_safe, scan_report)
    """
    scanner = DOCXSecurityScanner(strict_mode=strict_mode)
    is_safe, threats = scanner.scan_bytes(docx_bytes, filename)
    report = scanner.get_scan_report()
    return is_safe, report
