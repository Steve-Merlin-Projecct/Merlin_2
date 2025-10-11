"""
OLE Stream Analyzer - Deep Analysis of OLE Compound Files

This module provides deep analysis of OLE (Object Linking and Embedding) compound files
embedded in DOCX documents. Uses oletools library to detect VBA macros, suspicious stream
names, and malicious content that basic presence detection cannot identify.

Features:
- VBA macro detection in embedded Office documents
- Suspicious stream name identification
- OLE compound file structure analysis
- AutoOpen/AutoExec trigger detection

Author: Automated Job Application System
Version: 1.0.0
Security Level: DEFENSIVE ONLY
"""

import logging
from typing import Dict, List, Tuple, Optional
from io import BytesIO

logger = logging.getLogger(__name__)

# Try to import oletools (graceful degradation if not available)
try:
    from oletools.olevba import VBA_Parser
    from oletools.oleid import OleID
    import olefile

    OLETOOLS_AVAILABLE = True
except ImportError:
    OLETOOLS_AVAILABLE = False
    logger.warning(
        "oletools not available - deep OLE analysis disabled. "
        "Install with: pip install oletools"
    )


class OLEStreamAnalyzer:
    """
    Analyzes OLE compound files for security threats

    Performs deep analysis of embedded OLE objects to detect:
    - VBA macros (including AutoOpen/AutoExec triggers)
    - Suspicious stream names
    - Hidden or obfuscated content
    - Macro-enabled embedded documents
    """

    # Known suspicious OLE stream names
    SUSPICIOUS_STREAM_NAMES = [
        "VBA",  # VBA project directory
        "Macros",  # Macro storage
        "_VBA_PROJECT",  # VBA project metadata
        "__SRP_",  # Signed VBA streams
        "VBA/_VBA_PROJECT",  # VBA project file
        "Macros/VBA",  # Macro VBA directory
        r"\x01CompObj",  # Compound object (can hide data)
        r"\x01Ole10Native",  # Native embedded objects
        "PowerPoint Document",  # Embedded presentations
        "Workbook",  # Embedded spreadsheets
        "WordDocument",  # Embedded Word documents
    ]

    # VBA Auto-execution trigger patterns
    AUTO_EXEC_TRIGGERS = [
        "AutoOpen",  # Word/Excel auto-execution
        "AutoExec",  # Excel auto-execution
        "Document_Open",  # Word document open event
        "Workbook_Open",  # Excel workbook open event
        "Auto_Open",  # Legacy auto-open
        "AutoClose",  # Document close (can be malicious)
        "Document_Close",  # Word close event
        "Workbook_Close",  # Excel close event
    ]

    def __init__(self):
        """Initialize OLE Stream Analyzer"""
        self.oletools_available = OLETOOLS_AVAILABLE
        if not self.oletools_available:
            logger.warning("OLE stream analysis unavailable - oletools not installed")

    def analyze_ole_file(
        self, ole_bytes: bytes, filename: str = "embedded.ole"
    ) -> Tuple[bool, List[Dict]]:
        """
        Analyze OLE compound file for security threats

        Args:
            ole_bytes: OLE file content as bytes
            filename: Filename for logging purposes

        Returns:
            Tuple of (has_threats, list_of_findings)
            - has_threats: True if any threats detected
            - list_of_findings: List of finding dictionaries
        """
        if not self.oletools_available:
            logger.debug("OLE analysis skipped - oletools not available")
            return False, []

        findings = []

        try:
            # Phase 1: Check if file is valid OLE
            if not olefile.isOleFile(BytesIO(ole_bytes)):
                logger.debug(f"{filename} is not a valid OLE file")
                return False, []

            # Phase 2: Detect VBA macros
            macro_findings = self._detect_vba_macros(ole_bytes, filename)
            findings.extend(macro_findings)

            # Phase 3: Analyze stream names
            stream_findings = self._analyze_stream_names(ole_bytes, filename)
            findings.extend(stream_findings)

            # Phase 4: Check OLE metadata
            metadata_findings = self._analyze_ole_metadata(ole_bytes, filename)
            findings.extend(metadata_findings)

            has_threats = len(findings) > 0

            logger.info(
                f"OLE analysis complete for {filename}: "
                f"{'THREATS FOUND' if has_threats else 'CLEAN'} "
                f"({len(findings)} findings)"
            )

            return has_threats, findings

        except Exception as e:
            logger.error(f"Error analyzing OLE file {filename}: {str(e)}")
            # Return error as finding
            return True, [
                {
                    "type": "ole_analysis_error",
                    "severity": "medium",
                    "description": f"Error analyzing OLE file: {str(e)}",
                    "filename": filename,
                }
            ]

    def _detect_vba_macros(self, ole_bytes: bytes, filename: str) -> List[Dict]:
        """
        Detect VBA macros in OLE file

        Args:
            ole_bytes: OLE file content as bytes
            filename: Filename for logging

        Returns:
            List of macro findings
        """
        findings = []

        try:
            # Parse OLE file for VBA
            vba_parser = VBA_Parser(filename=None, data=ole_bytes)

            # Check if VBA macros detected
            if vba_parser.detect_vba_macros():
                logger.warning(f"VBA macros detected in {filename}")

                # Extract macro information
                macro_info = {
                    "type": "vba_macro_detected",
                    "severity": "high",
                    "description": f"VBA macros found in embedded file: {filename}",
                    "filename": filename,
                    "details": {"macro_count": 0, "auto_exec_triggers": []},
                }

                # Extract macros and analyze
                try:
                    macros = vba_parser.extract_macros()
                    if macros:
                        macro_info["details"]["macro_count"] = len(list(macros))

                        # Check for auto-execution triggers
                        vba_parser_reopen = VBA_Parser(filename=None, data=ole_bytes)
                        for (
                            vba_filename,
                            stream_path,
                            vba_code_path,
                            vba_code,
                        ) in vba_parser_reopen.extract_macros():
                            if vba_code:
                                for trigger in self.AUTO_EXEC_TRIGGERS:
                                    if trigger in vba_code:
                                        macro_info["details"][
                                            "auto_exec_triggers"
                                        ].append(trigger)
                                        logger.warning(
                                            f"Auto-execution trigger found: {trigger}"
                                        )

                        # Upgrade severity if auto-exec triggers found
                        if macro_info["details"]["auto_exec_triggers"]:
                            macro_info["severity"] = "critical"
                            macro_info[
                                "description"
                            ] += f" (Auto-execution triggers: {', '.join(macro_info['details']['auto_exec_triggers'])})"

                except Exception as e:
                    logger.error(f"Error extracting macros: {str(e)}")
                    macro_info["details"]["extraction_error"] = str(e)

                findings.append(macro_info)

            # Close parser
            vba_parser.close()

        except Exception as e:
            logger.error(f"Error detecting VBA macros in {filename}: {str(e)}")
            findings.append(
                {
                    "type": "vba_detection_error",
                    "severity": "medium",
                    "description": f"Error detecting VBA macros: {str(e)}",
                    "filename": filename,
                }
            )

        return findings

    def _analyze_stream_names(self, ole_bytes: bytes, filename: str) -> List[Dict]:
        """
        Analyze OLE stream names for suspicious patterns

        Args:
            ole_bytes: OLE file content as bytes
            filename: Filename for logging

        Returns:
            List of stream findings
        """
        findings = []

        try:
            # Open OLE file
            ole = olefile.OleFileIO(BytesIO(ole_bytes))

            # Get list of all streams
            streams = ole.listdir()

            suspicious_streams = []

            for stream_path in streams:
                stream_name = "/".join(stream_path)

                # Check against known suspicious patterns
                for suspicious_pattern in self.SUSPICIOUS_STREAM_NAMES:
                    if suspicious_pattern in stream_name:
                        suspicious_streams.append(
                            {
                                "name": stream_name,
                                "pattern": suspicious_pattern,
                                "size": ole.get_size(stream_path),
                            }
                        )
                        logger.warning(
                            f"Suspicious stream found: {stream_name} "
                            f"(matches {suspicious_pattern})"
                        )

            if suspicious_streams:
                findings.append(
                    {
                        "type": "suspicious_ole_stream",
                        "severity": "high",
                        "description": f"Suspicious OLE streams found in {filename}",
                        "filename": filename,
                        "details": {
                            "stream_count": len(suspicious_streams),
                            "streams": suspicious_streams,
                        },
                    }
                )

            ole.close()

        except Exception as e:
            logger.error(f"Error analyzing stream names in {filename}: {str(e)}")
            findings.append(
                {
                    "type": "stream_analysis_error",
                    "severity": "low",
                    "description": f"Error analyzing stream names: {str(e)}",
                    "filename": filename,
                }
            )

        return findings

    def _analyze_ole_metadata(self, ole_bytes: bytes, filename: str) -> List[Dict]:
        """
        Analyze OLE file metadata using oletools OleID

        Args:
            ole_bytes: OLE file content as bytes
            filename: Filename for logging

        Returns:
            List of metadata findings
        """
        findings = []

        try:
            # Analyze with OleID
            ole_id = OleID(BytesIO(ole_bytes))
            indicators = ole_id.check()

            # Check for security-relevant indicators
            for indicator in indicators:
                if indicator.value:  # Indicator triggered
                    # Focus on high-risk indicators
                    if indicator.id in [
                        "ole_format",
                        "has_suminfo",
                        "word_doc",
                        "excel_doc",
                        "ppt_doc",
                        "visio_doc",
                        "encrypted",
                        "macros",
                        "vba",
                        "xlm",
                        "external_rels",
                        "flash",
                        "objectpool",
                    ]:
                        if indicator.id in ["macros", "vba", "flash"]:
                            # High risk indicators
                            logger.warning(
                                f"High-risk indicator: {indicator.name} in {filename}"
                            )
                            findings.append(
                                {
                                    "type": "ole_metadata_indicator",
                                    "severity": "high",
                                    "description": f"OLE metadata indicator: {indicator.name}",
                                    "filename": filename,
                                    "details": {
                                        "indicator_id": indicator.id,
                                        "indicator_name": indicator.name,
                                        "indicator_description": indicator.description,
                                    },
                                }
                            )

        except Exception as e:
            logger.error(f"Error analyzing OLE metadata in {filename}: {str(e)}")
            # Not adding error to findings - metadata analysis is optional

        return findings


# Module-level convenience function


def analyze_ole_file(
    ole_bytes: bytes, filename: str = "embedded.ole"
) -> Tuple[bool, List[Dict]]:
    """
    Convenience function to analyze OLE file

    Args:
        ole_bytes: OLE file content as bytes
        filename: Filename for logging

    Returns:
        Tuple of (has_threats, list_of_findings)
    """
    analyzer = OLEStreamAnalyzer()
    return analyzer.analyze_ole_file(ole_bytes, filename)
