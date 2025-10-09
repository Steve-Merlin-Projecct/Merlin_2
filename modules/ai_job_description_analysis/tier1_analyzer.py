"""
Tier 1 Core Job Analysis
Focused analysis for essential job data extraction

This module implements the first tier of the 3-tier sequential batch processing system.
Tier 1 extracts: Skills, Authenticity, Industry Classification, Structured Data

Processing Schedule: 2:00-3:00 AM (first batch tier)
Target: 1,500-2,000 output tokens per job
Response Time: < 3 seconds per job
"""

import logging
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from modules.database.database_manager import DatabaseManager
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt

logger = logging.getLogger(__name__)


class Tier1CoreAnalyzer:
    """
    Tier 1 Core Analysis - Essential job data extraction

    Extracts: Skills, Authenticity, Industry Classification, Structured Data
    Target: 1,500-2,000 output tokens
    Processing Schedule: 2:00-3:00 AM
    """

    def __init__(self, model_override: Optional[str] = None):
        """
        Initialize Tier 1 analyzer

        Args:
            model_override: Optional model name to override default
                          (used for model performance testing)
        """
        self.gemini_analyzer = GeminiJobAnalyzer()
        self.db = DatabaseManager()
        self.model_override = model_override

        # Set model override if provided
        if model_override:
            self.gemini_analyzer.current_model = model_override
            logger.info(f"Tier1CoreAnalyzer using model override: {model_override}")

    def analyze_job(self, job_data: Dict) -> Dict:
        """
        Run Tier 1 core analysis on a single job

        Args:
            job_data: Job information dict with keys:
                     - id: Job ID
                     - title: Job title
                     - description: Job description
                     - company: Company name (optional)

        Returns:
            Dict with analysis results and metadata:
            {
                'success': bool,
                'job_id': str,
                'tier': 1,
                'analysis': dict,  # The actual analysis results
                'tokens_used': int,
                'response_time_ms': int,
                'timestamp': str
            }
        """
        start_time = time.time()

        try:
            # Create optimized Tier 1 prompt
            prompt = create_tier1_core_prompt([job_data])

            # Call Gemini API
            response = self.gemini_analyzer._make_gemini_request(prompt)

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Parse and validate response
            analysis = self._parse_tier1_response(response)

            if not analysis:
                raise ValueError("Failed to parse Tier 1 response")

            # Extract usage stats
            usage = response.get('usage', {})
            tokens_used = usage.get('totalTokenCount', 0)

            # Store results in database
            self._store_tier1_results(
                job_id=job_data['id'],
                analysis=analysis,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms
            )

            logger.info(
                f"Tier 1 analysis completed for job {job_data['id']}: "
                f"{tokens_used} tokens, {response_time_ms}ms"
            )

            return {
                'success': True,
                'job_id': job_data['id'],
                'tier': 1,
                'analysis': analysis,
                'tokens_used': tokens_used,
                'response_time_ms': response_time_ms,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Tier 1 analysis failed for job {job_data.get('id')}: {e}")
            return {
                'success': False,
                'job_id': job_data.get('id'),
                'tier': 1,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _parse_tier1_response(self, response: Dict) -> Optional[Dict]:
        """
        Parse and validate Tier 1 response from Gemini

        Args:
            response: Raw API response from Gemini

        Returns:
            Parsed analysis dict or None if parsing fails
        """
        try:
            # Extract content from Gemini response
            content = response.get("candidates", [{}])[0].get("content", {})
            text = content.get("parts", [{}])[0].get("text", "")

            if not text:
                logger.error("Empty response text from Gemini")
                return None

            # Parse JSON response
            parsed_data = json.loads(text)
            analysis_results = parsed_data.get("analysis_results", [])

            if not analysis_results:
                logger.error("No analysis_results in response")
                return None

            # Return first result (single job analysis)
            result = analysis_results[0]

            # Validate required fields
            required_fields = ["job_id", "authenticity_check", "classification", "structured_data"]
            for field in required_fields:
                if field not in result:
                    logger.error(f"Missing required field in response: {field}")
                    return None

            # Add metadata
            result["analysis_timestamp"] = datetime.now().isoformat()
            result["model_used"] = self.model_override or self.gemini_analyzer.current_model
            result["analysis_version"] = "tier1-v1.0"
            result["tier"] = 1

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response text: {text[:500]}...")
            return None
        except Exception as e:
            logger.error(f"Error parsing Tier 1 response: {e}")
            return None

    def _store_tier1_results(
        self,
        job_id: str,
        analysis: Dict,
        tokens_used: int,
        response_time_ms: int
    ):
        """
        Store Tier 1 results in database

        Updates:
        1. job_analysis_tiers table (marks tier_1_completed = TRUE)
        2. Existing normalized analysis tables (via existing writer)

        Args:
            job_id: Job ID
            analysis: Parsed analysis results
            tokens_used: Token count from API
            response_time_ms: Response time in milliseconds
        """
        try:
            # 1. Update job_analysis_tiers table
            upsert_query = """
                INSERT INTO job_analysis_tiers
                (job_id, tier_1_completed, tier_1_timestamp, tier_1_tokens_used,
                 tier_1_model, tier_1_response_time_ms)
                VALUES (%s, TRUE, NOW(), %s, %s, %s)
                ON CONFLICT (job_id)
                DO UPDATE SET
                    tier_1_completed = TRUE,
                    tier_1_timestamp = NOW(),
                    tier_1_tokens_used = %s,
                    tier_1_model = %s,
                    tier_1_response_time_ms = %s
            """

            model_name = self.model_override or self.gemini_analyzer.current_model

            self.db.execute_query(
                upsert_query,
                (job_id, tokens_used, model_name, response_time_ms,
                 tokens_used, model_name, response_time_ms)
            )

            # 2. Store in existing normalized analysis tables
            from modules.ai_job_description_analysis.normalized_analysis_writer import NormalizedAnalysisWriter

            writer = NormalizedAnalysisWriter(self.db)
            writer.save_analysis_results([analysis])

            logger.info(f"Tier 1 results stored for job {job_id}")

        except Exception as e:
            logger.error(f"Failed to store Tier 1 results for job {job_id}: {e}")
            raise

    def batch_analyze(self, job_ids: List[str], batch_size: int = 50) -> Dict:
        """
        Batch process multiple jobs for Tier 1 analysis

        Args:
            job_ids: List of job IDs to analyze
            batch_size: Number of jobs to process per API call

        Returns:
            Dict with batch processing statistics:
            {
                'total_jobs': int,
                'successful': int,
                'failed': int,
                'total_tokens': int,
                'avg_response_time_ms': float,
                'jobs_per_second': float
            }
        """
        logger.info(f"Starting Tier 1 batch analysis for {len(job_ids)} jobs")

        start_time = time.time()
        results = {
            'total_jobs': len(job_ids),
            'successful': 0,
            'failed': 0,
            'total_tokens': 0,
            'response_times': []
        }

        for i in range(0, len(job_ids), batch_size):
            batch = job_ids[i:i + batch_size]

            for job_id in batch:
                try:
                    # Get job data from database
                    job_data = self._get_job_data(job_id)

                    if not job_data:
                        logger.warning(f"Job {job_id} not found in database")
                        results['failed'] += 1
                        continue

                    # Analyze job
                    result = self.analyze_job(job_data)

                    if result['success']:
                        results['successful'] += 1
                        results['total_tokens'] += result.get('tokens_used', 0)
                        results['response_times'].append(result.get('response_time_ms', 0))
                    else:
                        results['failed'] += 1

                except Exception as e:
                    logger.error(f"Error processing job {job_id}: {e}")
                    results['failed'] += 1
                    continue

            # Small delay between batches to respect rate limits
            if i + batch_size < len(job_ids):
                time.sleep(1)

        # Calculate statistics
        total_time = time.time() - start_time
        results['total_time_seconds'] = total_time
        results['jobs_per_second'] = results['successful'] / total_time if total_time > 0 else 0

        if results['response_times']:
            results['avg_response_time_ms'] = sum(results['response_times']) / len(results['response_times'])
            results['p95_response_time_ms'] = sorted(results['response_times'])[int(len(results['response_times']) * 0.95)]

        logger.info(f"Tier 1 batch analysis completed: {results}")

        return results

    def _get_job_data(self, job_id: str) -> Optional[Dict]:
        """
        Fetch job data from database

        Args:
            job_id: Job ID to fetch

        Returns:
            Dict with job data or None if not found
        """
        try:
            query = """
                SELECT j.id, j.job_title as title, j.job_description as description,
                       c.name as company
                FROM jobs j
                LEFT JOIN companies c ON j.company_id = c.id
                WHERE j.id = %s
            """

            result = self.db.execute_query(query, (job_id,))

            if not result or len(result) == 0:
                return None

            row = result[0]
            return {
                'id': str(row[0]),
                'title': row[1],
                'description': row[2],
                'company': row[3] or 'Unknown'
            }

        except Exception as e:
            logger.error(f"Failed to fetch job data for {job_id}: {e}")
            return None

    def get_unanalyzed_jobs(self, limit: int = 100) -> List[str]:
        """
        Get list of job IDs that need Tier 1 analysis

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of job IDs
        """
        try:
            query = """
                SELECT j.id
                FROM jobs j
                LEFT JOIN job_analysis_tiers jat ON j.id = jat.job_id
                WHERE jat.tier_1_completed IS NULL OR jat.tier_1_completed = FALSE
                ORDER BY j.created_at DESC
                LIMIT %s
            """

            results = self.db.execute_query(query, (limit,))

            if not results:
                return []

            return [str(row[0]) for row in results]

        except Exception as e:
            logger.error(f"Failed to get unanalyzed jobs: {e}")
            return []
