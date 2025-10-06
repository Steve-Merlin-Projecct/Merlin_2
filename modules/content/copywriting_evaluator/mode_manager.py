#!/usr/bin/env python3
"""
Mode Manager for Copywriting Evaluator System

Provides centralized management for switching between testing and production modes
with proper configuration management and validation.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import logging
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from modules.content.copywriting_evaluator.pipeline_processor import CopywritingEvaluatorPipeline
from enum import Enum

# Pipeline integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

logger = logging.getLogger(__name__)

class ModeManager:
    """
    Centralized mode management for copywriting evaluator pipeline
    
    Features:
    - Centralized mode switching
    - Configuration validation
    - Mode-specific presets
    - Integration with scheduler
    - State persistence (optional)
    """
    
    def __init__(self):
        """Initialize mode manager"""
        self._current_pipeline = None
        logger.info("Mode manager initialized")
    
    def create_testing_pipeline(self) -> 'CopywritingEvaluatorPipeline':
        """
        Create pipeline configured for testing mode
        
        Returns:
            Pipeline configured for immediate testing processing
        """
        from modules.content.copywriting_evaluator.pipeline_processor import (
            CopywritingEvaluatorPipeline, PipelineConfig, ProcessingMode
        )
        
        config = PipelineConfig(
            mode=ProcessingMode.TESTING,
            batch_size=5,
            max_consecutive_errors=999999,  # No limits in testing
            immediate_processing=True,
            enable_scheduling=False,
            strict_validation=False,
            detailed_logging=True
        )
        
        self._current_pipeline = CopywritingEvaluatorPipeline(config)
        logger.info("Created testing mode pipeline")
        return self._current_pipeline
    
    def create_production_pipeline(self, enable_scheduler: bool = True) -> 'CopywritingEvaluatorPipeline':
        """
        Create pipeline configured for production mode
        
        Args:
            enable_scheduler: Whether to enable automatic scheduling
            
        Returns:
            Pipeline configured for production processing
        """
        from modules.content.copywriting_evaluator.pipeline_processor import (
            CopywritingEvaluatorPipeline, PipelineConfig, ProcessingMode
        )
        
        config = PipelineConfig(
            mode=ProcessingMode.PRODUCTION,
            batch_size=5,
            max_consecutive_errors=15,
            error_cooldown_hours=23,
            immediate_processing=not enable_scheduler,
            enable_scheduling=enable_scheduler,
            strict_validation=True,
            detailed_logging=False
        )
        
        self._current_pipeline = CopywritingEvaluatorPipeline(config)
        logger.info(f"Created production mode pipeline (scheduling: {enable_scheduler})")
        return self._current_pipeline
    
    def switch_pipeline_mode(self, pipeline: 'CopywritingEvaluatorPipeline', 
                           target_mode: str) -> Dict:
        """
        Switch existing pipeline to different mode
        
        Args:
            pipeline: Pipeline instance to switch
            target_mode: 'testing' or 'production'
            
        Returns:
            Switch result dictionary
        """
        from modules.content.copywriting_evaluator.pipeline_processor import ProcessingMode
        
        try:
            if target_mode.lower() == 'testing':
                new_mode = ProcessingMode.TESTING
            elif target_mode.lower() == 'production':
                new_mode = ProcessingMode.PRODUCTION
            else:
                return {
                    'success': False,
                    'error': f'Invalid mode: {target_mode}. Use "testing" or "production"'
                }
            
            result = pipeline.switch_mode(new_mode)
            if result['success']:
                self._current_pipeline = pipeline
            
            return result
            
        except Exception as e:
            logger.error(f"Mode switch failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_current_status(self) -> Dict:
        """Get status of current pipeline and mode configuration"""
        
        if not self._current_pipeline:
            return {
                'pipeline_active': False,
                'message': 'No active pipeline'
            }
        
        status = self._current_pipeline.get_processing_status()
        status['pipeline_active'] = True
        
        return status
    
    def get_mode_comparison(self) -> Dict:
        """Get comparison of testing vs production mode features"""
        
        return {
            'testing_mode': {
                'description': 'Development and testing mode',
                'immediate_processing': True,
                'error_limits': False,
                'scheduling': False,
                'strict_validation': False,
                'detailed_logging': True,
                'use_cases': [
                    'Development testing',
                    'Manual processing runs', 
                    'Debugging and troubleshooting',
                    'Performance testing'
                ]
            },
            'production_mode': {
                'description': 'Live production processing mode',
                'immediate_processing': False,
                'error_limits': True,
                'scheduling': True,
                'strict_validation': True,
                'detailed_logging': False,
                'scheduled_runs': 'Tuesdays and Fridays at 2:00 AM',
                'error_limit': '15 consecutive errors',
                'cooldown_period': '23 hours',
                'use_cases': [
                    'Automated twice-weekly processing',
                    'Production sentence validation',
                    'Scheduled batch processing',
                    'Live system operation'
                ]
            },
            'switching': {
                'description': 'Mode can be switched dynamically',
                'preserves_state': True,
                'resets_errors': True,
                'scheduler_management': 'Automatic start/stop'
            }
        }

# Global mode manager instance
_mode_manager = None

def get_mode_manager() -> ModeManager:
    """Get or create the global mode manager instance"""
    global _mode_manager
    if _mode_manager is None:
        _mode_manager = ModeManager()
    return _mode_manager

# Convenience functions for common operations

def create_testing_pipeline() -> 'CopywritingEvaluatorPipeline':
    """Create a pipeline in testing mode"""
    return get_mode_manager().create_testing_pipeline()

def create_production_pipeline(enable_scheduler: bool = True) -> 'CopywritingEvaluatorPipeline':
    """Create a pipeline in production mode"""
    return get_mode_manager().create_production_pipeline(enable_scheduler)

def switch_mode(pipeline: 'CopywritingEvaluatorPipeline', target_mode: str) -> Dict:
    """Switch pipeline mode"""
    return get_mode_manager().switch_pipeline_mode(pipeline, target_mode)

def get_system_status() -> Dict:
    """Get overall system status"""
    return get_mode_manager().get_current_status()

def get_mode_info() -> Dict:
    """Get information about available modes"""
    return get_mode_manager().get_mode_comparison()