"""
Integration Tests for Sequential Batch Workflow
Tests complete three-tier analysis system end-to-end

Test Coverage:
- Sequential tier progression (Tier 1 -> Tier 2 -> Tier 3)
- Context passing between tiers
- Time window detection
- API endpoints
- Error handling and resilience
"""

import unittest
import json
from datetime import datetime, time as dt_time
from unittest.mock import Mock, patch, MagicMock
from modules.ai_job_description_analysis.sequential_batch_scheduler import (
    SequentialBatchScheduler,
    get_status
)


class TestSequentialBatchScheduler(unittest.TestCase):
    """Test cases for SequentialBatchScheduler"""

    def setUp(self):
        """Set up test fixtures"""
        self.scheduler = SequentialBatchScheduler(batch_size=10)

    def test_time_window_detection_tier1(self):
        """Test Tier 1 time window detection (2:00-3:00 AM)"""
        # Inside Tier 1 window
        test_time = datetime(2025, 10, 9, 2, 30, 0)  # 2:30 AM
        self.assertTrue(self.scheduler.is_in_tier1_window(test_time))
        self.assertEqual(self.scheduler.get_active_tier(test_time), 1)

        # Start of window
        test_time = datetime(2025, 10, 9, 2, 0, 0)  # 2:00 AM
        self.assertTrue(self.scheduler.is_in_tier1_window(test_time))

        # End of window (exclusive)
        test_time = datetime(2025, 10, 9, 3, 0, 0)  # 3:00 AM
        self.assertFalse(self.scheduler.is_in_tier1_window(test_time))

        # Outside window
        test_time = datetime(2025, 10, 9, 1, 30, 0)  # 1:30 AM
        self.assertFalse(self.scheduler.is_in_tier1_window(test_time))

    def test_time_window_detection_tier2(self):
        """Test Tier 2 time window detection (3:00-4:30 AM)"""
        # Inside Tier 2 window
        test_time = datetime(2025, 10, 9, 3, 45, 0)  # 3:45 AM
        self.assertTrue(self.scheduler.is_in_tier2_window(test_time))
        self.assertEqual(self.scheduler.get_active_tier(test_time), 2)

        # Start of window
        test_time = datetime(2025, 10, 9, 3, 0, 0)  # 3:00 AM
        self.assertTrue(self.scheduler.is_in_tier2_window(test_time))

        # End of window (exclusive)
        test_time = datetime(2025, 10, 9, 4, 30, 0)  # 4:30 AM
        self.assertFalse(self.scheduler.is_in_tier2_window(test_time))

    def test_time_window_detection_tier3(self):
        """Test Tier 3 time window detection (4:30-6:00 AM)"""
        # Inside Tier 3 window
        test_time = datetime(2025, 10, 9, 5, 15, 0)  # 5:15 AM
        self.assertTrue(self.scheduler.is_in_tier3_window(test_time))
        self.assertEqual(self.scheduler.get_active_tier(test_time), 3)

        # Start of window
        test_time = datetime(2025, 10, 9, 4, 30, 0)  # 4:30 AM
        self.assertTrue(self.scheduler.is_in_tier3_window(test_time))

        # End of window (exclusive)
        test_time = datetime(2025, 10, 9, 6, 0, 0)  # 6:00 AM
        self.assertFalse(self.scheduler.is_in_tier3_window(test_time))

    def test_no_active_tier_outside_windows(self):
        """Test that no tier is active outside processing windows"""
        # 10:00 AM - outside all windows
        test_time = datetime(2025, 10, 9, 10, 0, 0)
        self.assertIsNone(self.scheduler.get_active_tier(test_time))

        # 1:00 AM - before all windows
        test_time = datetime(2025, 10, 9, 1, 0, 0)
        self.assertIsNone(self.scheduler.get_active_tier(test_time))

        # 7:00 AM - after all windows
        test_time = datetime(2025, 10, 9, 7, 0, 0)
        self.assertIsNone(self.scheduler.get_active_tier(test_time))

    def test_model_override_initialization(self):
        """Test scheduler initialization with model overrides"""
        scheduler = SequentialBatchScheduler(
            tier1_model='gemini-2.0-flash-lite-001',
            tier2_model='gemini-2.0-flash-001',
            tier3_model='gemini-1.5-pro'
        )

        self.assertEqual(
            scheduler.tier1_analyzer.gemini_analyzer.current_model,
            'gemini-2.0-flash-lite-001'
        )
        self.assertEqual(
            scheduler.tier2_analyzer.gemini_analyzer.current_model,
            'gemini-2.0-flash-001'
        )
        self.assertEqual(
            scheduler.tier3_analyzer.gemini_analyzer.current_model,
            'gemini-1.5-pro'
        )

    @patch('modules.ai_job_description_analysis.tier1_analyzer.Tier1CoreAnalyzer.get_unanalyzed_jobs')
    @patch('modules.ai_job_description_analysis.tier1_analyzer.Tier1CoreAnalyzer.batch_analyze')
    def test_tier1_batch_execution(self, mock_batch_analyze, mock_get_jobs):
        """Test Tier 1 batch execution"""
        # Mock get_unanalyzed_jobs to return test job IDs
        mock_get_jobs.return_value = ['job1', 'job2', 'job3']

        # Mock batch_analyze to return success results
        mock_batch_analyze.return_value = {
            'total_jobs': 3,
            'successful': 3,
            'failed': 0,
            'total_tokens': 5400,
            'avg_response_time_ms': 2100
        }

        # Run Tier 1 batch
        results = self.scheduler.run_tier1_batch()

        # Verify results
        self.assertEqual(results['tier'], 1)
        self.assertEqual(results['successful'], 3)
        self.assertEqual(results['failed'], 0)
        self.assertEqual(results['total_tokens'], 5400)

        # Verify methods were called
        mock_get_jobs.assert_called_once()
        mock_batch_analyze.assert_called_once()

    @patch('modules.ai_job_description_analysis.tier2_analyzer.Tier2EnhancedAnalyzer.get_tier1_completed_jobs')
    @patch('modules.ai_job_description_analysis.tier2_analyzer.Tier2EnhancedAnalyzer.batch_analyze')
    def test_tier2_batch_execution(self, mock_batch_analyze, mock_get_jobs):
        """Test Tier 2 batch execution"""
        mock_get_jobs.return_value = ['job1', 'job2']

        mock_batch_analyze.return_value = {
            'total_jobs': 2,
            'successful': 2,
            'failed': 0,
            'total_tokens': 2800
        }

        results = self.scheduler.run_tier2_batch()

        self.assertEqual(results['tier'], 2)
        self.assertEqual(results['successful'], 2)

    @patch('modules.ai_job_description_analysis.tier3_analyzer.Tier3StrategicAnalyzer.get_tier2_completed_jobs')
    @patch('modules.ai_job_description_analysis.tier3_analyzer.Tier3StrategicAnalyzer.batch_analyze')
    def test_tier3_batch_execution(self, mock_batch_analyze, mock_get_jobs):
        """Test Tier 3 batch execution"""
        mock_get_jobs.return_value = ['job1']

        mock_batch_analyze.return_value = {
            'total_jobs': 1,
            'successful': 1,
            'failed': 0,
            'total_tokens': 1800
        }

        results = self.scheduler.run_tier3_batch()

        self.assertEqual(results['tier'], 3)
        self.assertEqual(results['successful'], 1)

    def test_no_jobs_handling(self):
        """Test graceful handling when no jobs are available"""
        with patch('modules.ai_job_description_analysis.tier1_analyzer.Tier1CoreAnalyzer.get_unanalyzed_jobs') as mock:
            mock.return_value = []

            results = self.scheduler.run_tier1_batch()

            self.assertEqual(results['total_jobs'], 0)
            self.assertEqual(results['successful'], 0)
            self.assertIn('message', results)

    @patch('modules.ai_job_description_analysis.tier1_analyzer.Tier1CoreAnalyzer.batch_analyze')
    @patch('modules.ai_job_description_analysis.tier2_analyzer.Tier2EnhancedAnalyzer.batch_analyze')
    @patch('modules.ai_job_description_analysis.tier3_analyzer.Tier3StrategicAnalyzer.batch_analyze')
    def test_full_sequential_batch(self, mock_tier3, mock_tier2, mock_tier1):
        """Test complete sequential batch execution"""
        # Mock all tier batch_analyze methods
        mock_tier1.return_value = {
            'total_jobs': 10,
            'successful': 9,
            'failed': 1,
            'total_tokens': 18000
        }

        mock_tier2.return_value = {
            'total_jobs': 9,
            'successful': 8,
            'failed': 1,
            'total_tokens': 11000
        }

        mock_tier3.return_value = {
            'total_jobs': 8,
            'successful': 7,
            'failed': 1,
            'total_tokens': 14000
        }

        # Mock get_jobs methods
        with patch.multiple(
            'modules.ai_job_description_analysis.tier1_analyzer.Tier1CoreAnalyzer',
            get_unanalyzed_jobs=Mock(return_value=['job1'] * 10)
        ), patch.multiple(
            'modules.ai_job_description_analysis.tier2_analyzer.Tier2EnhancedAnalyzer',
            get_tier1_completed_jobs=Mock(return_value=['job1'] * 9)
        ), patch.multiple(
            'modules.ai_job_description_analysis.tier3_analyzer.Tier3StrategicAnalyzer',
            get_tier2_completed_jobs=Mock(return_value=['job1'] * 8)
        ):
            # Run full sequential batch
            results = self.scheduler.run_full_sequential_batch()

            # Verify execution type
            self.assertEqual(results['execution_type'], 'full_sequential_batch')

            # Verify all tiers executed
            self.assertIn('tier1', results)
            self.assertIn('tier2', results)
            self.assertIn('tier3', results)

            # Verify summary
            self.assertEqual(results['summary']['total_jobs_processed'], 24)  # 9 + 8 + 7
            self.assertEqual(results['summary']['total_failures'], 3)
            self.assertEqual(results['summary']['total_tokens'], 43000)  # 18000 + 11000 + 14000

    def test_max_jobs_limit(self):
        """Test that max_jobs parameter limits processing"""
        with patch('modules.ai_job_description_analysis.tier1_analyzer.Tier1CoreAnalyzer.get_unanalyzed_jobs') as mock:
            mock.return_value = ['job1'] * 10

            # Run with max_jobs=5
            self.scheduler.run_tier1_batch(max_jobs=5)

            # Verify get_unanalyzed_jobs called with limit=5
            mock.assert_called_with(limit=5)


class TestSchedulerIntegration(unittest.TestCase):
    """Integration tests for scheduler with mocked database"""

    @patch('modules.ai_job_description_analysis.sequential_batch_scheduler.DatabaseManager')
    def test_processing_status_query(self, mock_db_manager):
        """Test get_processing_status database query"""
        # Mock database response
        mock_db = Mock()
        mock_db.execute_query.return_value = [(10, 5, 3, 100)]
        mock_db_manager.return_value = mock_db

        scheduler = SequentialBatchScheduler()
        status = scheduler.get_processing_status()

        # Verify status structure
        self.assertEqual(status['pending_tier1'], 10)
        self.assertEqual(status['pending_tier2'], 5)
        self.assertEqual(status['pending_tier3'], 3)
        self.assertEqual(status['fully_analyzed'], 100)
        self.assertIn('active_tier', status)
        self.assertIn('current_time', status)

    @patch('modules.ai_job_description_analysis.sequential_batch_scheduler.DatabaseManager')
    def test_status_error_handling(self, mock_db_manager):
        """Test error handling in get_processing_status"""
        # Mock database error
        mock_db = Mock()
        mock_db.execute_query.side_effect = Exception("Database connection failed")
        mock_db_manager.return_value = mock_db

        scheduler = SequentialBatchScheduler()
        status = scheduler.get_processing_status()

        # Verify error handling
        self.assertIn('error', status)
        self.assertEqual(status['pending_tier1'], 0)
        self.assertEqual(status['pending_tier2'], 0)
        self.assertEqual(status['pending_tier3'], 0)


class TestAPIRoutes(unittest.TestCase):
    """Test API routes for tiered analysis"""

    def setUp(self):
        """Set up Flask test client"""
        from flask import Flask
        from modules.ai_job_description_analysis.api_routes_tiered import tiered_analysis_bp
        import os

        # Set test API key
        os.environ['WEBHOOK_API_KEY'] = 'test_api_key_12345'

        self.app = Flask(__name__)
        self.app.register_blueprint(tiered_analysis_bp)
        self.client = self.app.test_client()

        self.headers = {'X-API-Key': 'test_api_key_12345'}

    def test_health_endpoint_no_auth(self):
        """Test health endpoint doesn't require authentication"""
        response = self.client.get('/api/analyze/health')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'tiered_job_analysis')

    def test_status_endpoint_requires_auth(self):
        """Test status endpoint requires API key"""
        # No API key
        response = self.client.get('/api/analyze/status')
        self.assertEqual(response.status_code, 401)

        # Invalid API key
        response = self.client.get(
            '/api/analyze/status',
            headers={'X-API-Key': 'invalid_key'}
        )
        self.assertEqual(response.status_code, 401)

    @patch('modules.ai_job_description_analysis.sequential_batch_scheduler.SequentialBatchScheduler.run_tier1_batch')
    def test_tier1_endpoint(self, mock_run_tier1):
        """Test POST /api/analyze/tier1 endpoint"""
        mock_run_tier1.return_value = {
            'tier': 1,
            'total_jobs': 10,
            'successful': 9,
            'failed': 1,
            'total_tokens': 18000
        }

        response = self.client.post(
            '/api/analyze/tier1',
            headers=self.headers,
            json={'max_jobs': 10}
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['tier'], 1)
        self.assertEqual(data['successful'], 9)
        self.assertIn('timestamp', data)

    @patch('modules.ai_job_description_analysis.sequential_batch_scheduler.SequentialBatchScheduler.run_tier2_batch')
    def test_tier2_endpoint(self, mock_run_tier2):
        """Test POST /api/analyze/tier2 endpoint"""
        mock_run_tier2.return_value = {
            'tier': 2,
            'successful': 8,
            'failed': 0
        }

        response = self.client.post(
            '/api/analyze/tier2',
            headers=self.headers,
            json={'model_override': 'gemini-2.0-flash-001'}
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['tier'], 2)

    @patch('modules.ai_job_description_analysis.sequential_batch_scheduler.SequentialBatchScheduler.run_tier3_batch')
    def test_tier3_endpoint(self, mock_run_tier3):
        """Test POST /api/analyze/tier3 endpoint"""
        mock_run_tier3.return_value = {
            'tier': 3,
            'successful': 7,
            'failed': 0
        }

        response = self.client.post(
            '/api/analyze/tier3',
            headers=self.headers,
            json={'model_override': 'gemini-1.5-pro'}
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['tier'], 3)

    @patch('modules.ai_job_description_analysis.sequential_batch_scheduler.SequentialBatchScheduler.run_full_sequential_batch')
    def test_sequential_batch_endpoint(self, mock_run_sequential):
        """Test POST /api/analyze/sequential-batch endpoint"""
        mock_run_sequential.return_value = {
            'execution_type': 'full_sequential_batch',
            'total_time_seconds': 150.5,
            'tier1': {'successful': 10, 'failed': 0},
            'tier2': {'successful': 9, 'failed': 1},
            'tier3': {'successful': 8, 'failed': 1},
            'summary': {
                'total_jobs_processed': 27,
                'total_failures': 2,
                'total_tokens': 48000
            }
        }

        response = self.client.post(
            '/api/analyze/sequential-batch',
            headers=self.headers,
            json={
                'tier1_max_jobs': 10,
                'tier2_max_jobs': 10,
                'tier3_max_jobs': 10
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['execution_type'], 'full_sequential_batch')
        self.assertEqual(data['summary']['total_jobs_processed'], 27)

    @patch('modules.ai_job_description_analysis.sequential_batch_scheduler.get_status')
    def test_status_endpoint_success(self, mock_get_status):
        """Test GET /api/analyze/status endpoint"""
        mock_get_status.return_value = {
            'pending_tier1': 50,
            'pending_tier2': 25,
            'pending_tier3': 10,
            'fully_analyzed': 500,
            'active_tier': None
        }

        response = self.client.get('/api/analyze/status', headers=self.headers)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['pending_tier1'], 50)
        self.assertEqual(data['fully_analyzed'], 500)

    def test_endpoint_error_handling(self):
        """Test error handling in API endpoints"""
        with patch('modules.ai_job_description_analysis.sequential_batch_scheduler.SequentialBatchScheduler.run_tier1_batch') as mock:
            mock.side_effect = Exception("Database error")

            response = self.client.post(
                '/api/analyze/tier1',
                headers=self.headers
            )

            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('message', data)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions for manual execution"""

    @patch('modules.ai_job_description_analysis.sequential_batch_scheduler.SequentialBatchScheduler.run_tier1_batch')
    def test_run_tier1_now(self, mock_run_tier1):
        """Test run_tier1_now convenience function"""
        from modules.ai_job_description_analysis.sequential_batch_scheduler import run_tier1_now

        mock_run_tier1.return_value = {'tier': 1, 'successful': 5}

        result = run_tier1_now(max_jobs=10)

        self.assertEqual(result['tier'], 1)
        mock_run_tier1.assert_called_once_with(max_jobs=10)

    @patch('modules.ai_job_description_analysis.sequential_batch_scheduler.SequentialBatchScheduler.get_processing_status')
    def test_get_status_convenience(self, mock_get_status):
        """Test get_status convenience function"""
        from modules.ai_job_description_analysis.sequential_batch_scheduler import get_status

        mock_get_status.return_value = {'pending_tier1': 10}

        result = get_status()

        self.assertEqual(result['pending_tier1'], 10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
