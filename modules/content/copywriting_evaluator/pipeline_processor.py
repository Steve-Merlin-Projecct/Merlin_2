#!/usr/bin/env python3
"""
Main Pipeline Orchestrator for Copywriting Evaluator System

Coordinates five-stage processing workflow with independent status tracking,
restart capability, and comprehensive error handling. Supports both testing
and production modes with different scheduling behaviors.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import logging
import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Database integration
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from modules.database.database_manager import DatabaseManager
from modules.content.copywriting_evaluator.performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)

class ProcessingMode(Enum):
    """Processing modes for pipeline operation"""
    TESTING = "testing"    # Immediate processing, no error limits
    PRODUCTION = "production"  # Scheduled processing, error limits enabled

class ProcessingStage(Enum):
    """Five-stage processing pipeline"""
    KEYWORD_FILTER = "keyword_filter"
    TRUTHFULNESS = "truthfulness"
    CANADIAN_SPELLING = "canadian_spelling"
    TONE_ANALYSIS = "tone_analysis"
    SKILL_ANALYSIS = "skill_analysis"

@dataclass
class PipelineConfig:
    """Configuration for pipeline processing"""
    mode: ProcessingMode = ProcessingMode.TESTING
    batch_size: int = 5
    max_consecutive_errors: int = 15
    error_cooldown_hours: int = 23
    retry_attempts: int = 1
    # Mode-specific settings
    enable_scheduling: bool = False  # Enable scheduled processing for production
    immediate_processing: bool = True  # Process immediately (testing mode default)
    strict_validation: bool = False  # Stricter validation in production
    detailed_logging: bool = True  # Verbose logging for testing

@dataclass
class ProcessingStats:
    """Statistics for pipeline processing session"""
    session_id: str
    total_sentences: int = 0
    processed_sentences: int = 0
    filtered_sentences: int = 0  # Stage 1 rejections
    approved_sentences: int = 0
    error_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    stage_stats: Optional[Dict[str, Dict]] = None
    
    def __post_init__(self):
        if self.stage_stats is None:
            self.stage_stats = {}

class CopywritingEvaluatorPipeline:
    """
    Main orchestrator for the five-stage copywriting evaluation pipeline
    
    Coordinates processing across all stages with independent status tracking,
    restart capability, comprehensive error handling, and performance monitoring.
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize pipeline orchestrator"""
        self.config = config if config is not None else PipelineConfig()
        self.db = DatabaseManager()
        self.performance_tracker = PerformanceTracker()
        
        # Error tracking - integrate with comprehensive error handler
        self.consecutive_errors = 0
        self.last_error_time = None
        self.cooldown_until = None
        
        # Initialize comprehensive error handler
        from modules.content.copywriting_evaluator.error_handler import get_error_handler
        self.error_handler = get_error_handler()
        
        # Import stage processors (lazy loading)
        self._stage_processors = {}
        
        # Configure mode-specific settings
        self._configure_mode_settings()
        
        logger.info(f"Pipeline initialized in {self.config.mode.value} mode")
        
        # Initialize scheduler for production mode
        if self.config.mode == ProcessingMode.PRODUCTION and self.config.enable_scheduling:
            self._setup_production_scheduler()
    
    def _get_stage_processor(self, stage: ProcessingStage):
        """Lazy load stage processors to avoid circular imports"""
        if stage not in self._stage_processors:
            if stage == ProcessingStage.KEYWORD_FILTER:
                from modules.content.copywriting_evaluator.keyword_filter import KeywordFilter
                self._stage_processors[stage] = KeywordFilter()
            elif stage == ProcessingStage.TRUTHFULNESS:
                from modules.content.copywriting_evaluator.truthfulness_evaluator import TruthfulnessEvaluator
                self._stage_processors[stage] = TruthfulnessEvaluator()
            elif stage == ProcessingStage.CANADIAN_SPELLING:
                from modules.content.copywriting_evaluator.canadian_spelling_processor import CanadianSpellingProcessor
                self._stage_processors[stage] = CanadianSpellingProcessor()
            elif stage == ProcessingStage.TONE_ANALYSIS:
                from modules.content.copywriting_evaluator.tone_analyzer import ToneAnalyzer
                self._stage_processors[stage] = ToneAnalyzer()
            elif stage == ProcessingStage.SKILL_ANALYSIS:
                from modules.content.copywriting_evaluator.skill_analyzer import SkillAnalyzer
                self._stage_processors[stage] = SkillAnalyzer()
        
        return self._stage_processors[stage]
    
    def _configure_mode_settings(self) -> None:
        """Configure pipeline settings based on processing mode"""
        if self.config.mode == ProcessingMode.TESTING:
            # Testing mode: immediate processing, relaxed limits
            self.config.immediate_processing = True
            self.config.enable_scheduling = False
            self.config.strict_validation = False
            self.config.detailed_logging = True
            # No error limits in testing
            self.config.max_consecutive_errors = 999999
            logger.debug("Configured for TESTING mode: immediate processing, no error limits")
            
        elif self.config.mode == ProcessingMode.PRODUCTION:
            # Production mode: scheduled processing, strict limits
            self.config.immediate_processing = False
            self.config.enable_scheduling = True
            self.config.strict_validation = True
            self.config.detailed_logging = False
            # Restore original error limits
            if self.config.max_consecutive_errors == 999999:
                self.config.max_consecutive_errors = 15
            logger.debug("Configured for PRODUCTION mode: scheduled processing, error limits enabled")
    
    def _setup_production_scheduler(self) -> None:
        """Initialize production mode scheduler"""
        try:
            from modules.content.copywriting_evaluator.scheduler import setup_production_schedule
            setup_production_schedule(CopywritingEvaluatorPipeline)
            logger.info("Production scheduler initialized")
        except Exception as e:
            logger.error(f"Failed to setup production scheduler: {str(e)}")
    
    def switch_mode(self, new_mode: ProcessingMode) -> Dict:
        """
        Switch pipeline processing mode with proper reconfiguration
        
        Args:
            new_mode: New processing mode to switch to
            
        Returns:
            Dictionary with switch status and details
        """
        try:
            old_mode = self.config.mode
            
            if old_mode == new_mode:
                return {
                    'success': True,
                    'message': f'Already in {new_mode.value} mode',
                    'mode': new_mode.value
                }
            
            logger.info(f"Switching pipeline mode: {old_mode.value} -> {new_mode.value}")
            
            # Reset error tracking when switching modes
            self.error_handler.reset_error_tracking(f"Mode switch from {old_mode.value} to {new_mode.value}")
            self.consecutive_errors = 0
            self.cooldown_until = None
            
            # Update mode
            self.config.mode = new_mode
            self._configure_mode_settings()
            
            # Handle scheduler setup/teardown
            if new_mode == ProcessingMode.PRODUCTION and self.config.enable_scheduling:
                self._setup_production_scheduler()
            elif old_mode == ProcessingMode.PRODUCTION:
                # Stop production scheduler if switching away from production
                try:
                    from modules.content.copywriting_evaluator.scheduler import get_production_scheduler
                    scheduler = get_production_scheduler()
                    scheduler.stop()
                    logger.info("Production scheduler stopped")
                except:
                    pass  # Ignore errors when stopping scheduler
            
            return {
                'success': True,
                'message': f'Successfully switched from {old_mode.value} to {new_mode.value} mode',
                'previous_mode': old_mode.value,
                'current_mode': new_mode.value,
                'immediate_processing': self.config.immediate_processing,
                'scheduling_enabled': self.config.enable_scheduling
            }
            
        except Exception as e:
            logger.error(f"Mode switch failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'current_mode': self.config.mode.value
            }
    
    def is_in_cooldown(self) -> bool:
        """Check if pipeline is in error cooldown period"""
        # Use comprehensive error handler for cooldown status
        return self.error_handler.is_in_cooldown()
    
    def can_process(self) -> Tuple[bool, str]:
        """Check if pipeline can process new requests"""
        
        # Check cooldown period
        if self.is_in_cooldown():
            if self.cooldown_until is not None:
                remaining = (self.cooldown_until - datetime.now()).total_seconds() / 3600
                return False, f"In cooldown period. {remaining:.1f} hours remaining"
            else:
                return False, "In cooldown period"
        
        # Check if we're at error limit (production mode only)
        if (self.config.mode == ProcessingMode.PRODUCTION and 
            self.consecutive_errors >= self.config.max_consecutive_errors):
            return False, f"Maximum consecutive errors ({self.config.max_consecutive_errors}) reached"
        
        # Check if immediate processing is disabled (production scheduled mode)
        if (self.config.mode == ProcessingMode.PRODUCTION and 
            not self.config.immediate_processing and
            self.config.enable_scheduling):
            return False, "Production mode scheduled processing only - use scheduler for processing"
        
        return True, "Ready for processing"
    
    def _validate_sentence_variables(self, content_text: str) -> Tuple[bool, List[str]]:
        """
        Validate sentence content for supported variables
        
        Args:
            content_text: The sentence content to validate
            
        Returns:
            Tuple of (is_valid, list_of_unsupported_variables)
        """
        # Find all curly bracket variables in the text
        variable_pattern = r'\{([^}]+)\}'
        found_variables = re.findall(variable_pattern, content_text)
        
        # Supported variables
        supported_variables = {'job_title', 'company_name'}
        
        # Check for unsupported variables
        unsupported_variables = [var for var in found_variables if var not in supported_variables]
        
        is_valid = len(unsupported_variables) == 0
        return is_valid, unsupported_variables
    
    async def _validate_and_reject_unsupported_variables(self, sentences: List[Dict]) -> int:
        """
        Validate sentences for unsupported variables and mark them as rejected
        
        Args:
            sentences: List of sentence dictionaries to validate
            
        Returns:
            Number of sentences rejected due to unsupported variables
        """
        rejected_count = 0
        sentences_to_update = []
        
        for sentence in sentences:
            content_text = sentence.get('content_text', '')
            is_valid, unsupported_vars = self._validate_sentence_variables(content_text)
            
            if not is_valid:
                logger.info(f"Rejecting sentence {sentence['id']} due to unsupported variables: {unsupported_vars}")
                
                # Prepare update data for rejection
                sentences_to_update.append({
                    'id': sentence['id'],
                    'table_name': sentence['table_name'],
                    'unsupported_variables': unsupported_vars
                })
                rejected_count += 1
        
        # Batch update rejected sentences in database
        if sentences_to_update:
            await self._batch_reject_sentences_with_unsupported_variables(sentences_to_update)
        
        return rejected_count
    
    async def _batch_reject_sentences_with_unsupported_variables(self, sentences_to_reject: List[Dict]):
        """
        Batch update sentences with unsupported variables to rejected status
        
        Args:
            sentences_to_reject: List of sentence info to reject
        """
        for sentence_info in sentences_to_reject:
            sentence_id = sentence_info['id']
            table_name = sentence_info['table_name']
            unsupported_vars = sentence_info['unsupported_variables']
            
            # Create rejection reason
            rejection_reason = f"Unsupported variables: {', '.join(unsupported_vars)}"
            current_time = datetime.now()
            
            # Update all stage statuses to 'rejected'
            update_query = f"""
                UPDATE {table_name}
                SET status = 'rejected',
                    keyword_filter_status = 'rejected',
                    keyword_filter_date = %s,
                    keyword_filter_reason = %s,
                    truthfulness_status = 'rejected',
                    truthfulness_date = %s,
                    canadian_spelling_status = 'rejected',
                    canadian_spelling_date = %s,
                    tone_analysis_status = 'rejected',
                    tone_analysis_date = %s,
                    skill_analysis_status = 'rejected',
                    skill_analysis_date = %s
                WHERE id = %s
            """
            
            params = (
                current_time, rejection_reason,  # keyword_filter
                current_time,                    # truthfulness
                current_time,                    # canadian_spelling
                current_time,                    # tone_analysis
                current_time,                    # skill_analysis
                sentence_id
            )
            
            self.db.execute_query(update_query, params)
        
        logger.info(f"Batch rejected {len(sentences_to_reject)} sentences with unsupported variables")

    async def process_sentences(self, table_name: Optional[str] = None, 
                               sentence_ids: Optional[List[str]] = None,
                               restart_from_stage: Optional[ProcessingStage] = None) -> ProcessingStats:
        """
        Process sentences through the five-stage pipeline
        
        Args:
            table_name: 'sentence_bank_cover_letter' or 'sentence_bank_resume' 
            sentence_ids: Optional list of specific sentence IDs to process
            restart_from_stage: Stage to restart processing from
            
        Returns:
            ProcessingStats: Comprehensive processing statistics
        """
        
        session_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        stats = ProcessingStats(session_id=session_id, start_time=datetime.now(), stage_stats={})
        
        # Check if we can process
        can_process, reason = self.can_process()
        if not can_process:
            logger.warning(f"Processing blocked: {reason}")
            raise Exception(f"Processing blocked: {reason}")
        
        try:
            # Get sentences to process
            sentences = await self._get_sentences_for_processing(table_name, sentence_ids, restart_from_stage)
            stats.total_sentences = len(sentences)
            
            if self.config.detailed_logging:
                logger.info(f"Starting pipeline processing: {stats.total_sentences} sentences "
                           f"(Mode: {self.config.mode.value}, Immediate: {self.config.immediate_processing})")
            else:
                logger.info(f"Processing {stats.total_sentences} sentences")
            
            # Validate sentences for unsupported variables and reject if necessary
            # This happens before any stage processing to ensure data integrity
            if not restart_from_stage:  # Only validate on fresh processing, not restarts
                rejected_count = await self._validate_and_reject_unsupported_variables(sentences)
                if rejected_count > 0:
                    stats.filtered_sentences += rejected_count
                    logger.info(f"Pre-processing validation: {rejected_count} sentences rejected due to unsupported variables")
                    
                    # Remove rejected sentences from processing list
                    sentences = [s for s in sentences if s.get('status') != 'rejected']
                    logger.info(f"Continuing with {len(sentences)} valid sentences")
            
            # Process through each stage
            processing_stages = list(ProcessingStage)
            if restart_from_stage:
                # Start from specified stage
                start_index = processing_stages.index(restart_from_stage)
                processing_stages = processing_stages[start_index:]
            
            for stage in processing_stages:
                stage_stats = await self._process_stage(stage, sentences, session_id)
                if stats.stage_stats is not None:
                    stats.stage_stats[stage.value] = stage_stats
                
                # Update sentence list based on stage results (remove filtered/rejected)
                if stage == ProcessingStage.KEYWORD_FILTER:
                    stats.filtered_sentences += stage_stats.get('rejected', 0)
                    sentences = [s for s in sentences if s['keyword_filter_status'] != 'rejected']
                
                # Stop if all sentences rejected or error limit reached
                if not sentences or self.consecutive_errors >= self.config.max_consecutive_errors:
                    break
            
            stats.processed_sentences = len(sentences)
            stats.approved_sentences = len([s for s in sentences if s.get('final_status') == 'approved'])
            
            # Reset error count on successful completion
            if stats.error_count == 0:
                self.consecutive_errors = 0
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            await self._handle_pipeline_error(e, session_id)
            stats.error_count += 1
            raise
        finally:
            stats.end_time = datetime.now()
            await self.performance_tracker.log_pipeline_session(stats)
        
        logger.info(f"Pipeline processing complete: {stats.processed_sentences}/{stats.total_sentences} processed")
        return stats
    
    async def _get_sentences_for_processing(self, table_name: Optional[str], 
                                          sentence_ids: Optional[List[str]], 
                                          restart_from_stage: Optional[ProcessingStage]) -> List[Dict]:
        """Get sentences that need processing based on criteria"""
        
        # Default to both tables if not specified
        tables = [table_name] if table_name else ['sentence_bank_cover_letter', 'sentence_bank_resume']
        all_sentences = []
        
        for table in tables:
            query_conditions = []
            params = []
            
            if sentence_ids:
                # Process specific sentences
                placeholders = ','.join(['%s'] * len(sentence_ids))
                query_conditions.append(f"id IN ({placeholders})")
                params.extend(sentence_ids)
            else:
                # Get sentences that need processing
                if restart_from_stage:
                    # Restart from specific stage
                    stage_column = f"{restart_from_stage.value}_status"
                    query_conditions.append(f"{stage_column} IN ('pending', 'error')")
                else:
                    # Start from beginning - get sentences with pending keyword filter
                    query_conditions.append("keyword_filter_status = 'pending'")
            
            where_clause = " AND ".join(query_conditions) if query_conditions else "1=1"
            
            query = f"""
                SELECT id, content_text, status, 
                       keyword_filter_status, keyword_filter_date,
                       truthfulness_status, truthfulness_date, truthfulness_model,
                       canadian_spelling_status, canadian_spelling_date,
                       tone_analysis_status, tone_analysis_date, tone_analysis_model,
                       skill_analysis_status, skill_analysis_date, skill_analysis_model
                FROM {table}
                WHERE {where_clause}
                ORDER BY created_at ASC
                LIMIT %s
            """
            params.append(1000)  # Reasonable limit
            
            results = self.db.execute_query(query, tuple(params))

            # Add table info to each sentence
            # Note: execute_query already returns dicts, no need to convert
            for row in results:
                sentence = dict(row)  # Create a copy of the dict
                sentence['table_name'] = table
                all_sentences.append(sentence)
        
        return all_sentences
    
    async def _process_stage(self, stage: ProcessingStage, sentences: List[Dict], 
                           session_id: str) -> Dict:
        """Process sentences through a specific pipeline stage"""
        
        processor = self._get_stage_processor(stage)
        stage_stats = {
            'stage': stage.value,
            'total_sentences': len(sentences),
            'processed': 0,
            'approved': 0,
            'rejected': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        logger.info(f"Processing {stage.value}: {len(sentences)} sentences")
        
        try:
            # Filter sentences that need processing for this stage
            stage_column = f"{stage.value}_status"
            sentences_to_process = [s for s in sentences if s.get(stage_column) in ['pending', 'error', 'testing']]

            # DEBUG: Log filtering details
            if len(sentences) > 0:
                sample_sentence = sentences[0]
                logger.info(f"Stage {stage.value} filtering debug:")
                logger.info(f"  Total input sentences: {len(sentences)}")
                logger.info(f"  Looking for column: {stage_column}")
                logger.info(f"  Sample sentence keys: {list(sample_sentence.keys())}")
                logger.info(f"  Sample {stage_column} value: {sample_sentence.get(stage_column, 'KEY_NOT_FOUND')}")
                logger.info(f"  Sentences to process: {len(sentences_to_process)}")

            if not sentences_to_process:
                logger.info(f"No sentences need {stage.value} processing (filtered {len(sentences)} sentences)")
                return stage_stats
            
            # Process in batches
            batch_size = self.config.batch_size if stage in [ProcessingStage.TRUTHFULNESS, 
                                                           ProcessingStage.TONE_ANALYSIS,
                                                           ProcessingStage.SKILL_ANALYSIS] else 1
            
            for i in range(0, len(sentences_to_process), batch_size):
                batch = sentences_to_process[i:i + batch_size]
                
                try:
                    # Process batch through stage processor
                    results = await processor.process_batch(batch, session_id)

                    # Update database with results
                    await self._update_stage_results(stage, results)

                    # Update in-memory sentence dictionaries with new status
                    # This is CRITICAL - without this, subsequent stages won't see updated statuses
                    stage_column = f"{stage.value}_status"
                    for result in results:
                        sentence_id = result['id']
                        # Find matching sentence in the original list and update its status
                        for sentence in sentences:
                            if sentence['id'] == sentence_id:
                                sentence[stage_column] = result['status']
                                break

                    # Update statistics
                    for result in results:
                        stage_stats['processed'] += 1
                        if result.get('status') == 'approved':
                            stage_stats['approved'] += 1
                        elif result.get('status') == 'rejected':
                            stage_stats['rejected'] += 1

                    # Reset consecutive errors on successful batch
                    if self.config.mode == ProcessingMode.PRODUCTION:
                        self.consecutive_errors = 0
                
                except Exception as e:
                    logger.error(f"Batch processing failed in {stage.value}: {str(e)}")
                    stage_stats['errors'] += 1
                    
                    # Record error using comprehensive error handler
                    self.error_handler.record_error(e, {
                        'session_id': session_id,
                        'stage_name': stage.value,
                        'batch_size': len(batch),
                        'processing_mode': self.config.mode.value
                    })
                    
                    # Update local tracking for compatibility
                    if self.config.mode == ProcessingMode.PRODUCTION:
                        self.consecutive_errors = self.error_handler.consecutive_errors
                        self.last_error_time = self.error_handler.last_error_time
                        self.cooldown_until = self.error_handler.cooldown_until
                        
                        # Check if we hit error limit
                        if self.error_handler.is_in_cooldown():
                            logger.error(f"Error limit reached. Cooldown until {self.cooldown_until}")
                            break
                    
                    # Continue processing remaining batches unless in cooldown
                    continue
        
        finally:
            stage_stats['end_time'] = datetime.now()
            stage_stats['duration_seconds'] = (stage_stats['end_time'] - stage_stats['start_time']).total_seconds()
        
        logger.info(f"Stage {stage.value} complete: {stage_stats['processed']} processed, "
                   f"{stage_stats['approved']} approved, {stage_stats['rejected']} rejected")
        
        return stage_stats
    
    async def _update_stage_results(self, stage: ProcessingStage, results: List[Dict]):
        """Update database with stage processing results"""
        
        for result in results:
            table_name = result['table_name']
            sentence_id = result['id']
            status = result['status']
            
            # Build update query for stage-specific columns
            stage_column = f"{stage.value}_status"
            date_column = f"{stage.value}_date"
            
            update_columns = [f"{stage_column} = %s", f"{date_column} = CURRENT_DATE"]
            params = [status]
            
            # Add model info for AI stages
            if stage in [ProcessingStage.TRUTHFULNESS, ProcessingStage.TONE_ANALYSIS, ProcessingStage.SKILL_ANALYSIS]:
                model_column = f"{stage.value}_model"
                update_columns.append(f"{model_column} = %s")
                params.append(result.get('model_used', 'unknown'))
            
            # Add error message if present
            if result.get('error_message'):
                error_column = f"{stage.value}_error_message"
                update_columns.append(f"{error_column} = %s")
                params.append(result['error_message'])
            
            params.append(sentence_id)
            
            update_query = f"""
                UPDATE {table_name}
                SET {', '.join(update_columns)}
                WHERE id = %s
            """
            
            self.db.execute_query(update_query, tuple(params))
    
    async def _handle_pipeline_error(self, error: Exception, session_id: str):
        """Handle pipeline-level errors using comprehensive error handler"""
        
        # Record error using comprehensive error handler
        self.error_handler.record_error(error, {
            'session_id': session_id,
            'stage_name': 'pipeline',
            'error_type': 'pipeline_error',
            'processing_mode': self.config.mode.value
        })
        
        # Log performance metrics
        await self.performance_tracker.log_error({
            'session_id': session_id,
            'error_type': 'pipeline_error',
            'error_message': str(error),
            'timestamp': datetime.now()
        })
        
        # Update local tracking for compatibility
        if self.config.mode == ProcessingMode.PRODUCTION:
            self.consecutive_errors = self.error_handler.consecutive_errors
            self.last_error_time = self.error_handler.last_error_time
            self.cooldown_until = self.error_handler.cooldown_until
    
    def get_processing_status(self) -> Dict:
        """Get current pipeline processing status"""
        
        can_process, reason = self.can_process()
        
        status = {
            'mode': self.config.mode.value,
            'can_process': can_process,
            'status_message': reason,
            'consecutive_errors': self.consecutive_errors,
            'max_consecutive_errors': self.config.max_consecutive_errors,
            'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None,
            'cooldown_until': self.cooldown_until.isoformat() if self.cooldown_until else None,
            'is_in_cooldown': self.is_in_cooldown(),
            'immediate_processing': self.config.immediate_processing,
            'scheduling_enabled': self.config.enable_scheduling,
            'strict_validation': self.config.strict_validation
        }
        
        # Add scheduler status for production mode
        if self.config.mode == ProcessingMode.PRODUCTION and self.config.enable_scheduling:
            try:
                from modules.content.copywriting_evaluator.scheduler import get_production_scheduler
                scheduler = get_production_scheduler()
                status['scheduler_status'] = scheduler.get_task_status()
            except Exception as e:
                status['scheduler_error'] = str(e)
        
        # Add comprehensive error handler status
        try:
            error_status = self.error_handler.get_detailed_status()
            status['error_handler'] = error_status
        except Exception as e:
            status['error_handler_error'] = str(e)
        
        return status

# Utility functions for external integration

async def process_new_csv_data(csv_file_path: str, table_name: str) -> ProcessingStats:
    """Process newly uploaded CSV data through the complete pipeline"""
    
    # First, ingest CSV data
    from modules.content.copywriting_evaluator.csv_processor import CSVProcessor
    csv_processor = CSVProcessor()
    
    ingestion_result = await csv_processor.process_csv_file(csv_file_path, table_name)
    sentence_ids = ingestion_result.get('sentence_ids', [])
    
    # Then process through pipeline
    pipeline = CopywritingEvaluatorPipeline()
    return await pipeline.process_sentences(table_name=table_name, sentence_ids=sentence_ids)

async def restart_processing_from_stage(stage_name: str, table_name: Optional[str] = None) -> ProcessingStats:
    """Restart processing from a specific stage for sentences that need it"""
    
    try:
        stage = ProcessingStage(stage_name)
        pipeline = CopywritingEvaluatorPipeline()
        return await pipeline.process_sentences(table_name=table_name, restart_from_stage=stage)
    except ValueError:
        raise ValueError(f"Invalid stage: {stage_name}. Valid stages: {[s.value for s in ProcessingStage]}")