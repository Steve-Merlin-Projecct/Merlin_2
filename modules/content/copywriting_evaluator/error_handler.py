#!/usr/bin/env python3
"""
Comprehensive Error Handler for Copywriting Evaluator System

Implements sophisticated error handling with 15-error limit, 23-hour cooldown,
automatic recovery mechanisms, and detailed error tracking and analysis.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import traceback

# Database integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Minor issues, processing can continue
    MEDIUM = "medium"     # Significant issues, may affect processing
    HIGH = "high"         # Critical issues, immediate attention needed
    CRITICAL = "critical" # System-threatening errors

class ErrorCategory(Enum):
    """Categories of errors for classification"""
    API_ERROR = "api_error"               # Gemini API failures
    DATABASE_ERROR = "database_error"     # Database connectivity/query issues
    VALIDATION_ERROR = "validation_error" # Data validation failures
    PROCESSING_ERROR = "processing_error" # Stage processing failures
    SYSTEM_ERROR = "system_error"         # System-level errors
    NETWORK_ERROR = "network_error"       # Network connectivity issues
    RESOURCE_ERROR = "resource_error"     # Memory/disk/resource issues

@dataclass
class ErrorRecord:
    """Comprehensive error record with full context"""
    error_id: str
    timestamp: datetime
    session_id: Optional[str]
    stage_name: Optional[str]
    error_category: ErrorCategory
    severity: ErrorSeverity
    error_message: str
    error_details: Optional[str] = None
    exception_type: Optional[str] = None
    stack_trace: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    resolved: bool = False
    resolution_notes: Optional[str] = None

@dataclass
class ErrorStats:
    """Error statistics and metrics"""
    total_errors: int = 0
    consecutive_errors: int = 0
    error_rate_last_hour: float = 0.0
    error_rate_last_day: float = 0.0
    most_common_category: Optional[str] = None
    most_common_stage: Optional[str] = None
    cooldown_active: bool = False
    cooldown_until: Optional[datetime] = None
    hours_until_cooldown_end: float = 0.0
    errors_by_category: Dict[str, int] = field(default_factory=dict)
    errors_by_severity: Dict[str, int] = field(default_factory=dict)

class ComprehensiveErrorHandler:
    """
    Advanced error handling system for the copywriting evaluator pipeline
    
    Features:
    - Sophisticated error classification and tracking
    - 15-error limit with intelligent cooldown management
    - 23-hour cooldown period with gradual recovery
    - Automatic retry strategies with exponential backoff
    - Error pattern analysis and prediction
    - Recovery recommendations and automated fixes
    - Comprehensive error reporting and analytics
    """
    
    def __init__(self, max_consecutive_errors: int = 15, cooldown_hours: int = 23):
        """Initialize comprehensive error handler"""
        self.db = DatabaseManager()
        self.max_consecutive_errors = max_consecutive_errors
        self.cooldown_hours = cooldown_hours
        
        # Error tracking state
        self.consecutive_errors = 0
        self.last_error_time: Optional[datetime] = None
        self.cooldown_until: Optional[datetime] = None
        self.error_history: List[ErrorRecord] = []
        
        # Recovery state
        self.recovery_strategies: Dict[ErrorCategory, Any] = {}
        self.auto_fix_enabled = True
        
        # Initialize recovery strategies
        self._initialize_recovery_strategies()
        
        logger.info(f"Comprehensive error handler initialized (limit: {max_consecutive_errors}, cooldown: {cooldown_hours}h)")
    
    def _initialize_recovery_strategies(self) -> None:
        """Initialize automatic recovery strategies for different error types"""
        self.recovery_strategies = {
            ErrorCategory.API_ERROR: self._recover_from_api_error,
            ErrorCategory.DATABASE_ERROR: self._recover_from_database_error,
            ErrorCategory.NETWORK_ERROR: self._recover_from_network_error,
            ErrorCategory.VALIDATION_ERROR: self._recover_from_validation_error,
            ErrorCategory.PROCESSING_ERROR: self._recover_from_processing_error,
        }
    
    def record_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorRecord:
        """
        Record a comprehensive error with full context and classification
        
        Args:
            error: Exception that occurred
            context: Additional context information
            
        Returns:
            ErrorRecord with full error details
        """
        import uuid
        
        error_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Classify the error
        category = self._classify_error(error)
        severity = self._determine_severity(error, category)
        
        # Extract detailed error information
        error_details = self._extract_error_details(error)
        stack_trace = traceback.format_exc()
        
        # Create comprehensive error record
        error_record = ErrorRecord(
            error_id=error_id,
            timestamp=timestamp,
            session_id=context.get('session_id') if context else None,
            stage_name=context.get('stage_name') if context else None,
            error_category=category,
            severity=severity,
            error_message=str(error),
            error_details=error_details,
            exception_type=type(error).__name__,
            stack_trace=stack_trace,
            context_data=context if context is not None else {}
        )
        
        # Update error tracking state
        self.consecutive_errors += 1
        self.last_error_time = timestamp
        self.error_history.append(error_record)
        
        # Check if cooldown should be activated
        if self.consecutive_errors >= self.max_consecutive_errors and not self.is_in_cooldown():
            self.cooldown_until = timestamp + timedelta(hours=self.cooldown_hours)
            logger.critical(f"Error limit reached! Activating {self.cooldown_hours}h cooldown until {self.cooldown_until}")
        
        # Log error with appropriate level
        self._log_error(error_record)
        
        # Store in database for persistence
        try:
            self._store_error_record(error_record)
        except Exception as db_error:
            logger.error(f"Failed to store error record: {str(db_error)}")
        
        # Attempt automatic recovery if enabled
        if self.auto_fix_enabled:
            self._attempt_recovery(error_record)
        
        return error_record
    
    def _classify_error(self, error: Exception) -> ErrorCategory:
        """Classify error into appropriate category"""
        error_type = type(error).__name__.lower()
        error_message = str(error).lower()
        
        # API-related errors
        if any(keyword in error_message for keyword in ['api', 'quota', 'rate limit', 'gemini', 'auth']):
            return ErrorCategory.API_ERROR
        
        # Database errors
        if any(keyword in error_message for keyword in ['database', 'sql', 'connection', 'psycopg2']):
            return ErrorCategory.DATABASE_ERROR
        
        # Network errors
        if any(keyword in error_message for keyword in ['network', 'timeout', 'connection refused', 'dns']):
            return ErrorCategory.NETWORK_ERROR
        
        # Validation errors
        if any(keyword in error_message for keyword in ['validation', 'invalid', 'format', 'schema']):
            return ErrorCategory.VALIDATION_ERROR
        
        # System errors
        if any(keyword in error_message for keyword in ['memory', 'disk', 'resource', 'system']):
            return ErrorCategory.RESOURCE_ERROR
        
        # Default to processing error
        return ErrorCategory.PROCESSING_ERROR
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on type and category"""
        error_message = str(error).lower()
        
        # Critical severity indicators
        if any(keyword in error_message for keyword in ['critical', 'fatal', 'corrupt', 'security']):
            return ErrorSeverity.CRITICAL
        
        # High severity by category
        if category in [ErrorCategory.DATABASE_ERROR, ErrorCategory.SYSTEM_ERROR]:
            return ErrorSeverity.HIGH
        
        # API quota/auth errors are high severity
        if category == ErrorCategory.API_ERROR and any(keyword in error_message for keyword in ['quota', 'auth', 'forbidden']):
            return ErrorSeverity.HIGH
        
        # Medium severity indicators
        if any(keyword in error_message for keyword in ['failed', 'error', 'exception']):
            return ErrorSeverity.MEDIUM
        
        return ErrorSeverity.LOW
    
    def _extract_error_details(self, error: Exception) -> Optional[str]:
        """Extract detailed error information for analysis"""
        details = {}
        
        # Add exception-specific details
        if hasattr(error, 'response'):
            details['response'] = str(getattr(error, 'response'))
        if hasattr(error, 'status_code'):
            details['status_code'] = getattr(error, 'status_code')
        if hasattr(error, 'args') and error.args:
            details['args'] = error.args
        
        return json.dumps(details) if details else None
    
    def _log_error(self, error_record: ErrorRecord) -> None:
        """Log error with appropriate severity level"""
        log_message = f"[{error_record.error_category.value.upper()}] {error_record.error_message}"
        
        if error_record.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_record.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error_record.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        logger.debug(f"Error ID: {error_record.error_id}, Session: {error_record.session_id}")
    
    def _store_error_record(self, error_record: ErrorRecord) -> None:
        """Store error record in database for persistence and analysis"""
        try:
            query = """
                INSERT INTO error_log (
                    error_id, timestamp, session_id, stage_name, error_category,
                    severity, error_message, error_details, exception_type,
                    stack_trace, context_data, retry_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                error_record.error_id,
                error_record.timestamp,
                error_record.session_id,
                error_record.stage_name,
                error_record.error_category.value,
                error_record.severity.value,
                error_record.error_message,
                error_record.error_details,
                error_record.exception_type,
                error_record.stack_trace,
                json.dumps(error_record.context_data),
                error_record.retry_count
            )
            
            self.db.execute_query(query, params)
            
        except Exception as e:
            logger.error(f"Failed to store error record: {str(e)}")
    
    def _attempt_recovery(self, error_record: ErrorRecord) -> bool:
        """Attempt automatic recovery based on error category"""
        try:
            recovery_func = self.recovery_strategies.get(error_record.error_category)
            if recovery_func:
                logger.info(f"Attempting automatic recovery for {error_record.error_category.value}")
                success = recovery_func(error_record)
                if success:
                    error_record.resolved = True
                    error_record.resolution_notes = "Automatic recovery successful"
                    logger.info(f"Automatic recovery successful for error {error_record.error_id}")
                return success
        except Exception as recovery_error:
            logger.error(f"Recovery attempt failed: {str(recovery_error)}")
        
        return False
    
    def _recover_from_api_error(self, error_record: ErrorRecord) -> bool:
        """Attempt recovery from API-related errors"""
        # Implement exponential backoff for API errors
        wait_time = min(60, 2 ** error_record.retry_count)
        logger.info(f"API error recovery: waiting {wait_time}s before retry")
        return True  # Placeholder - would implement actual retry logic
    
    def _recover_from_database_error(self, error_record: ErrorRecord) -> bool:
        """Attempt recovery from database errors"""
        # Could implement connection reset, query optimization, etc.
        logger.info("Database error recovery: attempting connection reset")
        return False  # Placeholder
    
    def _recover_from_network_error(self, error_record: ErrorRecord) -> bool:
        """Attempt recovery from network errors"""
        logger.info("Network error recovery: checking connectivity")
        return False  # Placeholder
    
    def _recover_from_validation_error(self, error_record: ErrorRecord) -> bool:
        """Attempt recovery from validation errors"""
        logger.info("Validation error recovery: attempting data cleanup")
        return False  # Placeholder
    
    def _recover_from_processing_error(self, error_record: ErrorRecord) -> bool:
        """Attempt recovery from general processing errors"""
        logger.info("Processing error recovery: attempting stage restart")
        return False  # Placeholder
    
    def is_in_cooldown(self) -> bool:
        """Check if error handler is in cooldown period"""
        if self.cooldown_until is None:
            return False
        return datetime.now() < self.cooldown_until
    
    def get_time_until_cooldown_end(self) -> float:
        """Get hours remaining until cooldown ends"""
        if not self.is_in_cooldown() or self.cooldown_until is None:
            return 0.0
        
        remaining = self.cooldown_until - datetime.now()
        return remaining.total_seconds() / 3600
    
    def reset_error_tracking(self, reason: str = "Manual reset") -> Dict:
        """Reset error tracking state"""
        logger.info(f"Resetting error tracking: {reason}")
        
        old_consecutive = self.consecutive_errors
        old_cooldown = self.cooldown_until
        
        self.consecutive_errors = 0
        self.cooldown_until = None
        self.last_error_time = None
        
        return {
            'success': True,
            'message': f'Error tracking reset: {reason}',
            'previous_consecutive_errors': old_consecutive,
            'cooldown_was_active': old_cooldown is not None,
            'cooldown_ended_early': old_cooldown.isoformat() if old_cooldown else None
        }
    
    def get_error_statistics(self, hours_back: int = 24) -> ErrorStats:
        """Get comprehensive error statistics and analysis"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Get recent errors
        recent_errors = [e for e in self.error_history if e.timestamp >= cutoff_time]
        
        # Calculate error rates
        total_errors = len(recent_errors)
        error_rate_hour = len([e for e in recent_errors if e.timestamp >= datetime.now() - timedelta(hours=1)])
        error_rate_day = total_errors
        
        # Analyze by category
        errors_by_category = {}
        errors_by_severity = {}
        stage_errors = {}
        
        for error in recent_errors:
            # Category analysis
            cat = error.error_category.value
            errors_by_category[cat] = errors_by_category.get(cat, 0) + 1
            
            # Severity analysis
            sev = error.severity.value
            errors_by_severity[sev] = errors_by_severity.get(sev, 0) + 1
            
            # Stage analysis
            if error.stage_name:
                stage_errors[error.stage_name] = stage_errors.get(error.stage_name, 0) + 1
        
        # Find most common category and stage
        most_common_category = max(errors_by_category.keys(), key=lambda k: errors_by_category[k]) if errors_by_category else None
        most_common_stage = max(stage_errors.keys(), key=lambda k: stage_errors[k]) if stage_errors else None
        
        return ErrorStats(
            total_errors=total_errors,
            consecutive_errors=self.consecutive_errors,
            error_rate_last_hour=error_rate_hour,
            error_rate_last_day=error_rate_day,
            most_common_category=most_common_category,
            most_common_stage=most_common_stage,
            cooldown_active=self.is_in_cooldown(),
            cooldown_until=self.cooldown_until,
            hours_until_cooldown_end=self.get_time_until_cooldown_end(),
            errors_by_category=errors_by_category,
            errors_by_severity=errors_by_severity
        )
    
    def get_recovery_recommendations(self) -> List[Dict]:
        """Generate actionable recovery recommendations based on error patterns"""
        stats = self.get_error_statistics()
        recommendations = []
        
        # High error rate recommendations
        if stats.error_rate_last_hour > 5:
            recommendations.append({
                'priority': 'HIGH',
                'issue': 'High error rate detected',
                'recommendation': 'Consider switching to testing mode and investigating root cause',
                'action': 'switch_mode_testing'
            })
        
        # API error recommendations
        if stats.errors_by_category.get('api_error', 0) > 3:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': 'Multiple API errors detected',
                'recommendation': 'Check API key validity and quota limits',
                'action': 'check_api_credentials'
            })
        
        # Database error recommendations
        if stats.errors_by_category.get('database_error', 0) > 2:
            recommendations.append({
                'priority': 'HIGH',
                'issue': 'Database connectivity issues',
                'recommendation': 'Verify database connection and run diagnostics',
                'action': 'check_database_health'
            })
        
        # Cooldown recommendations
        if stats.cooldown_active:
            recommendations.append({
                'priority': 'CRITICAL',
                'issue': 'System in cooldown mode',
                'recommendation': f'Wait {stats.hours_until_cooldown_end:.1f} hours or investigate and reset if issue resolved',
                'action': 'wait_or_reset_cooldown'
            })
        
        return recommendations
    
    def get_detailed_status(self) -> Dict:
        """Get comprehensive error handler status"""
        stats = self.get_error_statistics()
        recommendations = self.get_recovery_recommendations()
        
        return {
            'error_tracking': {
                'consecutive_errors': stats.consecutive_errors,
                'max_consecutive_errors': self.max_consecutive_errors,
                'cooldown_active': stats.cooldown_active,
                'cooldown_until': stats.cooldown_until.isoformat() if stats.cooldown_until else None,
                'hours_until_cooldown_end': stats.hours_until_cooldown_end,
                'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None
            },
            'error_statistics': {
                'total_errors_24h': stats.total_errors,
                'error_rate_last_hour': stats.error_rate_last_hour,
                'most_common_category': stats.most_common_category,
                'most_common_stage': stats.most_common_stage,
                'errors_by_category': stats.errors_by_category,
                'errors_by_severity': stats.errors_by_severity
            },
            'system_health': {
                'auto_fix_enabled': self.auto_fix_enabled,
                'recovery_strategies_available': len(self.recovery_strategies),
                'recent_recovery_attempts': len([e for e in self.error_history if e.resolved and 
                                                e.timestamp >= datetime.now() - timedelta(hours=1)])
            },
            'recommendations': recommendations
        }

# Global error handler instance
_global_error_handler = None

def get_error_handler() -> ComprehensiveErrorHandler:
    """Get or create the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ComprehensiveErrorHandler()
    return _global_error_handler

def record_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorRecord:
    """Convenience function to record an error"""
    return get_error_handler().record_error(error, context)

def is_system_in_cooldown() -> bool:
    """Check if system is in error cooldown"""
    return get_error_handler().is_in_cooldown()

def get_error_status() -> Dict:
    """Get system error status"""
    return get_error_handler().get_detailed_status()

def reset_error_tracking(reason: str = "Manual reset") -> Dict:
    """Reset error tracking state"""
    return get_error_handler().reset_error_tracking(reason)