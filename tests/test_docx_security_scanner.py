"""
Comprehensive Tests for DOCX Security Scanner

Tests all security scanning functionality including:
- Remote template detection
- OLE object inspection
- ZIP structure validation
- External reference detection
- XML bomb detection
- Security audit logging

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import pytest
import zipfile
import tempfile
from pathlib import Path
from io import BytesIO

from modules.content.document_generation.docx_security_scanner import (
    DOCXSecurityScanner,
    SecurityThreat,
    scan_docx_file,
    scan_docx_bytes
)
from modules.content.document_generation.security_audit_logger import SecurityAuditLogger


class TestSecurityThreat:
    """Test SecurityThreat class"""

    def test_security_threat_creation(self):
        """Test creating a security threat object"""
        threat = SecurityThreat(
            threat_type="remote_template",
            severity="critical",
            description="Remote template detected",
            location="word/settings.xml",
            details={"template_id": "rId1"}
        )

        assert threat.threat_type == "remote_template"
        assert threat.severity == "critical"
        assert threat.description == "Remote template detected"
        assert threat.location == "word/settings.xml"
        assert threat.details["template_id"] == "rId1"
        assert threat.timestamp is not None

    def test_threat_to_dict(self):
        """Test converting threat to dictionary"""
        threat = SecurityThreat(
            threat_type="ole_object",
            severity="high",
            description="OLE object detected"
        )

        threat_dict = threat.to_dict()

        assert threat_dict["threat_type"] == "ole_object"
        assert threat_dict["severity"] == "high"
        assert threat_dict["description"] == "OLE object detected"
        assert "timestamp" in threat_dict


class TestDOCXSecurityScanner:
    """Test DOCX Security Scanner functionality"""

    @pytest.fixture
    def scanner(self):
        """Create scanner instance for testing"""
        return DOCXSecurityScanner(strict_mode=True)

    @pytest.fixture
    def safe_docx(self, tmp_path):
        """Create a safe DOCX file for testing"""
        docx_path = tmp_path / "safe_document.docx"

        # Create minimal valid DOCX structure
        with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add required files
            zf.writestr('[Content_Types].xml', self._get_content_types_xml())
            zf.writestr('_rels/.rels', self._get_rels_xml())
            zf.writestr('word/document.xml', self._get_document_xml())
            zf.writestr('word/_rels/document.xml.rels', self._get_document_rels_xml())

        return str(docx_path)

    @pytest.fixture
    def malicious_docx_remote_template(self, tmp_path):
        """Create DOCX with remote template reference"""
        docx_path = tmp_path / "malicious_remote_template.docx"

        with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml', self._get_content_types_xml())
            zf.writestr('_rels/.rels', self._get_rels_xml())
            zf.writestr('word/document.xml', self._get_document_xml())
            zf.writestr('word/_rels/document.xml.rels', self._get_document_rels_xml())

            # Add settings.xml with remote template reference
            settings_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
    <w:attachedTemplate r:id="rId1"/>
</w:settings>'''
            zf.writestr('word/settings.xml', settings_xml)

        return str(docx_path)

    @pytest.fixture
    def malicious_docx_ole_object(self, tmp_path):
        """Create DOCX with OLE object"""
        docx_path = tmp_path / "malicious_ole_object.docx"

        with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml', self._get_content_types_xml())
            zf.writestr('_rels/.rels', self._get_rels_xml())

            # Add document with OLE object reference
            doc_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:o="urn:schemas-microsoft-com:office:office">
    <w:body>
        <w:p>
            <w:r>
                <w:object>
                    <o:OLEObject Type="Embed" ProgID="Package"/>
                </w:object>
            </w:r>
        </w:p>
    </w:body>
</w:document>'''
            zf.writestr('word/document.xml', doc_xml)
            zf.writestr('word/_rels/document.xml.rels', self._get_document_rels_xml())

            # Add fake OLE object file
            zf.writestr('word/embeddings/oleObject1.bin', b'fake_ole_content')

        return str(docx_path)

    @pytest.fixture
    def malicious_docx_xml_bomb(self, tmp_path):
        """Create DOCX with XML entity definitions"""
        docx_path = tmp_path / "malicious_xml_bomb.docx"

        with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml', self._get_content_types_xml())
            zf.writestr('_rels/.rels', self._get_rels_xml())

            # Add document with DOCTYPE and entities
            doc_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE w:document [
    <!ENTITY lol "lol">
    <!ENTITY lol2 "&lol;&lol;">
]>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p><w:r><w:t>&lol2;</w:t></w:r></w:p>
    </w:body>
</w:document>'''
            zf.writestr('word/document.xml', doc_xml)
            zf.writestr('word/_rels/document.xml.rels', self._get_document_rels_xml())

        return str(docx_path)

    def _get_content_types_xml(self):
        """Get minimal [Content_Types].xml"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

    def _get_rels_xml(self):
        """Get minimal _rels/.rels"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

    def _get_document_xml(self):
        """Get minimal word/document.xml"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p><w:r><w:t>Test document</w:t></w:r></w:p>
    </w:body>
</w:document>'''

    def _get_document_rels_xml(self):
        """Get minimal word/_rels/document.xml.rels"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>'''

    def test_scanner_initialization(self, scanner):
        """Test scanner initializes correctly"""
        assert scanner.strict_mode is True
        assert scanner.threats == []
        assert scanner.NAMESPACES is not None

    def test_scan_safe_document(self, scanner, safe_docx):
        """Test scanning a safe document"""
        is_safe, threats = scanner.scan_file(safe_docx)

        assert is_safe is True
        assert len(threats) == 0

    def test_detect_remote_template(self, scanner, malicious_docx_remote_template):
        """Test detection of remote template reference"""
        is_safe, threats = scanner.scan_file(malicious_docx_remote_template)

        assert is_safe is False
        assert len(threats) > 0

        # Find remote template threat
        remote_template_threats = [t for t in threats if t.threat_type == "remote_template"]
        assert len(remote_template_threats) > 0
        assert remote_template_threats[0].severity == "critical"

    def test_detect_ole_object(self, scanner, malicious_docx_ole_object):
        """Test detection of OLE objects"""
        is_safe, threats = scanner.scan_file(malicious_docx_ole_object)

        # Should detect OLE object
        ole_threats = [t for t in threats if "ole" in t.threat_type.lower()]
        assert len(ole_threats) > 0

    def test_detect_xml_entities(self, scanner, malicious_docx_xml_bomb):
        """Test detection of XML entities"""
        is_safe, threats = scanner.scan_file(malicious_docx_xml_bomb)

        # Should detect XML entities
        xml_threats = [t for t in threats if "xml" in t.threat_type.lower()]
        assert len(xml_threats) > 0

    def test_invalid_zip_file(self, scanner, tmp_path):
        """Test handling of invalid ZIP file"""
        invalid_file = tmp_path / "invalid.docx"
        invalid_file.write_text("This is not a valid DOCX file")

        is_safe, threats = scanner.scan_file(str(invalid_file))

        assert is_safe is False
        assert len(threats) > 0

        # Should detect invalid ZIP
        zip_threats = [t for t in threats if "zip" in t.threat_type.lower()]
        assert len(zip_threats) > 0

    def test_scan_nonexistent_file(self, scanner):
        """Test handling of nonexistent file"""
        is_safe, threats = scanner.scan_file("/nonexistent/file.docx")

        assert is_safe is False
        assert len(threats) > 0
        assert threats[0].threat_type == "file_not_found"

    def test_scan_bytes(self, scanner, safe_docx):
        """Test scanning from bytes"""
        with open(safe_docx, 'rb') as f:
            docx_bytes = f.read()

        is_safe, threats = scanner.scan_bytes(docx_bytes, "test.docx")

        assert is_safe is True
        assert len(threats) == 0

    def test_get_scan_report(self, scanner, safe_docx):
        """Test generating scan report"""
        scanner.scan_file(safe_docx)
        report = scanner.get_scan_report()

        assert "timestamp" in report
        assert "total_threats" in report
        assert "severity_counts" in report
        assert "is_safe" in report
        assert "strict_mode" in report
        assert "threats" in report

    def test_strict_mode_vs_permissive(self, safe_docx):
        """Test difference between strict and permissive modes"""
        strict_scanner = DOCXSecurityScanner(strict_mode=True)
        permissive_scanner = DOCXSecurityScanner(strict_mode=False)

        # Both should pass safe document
        is_safe_strict, _ = strict_scanner.scan_file(safe_docx)
        is_safe_permissive, _ = permissive_scanner.scan_file(safe_docx)

        assert is_safe_strict is True
        assert is_safe_permissive is True

    def test_convenience_function_scan_file(self, safe_docx):
        """Test convenience function for file scanning"""
        is_safe, report = scan_docx_file(safe_docx, strict_mode=True)

        assert is_safe is True
        assert "total_threats" in report

    def test_convenience_function_scan_bytes(self, safe_docx):
        """Test convenience function for bytes scanning"""
        with open(safe_docx, 'rb') as f:
            docx_bytes = f.read()

        is_safe, report = scan_docx_bytes(docx_bytes, "test.docx", strict_mode=True)

        assert is_safe is True
        assert "total_threats" in report


class TestSecurityAuditLogger:
    """Test Security Audit Logger functionality"""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create logger instance with temporary directory"""
        log_dir = tmp_path / "audit_logs"
        return SecurityAuditLogger(log_dir=str(log_dir))

    def test_logger_initialization(self, logger):
        """Test logger initializes correctly"""
        assert logger.log_dir.exists()
        assert logger.current_log_file is not None

    def test_log_scan(self, logger):
        """Test logging a security scan"""
        scan_data = {
            "file_path": "/test/document.docx",
            "is_safe": True,
            "threat_count": 0,
            "scan_report": {"total_threats": 0}
        }

        logger.log_scan(scan_data)

        # Check log file exists
        assert logger.current_log_file.exists()

        # Read log file and verify entry
        with open(logger.current_log_file, 'r') as f:
            content = f.read()
            assert "/test/document.docx" in content
            assert "security_scan" in content

    def test_log_threat_blocked(self, logger):
        """Test logging a blocked threat"""
        threat_data = {
            "threat_type": "remote_template",
            "severity": "critical"
        }

        logger.log_threat_blocked("/test/malicious.docx", threat_data)

        assert logger.current_log_file.exists()

        with open(logger.current_log_file, 'r') as f:
            content = f.read()
            assert "threat_blocked" in content
            assert "remote_template" in content

    def test_get_recent_scans(self, logger):
        """Test retrieving recent scans"""
        # Log a few scans
        for i in range(5):
            scan_data = {
                "file_path": f"/test/document_{i}.docx",
                "is_safe": True,
                "threat_count": 0
            }
            logger.log_scan(scan_data)

        recent = logger.get_recent_scans(limit=10, days=1)

        assert len(recent) == 5
        assert recent[0]["event_type"] == "security_scan"

    def test_get_threat_summary(self, logger):
        """Test generating threat summary"""
        # Log scans with various threats
        scan_data_safe = {
            "file_path": "/test/safe.docx",
            "is_safe": True,
            "threat_count": 0,
            "scan_report": {"threats": []}
        }

        scan_data_unsafe = {
            "file_path": "/test/unsafe.docx",
            "is_safe": False,
            "threat_count": 2,
            "scan_report": {
                "threats": [
                    {"threat_type": "remote_template", "severity": "critical"},
                    {"threat_type": "ole_object", "severity": "high"}
                ]
            }
        }

        logger.log_scan(scan_data_safe)
        logger.log_scan(scan_data_unsafe)

        summary = logger.get_threat_summary(days=1)

        assert summary["total_scans"] == 2
        assert summary["safe_documents"] == 1
        assert summary["unsafe_documents"] == 1
        assert summary["threats_by_severity"]["critical"] == 1
        assert summary["threats_by_severity"]["high"] == 1

    def test_export_report(self, logger, tmp_path):
        """Test exporting security report"""
        # Log some scans
        scan_data = {
            "file_path": "/test/document.docx",
            "is_safe": True,
            "threat_count": 0,
            "scan_report": {"threats": []}
        }
        logger.log_scan(scan_data)

        # Export report
        report_path = tmp_path / "security_report.json"
        success = logger.export_report(str(report_path), days=1)

        assert success is True
        assert report_path.exists()

        # Verify report content
        import json
        with open(report_path, 'r') as f:
            report = json.load(f)

        assert "report_generated" in report
        assert "summary" in report
        assert "recent_scans" in report

    def test_query_by_file(self, logger):
        """Test querying logs by file path"""
        target_file = "/test/target.docx"

        # Log multiple scans
        for i in range(3):
            scan_data = {
                "file_path": target_file if i == 1 else f"/test/other_{i}.docx",
                "is_safe": True,
                "threat_count": 0
            }
            logger.log_scan(scan_data)

        results = logger.query_by_file(target_file)

        assert len(results) == 1
        assert results[0]["file_path"] == target_file

    def test_cleanup_old_logs(self, logger, tmp_path):
        """Test cleaning up old audit logs"""
        # Create old log file (simulate)
        old_log = logger.log_dir / "security_audit_2020-01-01.jsonl"
        old_log.write_text('{"test": "data"}\n')

        deleted_count = logger.cleanup_old_logs(keep_days=90)

        # Old log should be deleted
        assert not old_log.exists()
        assert deleted_count >= 1


class TestIntegration:
    """Integration tests for security scanner and audit logger"""

    @pytest.fixture
    def scanner(self):
        """Create scanner for integration tests"""
        return DOCXSecurityScanner(strict_mode=True)

    @pytest.fixture
    def logger(self, tmp_path):
        """Create logger for integration tests"""
        log_dir = tmp_path / "audit_logs"
        return SecurityAuditLogger(log_dir=str(log_dir))

    def test_scan_and_log_workflow(self, scanner, logger, tmp_path):
        """Test complete scan and log workflow"""
        # Create test document
        docx_path = tmp_path / "test.docx"

        with zipfile.ZipFile(docx_path, 'w') as zf:
            zf.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types/>')
            zf.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships/>')

        # Scan document
        is_safe, threats = scanner.scan_file(str(docx_path))
        scan_report = scanner.get_scan_report()

        # Log results
        audit_entry = {
            "file_path": str(docx_path),
            "is_safe": is_safe,
            "threat_count": len(threats),
            "scan_report": scan_report
        }
        logger.log_scan(audit_entry)

        # Verify logging worked
        recent = logger.get_recent_scans(limit=1, days=1)
        assert len(recent) == 1
        assert recent[0]["file_path"] == str(docx_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
