#!/usr/bin/env python3
"""
Performance Tracker for Copywriting Evaluator System

Tracks API performance metrics, error rates, and processing statistics for
Gemini AI calls across all pipeline stages. Provides data for dashboard
analytics and cost optimization.

Author: Automated Job Application System  
Version: 1.0.0
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Database integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

@dataclass
class APIMetrics:
    """Metrics for a single API call"""
    stage_name: str
    api_call_type: str
    response_time_ms: Optional[int]
    success: bool
    error_message: Optional[str] = None
    cost_estimate: Optional[float] = None
    batch_size: Optional[int] = None
    sentences_processed: Optional[int] = None
    model_used: Optional[str] = None
    session_id: Optional[str] = None

class PerformanceTracker:
    """
    Tracks performance metrics for Gemini API calls and pipeline processing
    
    Features:
    - API response time monitoring
    - Error rate tracking
    - Cost estimation and tracking  
    - Batch processing efficiency metrics
    - Stage-specific performance data
    - Session grouping for related calls
    """
    
    def __init__(self):
        """Initialize performance tracker"""
        self.db = DatabaseManager()
        logger.info("Performance tracker initialized")
    
    def log_api_call(self, metrics: APIMetrics) -> None:
        """
        Log a single API call performance metrics
        
        Args:
            metrics: APIMetrics object with call details
        """
        try:
            query = """
                INSERT INTO performance_metrics (
                    stage_name, api_call_type, response_time_ms, success,
                    error_message, cost_estimate, batch_size, sentences_processed,
                    model_used, session_id, processing_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                metrics.stage_name,
                metrics.api_call_type,
                metrics.response_time_ms,
                metrics.success,
                metrics.error_message,
                metrics.cost_estimate,
                metrics.batch_size,
                metrics.sentences_processed,
                metrics.model_used,
                metrics.session_id,
                datetime.now()
            )
            
            self.db.execute_query(query, params)
            
        except Exception as e:
            logger.error(f"Failed to log API metrics: {str(e)}")
            # Don't raise - performance tracking shouldn't break main processing
    
    def log_batch_metrics(self, stage_name: str, batch_metrics: List[APIMetrics]) -> None:
        """
        Log metrics for a batch of API calls
        
        Args:
            stage_name: Processing stage name
            batch_metrics: List of APIMetrics for the batch
        """
        for metrics in batch_metrics:
            self.log_api_call(metrics)
        
        logger.info(f"Logged {len(batch_metrics)} API calls for {stage_name}")
    
    async def log_pipeline_session(self, stats: Any) -> None:
        """
        Log overall pipeline session statistics
        
        Args:
            stats: ProcessingStats object from pipeline session
        """
        try:
            # Create session summary metrics
            session_metrics = APIMetrics(
                stage_name="pipeline_session",
                api_call_type="session_summary",
                response_time_ms=None,
                success=stats.error_count == 0,
                error_message=None if stats.error_count == 0 else f"{stats.error_count} errors occurred",
                batch_size=stats.total_sentences,
                sentences_processed=stats.processed_sentences,
                session_id=stats.session_id
            )
            
            self.log_api_call(session_metrics)
            
        except Exception as e:
            logger.error(f"Failed to log pipeline session: {str(e)}")
    
    async def log_error(self, error_info: Dict) -> None:
        """
        Log error information for debugging
        
        Args:
            error_info: Dictionary with error details
        """
        try:
            error_metrics = APIMetrics(
                stage_name=error_info.get('stage_name', 'unknown'),
                api_call_type="error",
                response_time_ms=None,
                success=False,
                error_message=error_info.get('error_message', 'Unknown error'),
                session_id=error_info.get('session_id')
            )
            
            self.log_api_call(error_metrics)
            
        except Exception as e:
            logger.error(f"Failed to log error info: {str(e)}")
    
    def get_stage_performance(self, stage_name: str, hours_back: int = 24) -> Dict:
        """
        Get performance metrics for a specific stage
        
        Args:
            stage_name: Stage to get metrics for
            hours_back: Hours of history to include
            
        Returns:
            Dictionary with performance statistics
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total_calls,
                    COUNT(CASE WHEN success = true THEN 1 END) as successful_calls,
                    COUNT(CASE WHEN success = false THEN 1 END) as failed_calls,
                    AVG(response_time_ms) as avg_response_time,
                    MIN(response_time_ms) as min_response_time,
                    MAX(response_time_ms) as max_response_time,
                    SUM(cost_estimate) as total_cost,
                    SUM(sentences_processed) as total_sentences_processed,
                    COUNT(DISTINCT model_used) as models_used
                FROM performance_metrics 
                WHERE stage_name = %s 
                AND processing_date >= NOW() - INTERVAL '%s hours'
            """
            
            results = self.db.execute_query(query, (stage_name, hours_back))
            
            if results:
                row = results[0]
                return {
                    'stage_name': stage_name,
                    'total_calls': row[0] or 0,
                    'successful_calls': row[1] or 0,
                    'failed_calls': row[2] or 0,
                    'success_rate': (row[1] or 0) / max(row[0] or 1, 1) * 100,
                    'avg_response_time_ms': row[3] or 0,
                    'min_response_time_ms': row[4] or 0,
                    'max_response_time_ms': row[5] or 0,
                    'total_cost_estimate': row[6] or 0,
                    'total_sentences_processed': row[7] or 0,
                    'models_used_count': row[8] or 0,
                    'hours_back': hours_back
                }
            
            return {'stage_name': stage_name, 'no_data': True}
            
        except Exception as e:
            logger.error(f"Failed to get stage performance: {str(e)}")
            return {'stage_name': stage_name, 'error': str(e)}
    
    def get_overall_performance(self, hours_back: int = 24) -> Dict:
        """
        Get overall performance metrics across all stages
        
        Args:
            hours_back: Hours of history to include
            
        Returns:
            Dictionary with overall performance statistics
        """
        try:
            query = """
                SELECT 
                    stage_name,
                    COUNT(*) as total_calls,
                    COUNT(CASE WHEN success = true THEN 1 END) as successful_calls,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(cost_estimate) as stage_cost
                FROM performance_metrics 
                WHERE processing_date >= NOW() - INTERVAL '%s hours'
                AND stage_name != 'pipeline_session'
                GROUP BY stage_name
                ORDER BY stage_name
            """
            
            results = self.db.execute_query(query, (hours_back,))
            
            stage_stats = {}
            total_calls = 0
            total_successful = 0
            total_cost = 0
            
            for row in results:
                stage_name = row[0]
                calls = row[1] or 0
                successful = row[2] or 0
                avg_time = row[3] or 0
                cost = row[4] or 0
                
                stage_stats[stage_name] = {
                    'total_calls': calls,
                    'successful_calls': successful,
                    'success_rate': successful / max(calls, 1) * 100,
                    'avg_response_time_ms': avg_time,
                    'total_cost_estimate': cost
                }
                
                total_calls += calls
                total_successful += successful
                total_cost += cost
            
            return {
                'hours_back': hours_back,
                'total_calls': total_calls,
                'total_successful': total_successful,
                'overall_success_rate': total_successful / max(total_calls, 1) * 100,
                'total_cost_estimate': total_cost,
                'stages': stage_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get overall performance: {str(e)}")
            return {'error': str(e)}
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """
        Get recent errors for troubleshooting
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of recent error records
        """
        try:
            query = """
                SELECT stage_name, api_call_type, error_message, 
                       processing_date, session_id, model_used
                FROM performance_metrics 
                WHERE success = false 
                AND error_message IS NOT NULL
                ORDER BY processing_date DESC
                LIMIT %s
            """
            
            results = self.db.execute_query(query, (limit,))
            
            errors = []
            for row in results:
                errors.append({
                    'stage_name': row[0],
                    'api_call_type': row[1],
                    'error_message': row[2],
                    'processing_date': row[3].isoformat() if row[3] else None,
                    'session_id': row[4],
                    'model_used': row[5]
                })
            
            return errors
            
        except Exception as e:
            logger.error(f"Failed to get recent errors: {str(e)}")
            return []

# Utility function for quick API call logging
def log_api_metrics(stage_name: str, api_call_type: str, success: bool, 
                   response_time_ms: int = None, error_message: str = None,
                   model_used: str = None, session_id: str = None) -> None:
    """
    Quick utility function to log API metrics
    
    Args:
        stage_name: Processing stage name
        api_call_type: Type of API call
        success: Whether the call succeeded
        response_time_ms: Response time in milliseconds
        error_message: Error message if failed
        model_used: Model name used for the call
        session_id: Session identifier
    """
    tracker = PerformanceTracker()
    metrics = APIMetrics(
        stage_name=stage_name,
        api_call_type=api_call_type,
        response_time_ms=response_time_ms,
        success=success,
        error_message=error_message,
        model_used=model_used,
        session_id=session_id
    )
    tracker.log_api_call(metrics)