#!/usr/bin/env python3
"""
Copywriting Evaluator API Routes

Flask blueprint for copywriting evaluator functionality including:
- Pipeline processing endpoints
- Processing status and statistics
- Stage-specific processing controls
- CSV file upload and management

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import json
import logging
from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify, request, session
from modules.database.database_manager import DatabaseManager
from modules.security.security_patch import SecurityPatch

logger = logging.getLogger(__name__)

def require_auth(f):
    """Authentication decorator for copywriting evaluator endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    
    return decorated_function

# Create blueprint
copywriting_evaluator_bp = Blueprint("copywriting_evaluator", __name__, url_prefix="/api/copywriting-evaluator")

@copywriting_evaluator_bp.route("/pipeline/start", methods=["POST"])
@require_auth
@SecurityPatch.validate_request_size()
def start_pipeline_processing():
    """
    Start copywriting evaluator pipeline processing
    
    Expected JSON payload:
    {
        "mode": "testing" | "production",
        "stages": ["keyword_filter", "truthfulness", "canadian_spelling", "tone_analysis", "skill_analysis"],
        "batch_size": 50,
        "immediate_processing": true
    }
    """
    try:
        data = request.get_json() or {}
        
        # Validate mode
        mode = data.get('mode', 'testing')
        if mode not in ['testing', 'production']:
            return jsonify({"error": "Mode must be 'testing' or 'production'"}), 400
        
        # Import pipeline processor
        try:
            from modules.content.copywriting_evaluator.pipeline_processor import CopywritingEvaluatorPipeline, ProcessingMode, PipelineConfig
            
            # Create configuration
            config = PipelineConfig(
                mode=ProcessingMode.TESTING if mode == 'testing' else ProcessingMode.PRODUCTION,
                immediate_processing=True
            )
            processor = CopywritingEvaluatorPipeline(config=config)
        except ImportError as e:
            return jsonify({"error": f"Pipeline processor not available: {str(e)}"}), 503
        
        # Get processing configuration
        stages = data.get('stages', ['keyword_filter', 'truthfulness', 'canadian_spelling', 'tone_analysis', 'skill_analysis'])
        batch_size = data.get('batch_size', 50)
        immediate_processing = data.get('immediate_processing', True)
        
        if immediate_processing:
            # Start immediate processing
            session_id = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Process all specified stages
            results = {}
            for stage in stages:
                try:
                    result = processor.process_stage(stage, session_id, batch_size)
                    results[stage] = {
                        'success': True,
                        'processed': result.get('processed', 0),
                        'approved': result.get('approved', 0),
                        'rejected': result.get('rejected', 0),
                        'errors': result.get('errors', 0)
                    }
                except Exception as e:
                    logger.error(f"Error processing stage {stage}: {str(e)}")
                    results[stage] = {
                        'success': False,
                        'error': str(e)
                    }
            
            return jsonify({
                'success': True,
                'message': 'Pipeline processing completed',
                'session_id': session_id,
                'mode': mode,
                'results': results,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Schedule processing for later
            return jsonify({
                'success': True,
                'message': 'Pipeline processing scheduled',
                'mode': mode,
                'scheduled_stages': stages,
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Pipeline start error: {str(e)}")
        return jsonify({"error": f"Pipeline processing failed: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/pipeline/status", methods=["GET"])
@require_auth
def get_pipeline_status():
    """Get current pipeline processing status and statistics"""
    try:
        from modules.content.copywriting_evaluator.pipeline_processor import CopywritingEvaluatorPipeline, ProcessingMode, PipelineConfig
        
        # Get status for both modes  
        testing_config = PipelineConfig(mode=ProcessingMode.TESTING)
        production_config = PipelineConfig(mode=ProcessingMode.PRODUCTION)
        testing_processor = CopywritingEvaluatorPipeline(config=testing_config)
        production_processor = CopywritingEvaluatorPipeline(config=production_config)
        
        # Get database statistics
        db = DatabaseManager()
        
        # Count sentences by processing stage
        stage_counts = {}
        tables = ['sentence_bank_technical', 'sentence_bank_behavioral', 'sentence_bank_achievements']
        
        for table in tables:
            try:
                # Get counts by processing stage
                query = f"""
                    SELECT 
                        COALESCE(keyword_filter_status, 'pending') as kf_status,
                        COALESCE(truthfulness_status, 'pending') as truth_status,
                        COALESCE(canadian_spelling_status, 'pending') as spelling_status,
                        COALESCE(tone_analysis_status, 'pending') as tone_status,
                        COALESCE(skill_analysis_status, 'pending') as skill_status,
                        COUNT(*) as count
                    FROM {table}
                    GROUP BY kf_status, truth_status, spelling_status, tone_status, skill_status
                """
                
                results = db.execute_query(query)
                stage_counts[table] = results
                
            except Exception as e:
                logger.warning(f"Could not get stage counts for {table}: {str(e)}")
                stage_counts[table] = []
        
        # Get processing statistics
        processing_stats = {
            'total_sentences': sum([
                len(db.execute_query(f"SELECT id FROM {table}") or [])
                for table in tables
            ]),
            'stage_progress': stage_counts,
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'pipeline_status': {
                'testing_mode': {
                    'available': True,
                    'description': 'Immediate processing for testing'
                },
                'production_mode': {
                    'available': True,
                    'description': 'Scheduled processing for production'
                }
            },
            'processing_statistics': processing_stats
        })
        
    except Exception as e:
        logger.error(f"Status retrieval error: {str(e)}")
        return jsonify({"error": f"Could not retrieve pipeline status: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/stages/<stage_name>/process", methods=["POST"])
@require_auth
@SecurityPatch.validate_request_size()
def process_single_stage(stage_name):
    """
    Process a specific stage of the copywriting evaluator pipeline
    
    URL parameter: stage_name (keyword_filter, truthfulness, canadian_spelling, tone_analysis, skill_analysis)
    
    Expected JSON payload:
    {
        "mode": "testing" | "production",
        "batch_size": 50,
        "session_id": "optional_session_id"
    }
    """
    try:
        # Validate stage name
        valid_stages = ['keyword_filter', 'truthfulness', 'canadian_spelling', 'tone_analysis', 'skill_analysis']
        if stage_name not in valid_stages:
            return jsonify({"error": f"Invalid stage name. Must be one of: {valid_stages}"}), 400
        
        data = request.get_json() or {}
        mode = data.get('mode', 'testing')
        batch_size = data.get('batch_size', 50)
        session_id = data.get('session_id', f"stage_{stage_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Import and initialize processor
        from modules.content.copywriting_evaluator.pipeline_processor import CopywritingEvaluatorPipeline, ProcessingMode, PipelineConfig
        
        config = PipelineConfig(
            mode=ProcessingMode.TESTING if mode == 'testing' else ProcessingMode.PRODUCTION
        )
        processor = CopywritingEvaluatorPipeline(config=config)
        
        # Process the specified stage - placeholder implementation
        result = {
            'processed': 0,
            'approved': 0,
            'rejected': 0,
            'errors': 0,
            'message': f'Stage {stage_name} processing endpoint ready for integration'
        }
        
        return jsonify({
            'success': True,
            'stage': stage_name,
            'session_id': session_id,
            'mode': mode,
            'result': {
                'processed': result.get('processed', 0),
                'approved': result.get('approved', 0),
                'rejected': result.get('rejected', 0),
                'errors': result.get('errors', 0)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Single stage processing error for {stage_name}: {str(e)}")
        return jsonify({"error": f"Stage {stage_name} processing failed: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/data/csv-upload", methods=["POST"])
@require_auth
@SecurityPatch.validate_request_size()
def upload_csv_data():
    """
    Upload CSV data for processing
    
    Expected JSON payload:
    {
        "data_type": "sentences" | "keywords" | "spellings",
        "csv_content": "base64_encoded_csv" | "csv_text_content",
        "table_target": "sentence_bank_technical" | "keyword_filters" | "canadian_spellings",
        "processing_mode": "append" | "replace"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON payload required"}), 400
        
        data_type = data.get('data_type')
        csv_content = data.get('csv_content')
        table_target = data.get('table_target')
        processing_mode = data.get('processing_mode', 'append')
        
        if not all([data_type, csv_content, table_target]):
            return jsonify({"error": "Missing required fields: data_type, csv_content, table_target"}), 400
        
        # Import CSV processor
        from modules.content.copywriting_evaluator.pipeline_processor import CopywritingEvaluatorPipeline, PipelineConfig
        
        config = PipelineConfig()
        processor = CopywritingEvaluatorPipeline(config=config)
        
        # Process CSV data - placeholder implementations
        if data_type == 'sentences':
            # Process sentence bank data
            result = {'success': True, 'message': f'Sentence CSV processing to {table_target} ready for implementation', 'rows_processed': 0}
        elif data_type == 'keywords':
            # Process keyword filter data
            result = {'success': True, 'message': 'Keyword CSV processing ready for implementation', 'rows_processed': 0}
        elif data_type == 'spellings':
            # Process Canadian spellings data
            result = {'success': True, 'message': 'Spelling CSV processing ready for implementation', 'rows_processed': 0}
        else:
            return jsonify({"error": "Invalid data_type. Must be 'sentences', 'keywords', or 'spellings'"}), 400
        
        return jsonify({
            'success': True,
            'data_type': data_type,
            'table_target': table_target,
            'processing_mode': processing_mode,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"CSV upload error: {str(e)}")
        return jsonify({"error": f"CSV upload failed: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/statistics", methods=["GET"])
@require_auth
def get_processing_statistics():
    """Get comprehensive processing statistics for the copywriting evaluator"""
    try:
        db = DatabaseManager()
        
        # Get sentence bank statistics
        sentence_stats = {}
        tables = ['sentence_bank_technical', 'sentence_bank_behavioral', 'sentence_bank_achievements']
        
        for table in tables:
            try:
                # Count total sentences
                total_query = f"SELECT COUNT(*) as total FROM {table}"
                total_result = db.execute_query(total_query)
                total = total_result[0]['total'] if total_result else 0
                
                # Count by processing stages
                stage_query = f"""
                    SELECT 
                        SUM(CASE WHEN keyword_filter_status = 'approved' THEN 1 ELSE 0 END) as kf_approved,
                        SUM(CASE WHEN truthfulness_status = 'approved' THEN 1 ELSE 0 END) as truth_approved,
                        SUM(CASE WHEN canadian_spelling_status = 'approved' THEN 1 ELSE 0 END) as spelling_approved,
                        SUM(CASE WHEN tone_analysis_status = 'approved' THEN 1 ELSE 0 END) as tone_approved,
                        SUM(CASE WHEN skill_analysis_status = 'approved' THEN 1 ELSE 0 END) as skill_approved
                    FROM {table}
                """
                
                stage_result = db.execute_query(stage_query)
                stage_counts = stage_result[0] if stage_result else {}
                
                sentence_stats[table] = {
                    'total': total,
                    'processing_progress': stage_counts
                }
                
            except Exception as e:
                logger.warning(f"Could not get statistics for {table}: {str(e)}")
                sentence_stats[table] = {'total': 0, 'processing_progress': {}}
        
        # Get keyword filters count
        try:
            keyword_query = "SELECT COUNT(*) as total FROM keyword_filters"
            keyword_result = db.execute_query(keyword_query)
            keyword_count = keyword_result[0]['total'] if keyword_result else 0
        except:
            keyword_count = 0
        
        # Get Canadian spellings count
        try:
            spelling_query = "SELECT COUNT(*) as total FROM canadian_spellings"
            spelling_result = db.execute_query(spelling_query)
            spelling_count = spelling_result[0]['total'] if spelling_result else 0
        except:
            spelling_count = 0
        
        return jsonify({
            'success': True,
            'statistics': {
                'sentence_banks': sentence_stats,
                'keyword_filters': keyword_count,
                'canadian_spellings': spelling_count,
                'pipeline_stages': [
                    'keyword_filter',
                    'truthfulness',
                    'canadian_spelling', 
                    'tone_analysis',
                    'skill_analysis'
                ],
                'last_updated': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Statistics retrieval error: {str(e)}")
        return jsonify({"error": f"Could not retrieve statistics: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/gemini/usage", methods=["GET"])
@require_auth
def get_gemini_usage_statistics():
    """Get Gemini API usage statistics for copywriting evaluator"""
    try:
        # Get usage statistics from different analyzers
        usage_stats = {}
        
        # Import performance tracker for enhanced metrics
        try:
            from modules.content.copywriting_evaluator.performance_tracker import PerformanceTracker
            performance_tracker = PerformanceTracker()
            
            # Get performance data for each stage/component
            stages = ['truthfulness', 'tone_analysis', 'skill_analysis']
            for stage in stages:
                try:
                    # Get 24-hour performance metrics
                    stage_metrics = performance_tracker.get_stage_performance(stage, hours_back=24)
                    
                    usage_stats[stage] = {
                        'status': 'operational',
                        'api_configured': bool(os.environ.get("GEMINI_API_KEY")),
                        'total_calls_24h': stage_metrics.get('total_calls', 0),
                        'successful_calls_24h': stage_metrics.get('successful_calls', 0),
                        'failed_calls_24h': stage_metrics.get('failed_calls', 0),
                        'success_rate': round(stage_metrics.get('success_rate', 100.0), 2),
                        'avg_response_time_ms': round(stage_metrics.get('avg_response_time_ms', 0), 2),
                        'total_cost_estimate': round(stage_metrics.get('total_cost_estimate', 0), 4),
                        'sentences_processed_24h': stage_metrics.get('total_sentences_processed', 0)
                    }
                except Exception as e:
                    logger.warning(f"Performance tracking error for {stage}: {str(e)}")
                    usage_stats[stage] = {
                        'status': 'unavailable',
                        'api_configured': bool(os.environ.get("GEMINI_API_KEY")),
                        'error': 'Performance tracking unavailable'
                    }
                    
            # Add overall performance summary
            try:
                overall_perf = performance_tracker.get_overall_performance(hours_back=24)
                usage_stats['overall_24h'] = {
                    'total_api_calls': overall_perf.get('total_calls', 0),
                    'successful_calls': overall_perf.get('total_successful', 0),
                    'total_cost_estimate': round(overall_perf.get('total_cost_estimate', 0), 4),
                    'overall_success_rate': round(overall_perf.get('overall_success_rate', 100.0), 2),
                    'stage_breakdown': overall_perf.get('stages', {}),
                    'hours_analyzed': overall_perf.get('hours_back', 24)
                }
            except Exception as e:
                usage_stats['overall_24h'] = {'error': 'Overall metrics unavailable'}
                
        except ImportError:
            # Fallback to basic status checks if performance tracker unavailable
            usage_stats['truthfulness_evaluator'] = {'status': 'performance_tracking_unavailable'}
            usage_stats['tone_analyzer'] = {'status': 'performance_tracking_unavailable'}
            usage_stats['skill_analyzer'] = {'status': 'performance_tracking_unavailable'}
        
        return jsonify({
            'success': True,
            'gemini_usage_statistics': usage_stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Gemini usage statistics error: {str(e)}")
        return jsonify({"error": f"Could not retrieve Gemini usage statistics: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for copywriting evaluator API"""
    try:
        # Basic health checks
        health_status = {
            'api': 'healthy',
            'database': 'unknown',
            'gemini_api': 'unknown',
            'pipeline_processor': 'unknown'
        }
        
        # Check database connectivity
        try:
            db = DatabaseManager()
            db.execute_query("SELECT 1")
            health_status['database'] = 'healthy'
        except:
            health_status['database'] = 'error'
        
        # Check Gemini API configuration
        try:
            import os
            if os.environ.get('GEMINI_API_KEY'):
                health_status['gemini_api'] = 'configured'
            else:
                health_status['gemini_api'] = 'not_configured'
        except:
            health_status['gemini_api'] = 'error'
        
        # Check pipeline processor
        try:
            from modules.content.copywriting_evaluator.pipeline_processor import CopywritingEvaluatorPipeline, PipelineConfig
            config = PipelineConfig()
            processor = CopywritingEvaluatorPipeline(config=config)
            health_status['pipeline_processor'] = 'healthy'
        except:
            health_status['pipeline_processor'] = 'error'
        
        overall_status = 'healthy' if all(
            status in ['healthy', 'configured'] 
            for status in health_status.values()
        ) else 'degraded'
        
        return jsonify({
            'status': overall_status,
            'components': health_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@copywriting_evaluator_bp.route("/scheduler/status", methods=["GET"])
@require_auth
def get_scheduler_status():
    """Get current scheduler status and scheduled tasks"""
    try:
        from modules.content.copywriting_evaluator.scheduler import get_production_scheduler
        
        scheduler = get_production_scheduler()
        scheduler_status = scheduler.get_task_status()
        
        return jsonify({
            'success': True,
            'scheduler_status': scheduler_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Scheduler status error: {str(e)}")
        return jsonify({"error": f"Could not retrieve scheduler status: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/scheduler/start", methods=["POST"])
@require_auth
def start_scheduler():
    """Start the production scheduler"""
    try:
        from modules.content.copywriting_evaluator.scheduler import get_production_scheduler, setup_production_schedule
        from modules.content.copywriting_evaluator.pipeline_processor import CopywritingEvaluatorPipeline
        
        scheduler = get_production_scheduler()
        
        if scheduler.running:
            return jsonify({
                'success': True,
                'message': 'Scheduler is already running',
                'scheduler_running': True
            })
        
        # Set up production schedule if not already configured
        if not scheduler.tasks:
            setup_production_schedule(CopywritingEvaluatorPipeline)
        
        # Start the scheduler
        scheduler.start()
        
        return jsonify({
            'success': True,
            'message': 'Production scheduler started successfully',
            'scheduler_running': scheduler.running,
            'tasks_count': len(scheduler.tasks),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Scheduler start error: {str(e)}")
        return jsonify({"error": f"Could not start scheduler: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/scheduler/stop", methods=["POST"])
@require_auth
def stop_scheduler():
    """Stop the production scheduler"""
    try:
        from modules.content.copywriting_evaluator.scheduler import get_production_scheduler
        
        scheduler = get_production_scheduler()
        
        if not scheduler.running:
            return jsonify({
                'success': True,
                'message': 'Scheduler is already stopped',
                'scheduler_running': False
            })
        
        scheduler.stop()
        
        return jsonify({
            'success': True,
            'message': 'Production scheduler stopped successfully',
            'scheduler_running': scheduler.running,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Scheduler stop error: {str(e)}")
        return jsonify({"error": f"Could not stop scheduler: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/scheduler/tasks/<task_id>/enable", methods=["POST"])
@require_auth
def enable_scheduled_task(task_id):
    """Enable a specific scheduled task"""
    try:
        from modules.content.copywriting_evaluator.scheduler import get_production_scheduler
        
        scheduler = get_production_scheduler()
        success = scheduler.enable_task(task_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Task {task_id} enabled successfully',
                'task_id': task_id,
                'enabled': True,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Task {task_id} not found',
                'task_id': task_id
            }), 404
        
    except Exception as e:
        logger.error(f"Task enable error for {task_id}: {str(e)}")
        return jsonify({"error": f"Could not enable task {task_id}: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/scheduler/tasks/<task_id>/disable", methods=["POST"])
@require_auth
def disable_scheduled_task(task_id):
    """Disable a specific scheduled task"""
    try:
        from modules.content.copywriting_evaluator.scheduler import get_production_scheduler
        
        scheduler = get_production_scheduler()
        success = scheduler.disable_task(task_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Task {task_id} disabled successfully',
                'task_id': task_id,
                'enabled': False,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Task {task_id} not found',
                'task_id': task_id
            }), 404
        
    except Exception as e:
        logger.error(f"Task disable error for {task_id}: {str(e)}")
        return jsonify({"error": f"Could not disable task {task_id}: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/scheduler/tasks/<task_id>/run", methods=["POST"])
@require_auth
def force_run_scheduled_task(task_id):
    """Force immediate execution of a scheduled task"""
    try:
        from modules.content.copywriting_evaluator.scheduler import get_production_scheduler
        
        scheduler = get_production_scheduler()
        result = scheduler.force_run_task(task_id)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message'),
                'task_id': task_id,
                'execution_time': result.get('execution_time'),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error'),
                'task_id': task_id
            }), 400 if 'not found' in result.get('error', '').lower() else 500
        
    except Exception as e:
        logger.error(f"Force run error for {task_id}: {str(e)}")
        return jsonify({"error": f"Could not force run task {task_id}: {str(e)}"}), 500

@copywriting_evaluator_bp.route("/scheduler/configure", methods=["POST"])
@require_auth  
@SecurityPatch.validate_request_size()
def configure_production_schedule():
    """Configure production processing schedule settings"""
    try:
        data = request.get_json() or {}
        
        # Validate configuration options
        schedule_days = data.get('schedule_days', [1, 4])  # Default: Tuesday and Friday
        schedule_hour = data.get('schedule_hour', 2)  # Default: 2 AM
        schedule_minute = data.get('schedule_minute', 0)  # Default: 0 minutes
        enabled = data.get('enabled', True)
        
        # Validate days (0=Monday, 6=Sunday)
        if not all(isinstance(day, int) and 0 <= day <= 6 for day in schedule_days):
            return jsonify({"error": "schedule_days must be a list of integers 0-6 (0=Monday, 6=Sunday)"}), 400
        
        # Validate hour and minute
        if not (0 <= schedule_hour <= 23) or not (0 <= schedule_minute <= 59):
            return jsonify({"error": "Invalid hour (0-23) or minute (0-59)"}), 400
        
        from modules.content.copywriting_evaluator.scheduler import get_production_scheduler, setup_production_schedule
        from modules.content.copywriting_evaluator.pipeline_processor import CopywritingEvaluatorPipeline
        
        scheduler = get_production_scheduler()
        
        # Update schedule configuration
        scheduler.production_schedule = {
            'days': schedule_days,
            'hour': schedule_hour, 
            'minute': schedule_minute
        }
        
        # Remove existing task and recreate with new schedule
        if 'pipeline_processing' in scheduler.tasks:
            scheduler.remove_task('pipeline_processing')
        
        # Set up new production schedule
        setup_production_schedule(CopywritingEvaluatorPipeline)
        
        # Enable/disable task based on configuration
        if 'pipeline_processing' in scheduler.tasks:
            if enabled:
                scheduler.enable_task('pipeline_processing')
            else:
                scheduler.disable_task('pipeline_processing')
        
        return jsonify({
            'success': True,
            'message': 'Production schedule configured successfully',
            'configuration': {
                'schedule_days': schedule_days,
                'schedule_hour': schedule_hour,
                'schedule_minute': schedule_minute,
                'enabled': enabled,
                'next_run': scheduler.tasks['pipeline_processing'].next_run.isoformat() if 'pipeline_processing' in scheduler.tasks and scheduler.tasks['pipeline_processing'].next_run else None
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Schedule configuration error: {str(e)}")
        return jsonify({"error": f"Could not configure schedule: {str(e)}"}), 500