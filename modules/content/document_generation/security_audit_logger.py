"""
Security Audit Trail Logger

This module provides comprehensive audit logging for document security scanning.
All security scans are logged with timestamps, threat details, and outcomes
to maintain a complete audit trail for compliance and forensic analysis.

Features:
- JSON-formatted audit logs
- Log rotation and archival
- Thread-safe logging
- Query and reporting capabilities

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading

logger = logging.getLogger(__name__)


class SecurityAuditLogger:
    """
    Maintains audit trail of all document security scans

    Logs include:
    - Scan timestamp
    - File path
    - Security scan results
    - Threat details
    - Document metadata
    """

    def __init__(self, log_dir: str = "logs/security_audit"):
        """
        Initialize security audit logger

        Args:
            log_dir: Directory for security audit logs (default: logs/security_audit)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Thread lock for concurrent logging
        self.lock = threading.Lock()

        # Current log file (rotates daily)
        self.current_log_file = self._get_current_log_file()

        logger.info(f"Security audit logger initialized: {self.log_dir}")

    def _get_current_log_file(self) -> Path:
        """
        Get current log file path (rotates daily)

        Returns:
            Path to today's log file
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"security_audit_{today}.jsonl"

    def log_scan(self, scan_data: Dict) -> None:
        """
        Log a security scan event

        Args:
            scan_data: Dictionary containing scan results and metadata
        """
        try:
            with self.lock:
                # Add timestamp
                audit_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "security_scan",
                    **scan_data,
                }

                # Check if we need to rotate log file
                current_file = self._get_current_log_file()
                if current_file != self.current_log_file:
                    self.current_log_file = current_file

                # Write to JSONL (JSON Lines) format
                with open(self.current_log_file, "a") as f:
                    f.write(json.dumps(audit_entry) + "\n")

                logger.debug(
                    f"Logged security scan: {scan_data.get('file_path', 'unknown')}"
                )

        except Exception as e:
            logger.error(f"Failed to write security audit log: {str(e)}")

    def log_threat_blocked(self, file_path: str, threat_data: Dict) -> None:
        """
        Log when a document is blocked due to security threats

        Args:
            file_path: Path to blocked document
            threat_data: Details about detected threats
        """
        try:
            with self.lock:
                audit_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "threat_blocked",
                    "file_path": file_path,
                    "threat_data": threat_data,
                    "action": "document_rejected",
                }

                with open(self.current_log_file, "a") as f:
                    f.write(json.dumps(audit_entry) + "\n")

                logger.warning(f"Logged threat block: {file_path}")

        except Exception as e:
            logger.error(f"Failed to log threat block: {str(e)}")

    def get_recent_scans(self, limit: int = 100, days: int = 7) -> List[Dict]:
        """
        Retrieve recent security scan logs

        Args:
            limit: Maximum number of entries to return
            days: Number of days to look back

        Returns:
            List of scan entries (most recent first)
        """
        try:
            entries = []

            # Get log files for the specified number of days
            log_files = self._get_log_files_for_days(days)

            for log_file in reversed(log_files):  # Most recent first
                if not log_file.exists():
                    continue

                with open(log_file, "r") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            entries.append(entry)

                            if len(entries) >= limit:
                                return entries

                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in audit log: {line}")
                            continue

            return entries

        except Exception as e:
            logger.error(f"Error retrieving recent scans: {str(e)}")
            return []

    def get_threat_summary(self, days: int = 30) -> Dict:
        """
        Generate summary of threats detected over specified period

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with threat statistics
        """
        try:
            log_files = self._get_log_files_for_days(days)

            stats = {
                "period_days": days,
                "total_scans": 0,
                "safe_documents": 0,
                "unsafe_documents": 0,
                "threats_by_type": {},
                "threats_by_severity": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                },
            }

            for log_file in log_files:
                if not log_file.exists():
                    continue

                with open(log_file, "r") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())

                            if entry.get("event_type") != "security_scan":
                                continue

                            stats["total_scans"] += 1

                            if entry.get("is_safe"):
                                stats["safe_documents"] += 1
                            else:
                                stats["unsafe_documents"] += 1

                            # Analyze threat details
                            scan_report = entry.get("scan_report", {})
                            threats = scan_report.get("threats", [])

                            for threat in threats:
                                threat_type = threat.get("threat_type", "unknown")
                                severity = threat.get("severity", "unknown")

                                # Count by type
                                stats["threats_by_type"][threat_type] = (
                                    stats["threats_by_type"].get(threat_type, 0) + 1
                                )

                                # Count by severity
                                if severity in stats["threats_by_severity"]:
                                    stats["threats_by_severity"][severity] += 1

                        except json.JSONDecodeError:
                            continue

            return stats

        except Exception as e:
            logger.error(f"Error generating threat summary: {str(e)}")
            return {}

    def _get_log_files_for_days(self, days: int) -> List[Path]:
        """
        Get list of log files for specified number of days

        Args:
            days: Number of days to look back

        Returns:
            List of Path objects for log files
        """
        from datetime import timedelta

        log_files = []
        today = datetime.now().date()

        for i in range(days):
            date = today - timedelta(days=i)
            log_file = (
                self.log_dir / f"security_audit_{date.strftime('%Y-%m-%d')}.jsonl"
            )
            log_files.append(log_file)

        return log_files

    def export_report(self, output_path: str, days: int = 30) -> bool:
        """
        Export threat summary report to file

        Args:
            output_path: Path to write report
            days: Number of days to include in report

        Returns:
            True if export successful
        """
        try:
            summary = self.get_threat_summary(days)

            report = {
                "report_generated": datetime.now().isoformat(),
                "period_days": days,
                "summary": summary,
                "recent_scans": self.get_recent_scans(limit=50, days=days),
            }

            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"Exported security report to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export report: {str(e)}")
            return False

    def query_by_file(self, file_path: str) -> List[Dict]:
        """
        Query audit logs for specific file

        Args:
            file_path: File path to search for

        Returns:
            List of audit entries for the file
        """
        try:
            entries = []

            # Search all log files
            for log_file in self.log_dir.glob("security_audit_*.jsonl"):
                with open(log_file, "r") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if entry.get("file_path") == file_path:
                                entries.append(entry)
                        except json.JSONDecodeError:
                            continue

            return entries

        except Exception as e:
            logger.error(f"Error querying by file: {str(e)}")
            return []

    def cleanup_old_logs(self, keep_days: int = 90) -> int:
        """
        Clean up audit logs older than specified days

        Args:
            keep_days: Number of days to keep (default: 90)

        Returns:
            Number of log files deleted
        """
        try:
            from datetime import timedelta

            deleted_count = 0
            cutoff_date = datetime.now().date() - timedelta(days=keep_days)

            for log_file in self.log_dir.glob("security_audit_*.jsonl"):
                # Extract date from filename
                try:
                    date_str = log_file.stem.replace("security_audit_", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                    if file_date < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old audit log: {log_file}")

                except (ValueError, OSError) as e:
                    logger.warning(f"Error processing log file {log_file}: {e}")
                    continue

            logger.info(f"Cleaned up {deleted_count} old audit logs")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up old logs: {str(e)}")
            return 0


# Module-level convenience functions


def log_security_scan(scan_data: Dict, log_dir: str = "logs/security_audit") -> None:
    """
    Convenience function to log a security scan

    Args:
        scan_data: Scan results and metadata
        log_dir: Directory for audit logs
    """
    logger_instance = SecurityAuditLogger(log_dir=log_dir)
    logger_instance.log_scan(scan_data)


def get_threat_summary(days: int = 30, log_dir: str = "logs/security_audit") -> Dict:
    """
    Convenience function to get threat summary

    Args:
        days: Number of days to analyze
        log_dir: Directory containing audit logs

    Returns:
        Threat statistics dictionary
    """
    logger_instance = SecurityAuditLogger(log_dir=log_dir)
    return logger_instance.get_threat_summary(days=days)
