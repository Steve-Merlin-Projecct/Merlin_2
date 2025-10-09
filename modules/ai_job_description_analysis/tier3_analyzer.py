"""
Tier 3 Strategic Insights Job Analysis
Comprehensive application preparation guidance

This module implements the third tier of the 3-tier sequential batch processing system.
Tier 3 provides: Prestige Analysis, Cover Letter Insights

Processing Schedule: 4:30-6:00 AM (third batch tier)
Target: 1,500-2,000 output tokens per job
Response Time: < 4 seconds per job
"""

import logging
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from modules.database.database_manager import DatabaseManager
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.ai_job_description_analysis.prompts.tier3_strategic_prompt import create_tier3_strategic_prompt

logger = logging.getLogger(__name__)


class Tier3StrategicAnalyzer:
    """
    Tier 3 Strategic Insights - Application preparation guidance

    Analyzes: Prestige Analysis, Cover Letter Insights
    Uses cumulative Tier 1 + Tier 2 results for strategic guidance
    Target: 1,500-2,000 output tokens
    Processing Schedule: 4:30-6:00 AM
    """

    def __init__(self, model_override: Optional[str] = None):
        """
        Initialize Tier 3 analyzer

        Args:
            model_override: Optional model name to override default
                          (e.g., 'gemini-1.5-pro' for better strategic reasoning)
        """
        self.gemini_analyzer = GeminiJobAnalyzer()
        self.db = DatabaseManager()
        self.model_override = model_override

        # Set model override if provided
        if model_override:
            self.gemini_analyzer.current_model = model_override
            logger.info(f"Tier3StrategicAnalyzer using model override: {model_override}")

    def analyze_job(self, job_data: Dict, tier1_results: Dict, tier2_results: Dict) -> Dict:
        """
        Run Tier 3 strategic analysis on a single job

        Args:
            job_data: Job information dict
            tier1_results: Complete Tier 1 analysis results
            tier2_results: Complete Tier 2 analysis results

        Returns:
            Dict with analysis results and metadata
        """
        start_time = time.time()

        try:
            # Create Tier 3 prompt with cumulative context
            prompt = create_tier3_strategic_prompt([{
                'job_data': job_data,
                'tier1_results': tier1_results,
                'tier2_results': tier2_results
            }])

            # Call Gemini API
            response = self.gemini_analyzer._make_gemini_request(prompt)

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Parse and validate response
            analysis = self._parse_tier3_response(response)

            if not analysis:
                raise ValueError("Failed to parse Tier 3 response")

            # Extract usage stats
            usage = response.get('usage', {})
            tokens_used = usage.get('totalTokenCount', 0)

            # Store results in database
            self._store_tier3_results(
                job_id=job_data['id'],
                analysis=analysis,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms
            )

            logger.info(
                f"Tier 3 analysis completed for job {job_data['id']}: "
                f"{tokens_used} tokens, {response_time_ms}ms"
            )

            return {
                'success': True,
                'job_id': job_data['id'],
                'tier': 3,
                'analysis': analysis,
                'tokens_used': tokens_used,
                'response_time_ms': response_time_ms,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Tier 3 analysis failed for job {job_data.get('id')}: {e}")
            return {
                'success': False,
                'job_id': job_data.get('id'),
                'tier': 3,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _parse_tier3_response(self, response: Dict) -> Optional[Dict]:
        """Parse and validate Tier 3 response from Gemini"""
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

            # Return first result
            result = analysis_results[0]

            # Validate required fields
            required_fields = ["job_id", "prestige_analysis", "cover_letter_insight"]
            for field in required_fields:
                if field not in result:
                    logger.error(f"Missing required field in response: {field}")
                    return None

            # Add metadata
            result["analysis_timestamp"] = datetime.now().isoformat()
            result["model_used"] = self.model_override or self.gemini_analyzer.current_model
            result["analysis_version"] = "tier3-v1.0"
            result["tier"] = 3

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Tier 3 response: {e}")
            return None

    def _store_tier3_results(
        self,
        job_id: str,
        analysis: Dict,
        tokens_used: int,
        response_time_ms: int
    ):
        """Store Tier 3 results in database"""
        try:
            # Update job_analysis_tiers table
            update_query = """
                UPDATE job_analysis_tiers
                SET tier_3_completed = TRUE,
                    tier_3_timestamp = NOW(),
                    tier_3_tokens_used = %s,
                    tier_3_model = %s,
                    tier_3_response_time_ms = %s
                WHERE job_id = %s
            """

            model_name = self.model_override or self.gemini_analyzer.current_model

            self.db.execute_query(
                update_query,
                (tokens_used, model_name, response_time_ms, job_id)
            )

            # Store in normalized analysis tables
            from modules.ai_job_description_analysis.normalized_analysis_writer import NormalizedAnalysisWriter

            writer = NormalizedAnalysisWriter(self.db)
            writer.save_analysis_results([analysis])

            logger.info(f"Tier 3 results stored for job {job_id}")

        except Exception as e:
            logger.error(f"Failed to store Tier 3 results for job {job_id}: {e}")
            raise

    def batch_analyze(self, job_ids: List[str], batch_size: int = 50) -> Dict:
        """
        Batch process multiple jobs for Tier 3 analysis
        Loads Tier 1 + Tier 2 results for cumulative context

        Args:
            job_ids: List of job IDs to analyze
            batch_size: Number of jobs to process per API call

        Returns:
            Dict with batch processing statistics
        """
        logger.info(f"Starting Tier 3 batch analysis for {len(job_ids)} jobs")

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
                    # Get job data and previous tier results
                    job_data = self._get_job_data(job_id)
                    tier1_results = self._get_tier1_results(job_id)
                    tier2_results = self._get_tier2_results(job_id)

                    if not job_data:
                        logger.warning(f"Job {job_id} not found")
                        results['failed'] += 1
                        continue

                    if not tier1_results or not tier2_results:
                        logger.warning(f"Previous tier results not found for job {job_id}")
                        results['failed'] += 1
                        continue

                    # Analyze job with cumulative context
                    result = self.analyze_job(job_data, tier1_results, tier2_results)

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

            # Small delay between batches
            if i + batch_size < len(job_ids):
                time.sleep(1)

        # Calculate statistics
        total_time = time.time() - start_time
        results['total_time_seconds'] = total_time
        results['jobs_per_second'] = results['successful'] / total_time if total_time > 0 else 0

        if results['response_times']:
            results['avg_response_time_ms'] = sum(results['response_times']) / len(results['response_times'])
            results['p95_response_time_ms'] = sorted(results['response_times'])[int(len(results['response_times']) * 0.95)]

        logger.info(f"Tier 3 batch analysis completed: {results}")

        return results

    def _get_job_data(self, job_id: str) -> Optional[Dict]:
        """Fetch job data from database"""
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

    def _get_tier1_results(self, job_id: str) -> Optional[Dict]:
        """Fetch Tier 1 results for a job"""
        try:
            query = """
                SELECT tier1_analysis_data
                FROM analyzed_jobs
                WHERE job_id = %s
            """

            result = self.db.execute_query(query, (job_id,))

            if not result or len(result) == 0:
                return None

            tier1_data = result[0][0]
            if isinstance(tier1_data, str):
                tier1_data = json.loads(tier1_data)

            return tier1_data

        except Exception as e:
            logger.error(f"Failed to fetch Tier 1 results for {job_id}: {e}")
            return None

    def _get_tier2_results(self, job_id: str) -> Optional[Dict]:
        """Fetch Tier 2 results for a job"""
        try:
            query = """
                SELECT tier2_analysis_data
                FROM analyzed_jobs
                WHERE job_id = %s
            """

            result = self.db.execute_query(query, (job_id,))

            if not result or len(result) == 0:
                return None

            tier2_data = result[0][0]
            if isinstance(tier2_data, str):
                tier2_data = json.loads(tier2_data)

            return tier2_data

        except Exception as e:
            logger.error(f"Failed to fetch Tier 2 results for {job_id}: {e}")
            return None

    def get_tier2_completed_jobs(self, limit: int = 100) -> List[str]:
        """
        Get list of job IDs that have Tier 1 + 2 complete but need Tier 3

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of job IDs
        """
        try:
            query = """
                SELECT job_id
                FROM job_analysis_tiers
                WHERE tier_1_completed = TRUE
                  AND tier_2_completed = TRUE
                  AND (tier_3_completed IS NULL OR tier_3_completed = FALSE)
                ORDER BY tier_2_timestamp DESC
                LIMIT %s
            """

            results = self.db.execute_query(query, (limit,))

            if not results:
                return []

            return [str(row[0]) for row in results]

        except Exception as e:
            logger.error(f"Failed to get Tier 2 completed jobs: {e}")
            return []
