#!/usr/bin/env python3
"""
Simplified Seed Sentence Processing Pipeline
Processes seed sentences directly through 5-stage evaluation (no variations)

This script:
1. Parses seed sentences from text file
2. Inserts them into database
3. Processes through 5-stage copywriting evaluator
4. Generates comprehensive report

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import re
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database.database_manager import DatabaseManager
from modules.content.copywriting_evaluator.pipeline_processor import (
    CopywritingEvaluatorPipeline,
    PipelineConfig,
    ProcessingMode
)


class SimplifiedSeedProcessor:
    """
    Simplified pipeline processor for seed sentences only (no variations)
    """

    def __init__(self):
        """Initialize processor"""
        self.db = DatabaseManager()
        self.pipeline = CopywritingEvaluatorPipeline(
            PipelineConfig(mode=ProcessingMode.TESTING)
        )

        # Processing statistics
        self.stats = {
            'total_seeds': 0,
            'seeds_inserted': 0,
            'resume_sentences': 0,
            'cover_letter_sentences': 0,
            'stage_1_approved': 0,
            'stage_1_rejected': 0,
            'stage_2_approved': 0,
            'stage_2_rejected': 0,
            'stage_3_completed': 0,
            'stage_4_completed': 0,
            'stage_5_completed': 0,
            'production_ready': 0,
            'errors': []
        }

        logger.info("Simplified seed processor initialized")

    def parse_seed_sentences(self, file_path: str) -> List[Dict]:
        """
        Parse seed sentences from text file

        Args:
            file_path: Path to seed sentences text file

        Returns:
            List of parsed seed sentence dictionaries
        """
        logger.info(f"Parsing seed sentences from: {file_path}")

        sentences = []
        current_category = None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and header lines
                    if not line or line.startswith('=') or line.startswith('MARKETING AUTOMATION'):
                        continue

                    # Check for category headers
                    category_match = re.match(r'^([A-Z\s&]+)\s*\(\d+\s+sentences\)$', line)
                    if category_match:
                        current_category = category_match.group(1).strip()
                        logger.debug(f"Found category: {current_category}")
                        continue

                    # Parse sentence lines with employer tags
                    sentence_match = re.match(r'^\[([^\]]+)\]\s+(.+)$', line)
                    if sentence_match:
                        employer = sentence_match.group(1).strip()
                        content = sentence_match.group(2).strip()

                        # Determine document type based on content
                        # Resume sentences typically have metrics/achievements
                        # Cover letter sentences are more narrative
                        has_metrics = bool(re.search(r'\d+%|\d+\+|\d+x|\$\d+|\d+ million', content))
                        intended_document = 'resume' if has_metrics else 'cover_letter'

                        sentence = {
                            'content_text': content,
                            'employer': employer,
                            'category': current_category,
                            'intended_document': intended_document,
                            'status': 'Draft',
                            'tone': 'Confident',  # Default tone
                            'line_number': line_num
                        }

                        sentences.append(sentence)

            self.stats['total_seeds'] = len(sentences)
            self.stats['resume_sentences'] = sum(1 for s in sentences if s['intended_document'] == 'resume')
            self.stats['cover_letter_sentences'] = sum(1 for s in sentences if s['intended_document'] == 'cover_letter')

            logger.info(f"Parsed {len(sentences)} seed sentences ({self.stats['resume_sentences']} resume, {self.stats['cover_letter_sentences']} cover letter)")

            return sentences

        except Exception as e:
            logger.error(f"Failed to parse seed sentences: {str(e)}")
            self.stats['errors'].append(f"Parse error: {str(e)}")
            raise

    def load_atomic_truths(self, file_path: str) -> List[str]:
        """
        Load atomic truth statements from file

        Args:
            file_path: Path to atomic truths file

        Returns:
            List of atomic truth statements
        """
        logger.info(f"Loading atomic truths from: {file_path}")

        truths = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()

                    # Skip headers and empty lines
                    if not line or line.startswith('=') or line.startswith('MARKETING') or line.startswith('Simple'):
                        continue

                    # Skip section headers
                    if line.startswith('[') and line.endswith('TAKEN'):
                        continue

                    # Parse truth statements
                    truth_match = re.match(r'^\[([^\]]+)\]\s+(.+)$', line)
                    if truth_match:
                        employer = truth_match.group(1).strip()
                        truth = truth_match.group(2).strip()
                        truths.append(f"[{employer}] {truth}")

            logger.info(f"Loaded {len(truths)} atomic truth statements")
            return truths

        except Exception as e:
            logger.error(f"Failed to load atomic truths: {str(e)}")
            self.stats['errors'].append(f"Atomic truths load error: {str(e)}")
            raise

    async def insert_seed_sentences(self, sentences: List[Dict]) -> List[str]:
        """
        Insert seed sentences into database

        Args:
            sentences: List of seed sentence dictionaries

        Returns:
            List of inserted sentence IDs
        """
        logger.info(f"Inserting {len(sentences)} seed sentences into database")

        inserted_ids = []

        try:
            for sentence in sentences:
                # Determine target table
                table_name = f"sentence_bank_{sentence['intended_document']}"

                # Use minimal columns that exist in both tables
                insert_query = f"""
                    INSERT INTO {table_name}
                    (content_text, status, tone,
                     keyword_filter_status, truthfulness_status,
                     canadian_spelling_status, tone_analysis_status,
                     skill_analysis_status, created_at)
                    VALUES (%s, %s, %s,
                            'pending', 'pending', 'pending', 'pending', 'pending',
                            CURRENT_TIMESTAMP)
                    RETURNING id
                """

                params = (
                    sentence['content_text'],
                    sentence['status'],
                    sentence['tone']
                )

                result = self.db.execute_query(insert_query, params)
                if result and len(result) > 0:
                    sentence_id = result[0][0]
                    inserted_ids.append(sentence_id)
                    sentence['id'] = sentence_id
                    sentence['table_name'] = table_name

            self.stats['seeds_inserted'] = len(inserted_ids)
            logger.info(f"Successfully inserted {len(inserted_ids)} seed sentences")

            return inserted_ids

        except Exception as e:
            logger.error(f"Failed to insert seed sentences: {str(e)}")
            self.stats['errors'].append(f"Database insert error: {str(e)}")
            raise

    async def process_through_pipeline(self, atomic_truths: List[str]):
        """
        Process all pending sentences through the 5-stage pipeline

        Args:
            atomic_truths: List of atomic truth statements for stage 2
        """
        logger.info("Starting 5-stage pipeline processing")

        try:
            # Process both tables
            for table_name in ['sentence_bank_resume', 'sentence_bank_cover_letter']:
                logger.info(f"\nProcessing table: {table_name}")
                logger.info("=" * 60)

                # Run pipeline
                stats = await self.pipeline.process_sentences(table_name=table_name)

                logger.info(f"\nPipeline stats for {table_name}:")
                logger.info(f"  Total sentences: {stats.total_sentences}")
                logger.info(f"  Processed: {stats.processed_sentences}")
                logger.info(f"  Filtered (rejected): {stats.filtered_sentences}")
                logger.info(f"  Errors: {stats.error_count}")

                # Update statistics
                if stats.stage_stats:
                    stage_1 = stats.stage_stats.get('keyword_filter', {})
                    self.stats['stage_1_approved'] += stage_1.get('approved', 0)
                    self.stats['stage_1_rejected'] += stage_1.get('rejected', 0)

                    stage_2 = stats.stage_stats.get('truthfulness', {})
                    self.stats['stage_2_approved'] += stage_2.get('approved', 0)
                    self.stats['stage_2_rejected'] += stage_2.get('rejected', 0)

                    stage_3 = stats.stage_stats.get('canadian_spelling', {})
                    self.stats['stage_3_completed'] += stage_3.get('processed', 0)

                    stage_4 = stats.stage_stats.get('tone_analysis', {})
                    self.stats['stage_4_completed'] += stage_4.get('processed', 0)

                    stage_5 = stats.stage_stats.get('skill_analysis', {})
                    self.stats['stage_5_completed'] += stage_5.get('processed', 0)

            logger.info("\nPipeline processing complete")

        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            self.stats['errors'].append(f"Pipeline error: {str(e)}")
            raise

    async def verify_and_report(self) -> Dict:
        """
        Verify database storage and generate comprehensive report

        Returns:
            Dictionary with complete processing report
        """
        logger.info("Generating verification report")

        try:
            report = {
                'processing_summary': self.stats.copy(),
                'timestamp': datetime.now().isoformat(),
                'table_statistics': {}
            }

            # Query database for verification
            for table_name in ['sentence_bank_resume', 'sentence_bank_cover_letter']:
                table_stats = self._get_table_statistics(table_name)
                report['table_statistics'][table_name] = table_stats

            # Calculate production-ready count
            total_production_ready = sum(
                stats.get('production_ready', 0)
                for stats in report['table_statistics'].values()
            )
            self.stats['production_ready'] = total_production_ready
            report['processing_summary']['production_ready'] = total_production_ready

            # Generate sample queries
            report['sample_queries'] = self._generate_sample_queries()

            return report

        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            self.stats['errors'].append(f"Report generation error: {str(e)}")
            raise

    def _get_table_statistics(self, table_name: str) -> Dict:
        """Get statistics for a specific table"""
        try:
            query = f"""
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN keyword_filter_status = 'approved' THEN 1 END) as stage_1_pass,
                    COUNT(CASE WHEN keyword_filter_status = 'rejected' THEN 1 END) as stage_1_reject,
                    COUNT(CASE WHEN truthfulness_status = 'approved' THEN 1 END) as stage_2_pass,
                    COUNT(CASE WHEN truthfulness_status = 'rejected' THEN 1 END) as stage_2_reject,
                    COUNT(CASE WHEN canadian_spelling_status = 'completed' THEN 1 END) as stage_3_complete,
                    COUNT(CASE WHEN tone_analysis_status = 'completed' THEN 1 END) as stage_4_complete,
                    COUNT(CASE WHEN skill_analysis_status = 'completed' THEN 1 END) as stage_5_complete,
                    COUNT(CASE WHEN
                        keyword_filter_status = 'approved' AND
                        truthfulness_status = 'approved' AND
                        canadian_spelling_status = 'completed' AND
                        tone_analysis_status = 'completed' AND
                        skill_analysis_status = 'completed'
                    THEN 1 END) as production_ready
                FROM {table_name}
                WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '1 day'
            """

            result = self.db.execute_query(query, ())
            if result and len(result) > 0:
                row = result[0]
                return {
                    'total_sentences': row[0],
                    'stage_1_approved': row[1],
                    'stage_1_rejected': row[2],
                    'stage_2_approved': row[3],
                    'stage_2_rejected': row[4],
                    'stage_3_completed': row[5],
                    'stage_4_completed': row[6],
                    'stage_5_completed': row[7],
                    'production_ready': row[8]
                }

            return {}

        except Exception as e:
            logger.error(f"Failed to get table statistics: {str(e)}")
            return {'error': str(e)}

    def _generate_sample_queries(self) -> Dict:
        """Generate sample SQL queries for data verification"""
        return {
            'check_recent_seeds': """
                SELECT id, content_text, status, body_section, tone
                FROM sentence_bank_resume
                WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '1 day'
                ORDER BY created_at DESC
                LIMIT 10;
            """,
            'check_production_ready': """
                SELECT COUNT(*) as production_ready_count
                FROM sentence_bank_resume
                WHERE keyword_filter_status = 'approved'
                  AND truthfulness_status = 'approved'
                  AND canadian_spelling_status = 'completed'
                  AND tone_analysis_status = 'completed'
                  AND skill_analysis_status = 'completed';
            """,
            'check_stage_distribution': """
                SELECT
                    keyword_filter_status,
                    truthfulness_status,
                    COUNT(*) as count
                FROM sentence_bank_resume
                WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '1 day'
                GROUP BY keyword_filter_status, truthfulness_status
                ORDER BY count DESC;
            """
        }


async def main():
    """Main execution function"""
    logger.info("=" * 80)
    logger.info("SIMPLIFIED SEED SENTENCE PROCESSING PIPELINE - STARTING")
    logger.info("=" * 80)

    try:
        # Initialize processor
        processor = SimplifiedSeedProcessor()

        # File paths
        seed_file = '/workspace/.trees/convert-seed-sentences-to-production-ready-content/marketing_automation_seed_sentences_new.txt'
        truths_file = '/workspace/.trees/convert-seed-sentences-to-production-ready-content/marketing_automation_atomic_truths.txt'

        # Step 1: Parse seed sentences
        logger.info("\n" + "=" * 80)
        logger.info("STEP 1: PARSING SEED SENTENCES")
        logger.info("=" * 80)
        seed_sentences = processor.parse_seed_sentences(seed_file)

        # Step 2: Load atomic truths
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: LOADING ATOMIC TRUTHS")
        logger.info("=" * 80)
        atomic_truths = processor.load_atomic_truths(truths_file)

        # Step 3: Insert seed sentences
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: INSERTING SEED SENTENCES INTO DATABASE")
        logger.info("=" * 80)
        await processor.insert_seed_sentences(seed_sentences)

        # Step 4: Process through pipeline
        logger.info("\n" + "=" * 80)
        logger.info("STEP 4: PROCESSING THROUGH 5-STAGE PIPELINE")
        logger.info("=" * 80)
        await processor.process_through_pipeline(atomic_truths)

        # Step 5: Verify and report
        logger.info("\n" + "=" * 80)
        logger.info("STEP 5: GENERATING FINAL REPORT")
        logger.info("=" * 80)
        report = await processor.verify_and_report()

        # Print final report
        logger.info("\n" + "=" * 80)
        logger.info("FINAL PROCESSING REPORT")
        logger.info("=" * 80)
        logger.info(json.dumps(report, indent=2))

        # Write report to file
        report_file = f'/workspace/.trees/convert-seed-sentences-to-production-ready-content/processing_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"\nReport saved to: {report_file}")

        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE PROCESSING COMPLETE")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"\nPIPELINE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    asyncio.run(main())
