#!/usr/bin/env python3
"""
Execute pipeline processing starting from Stage 2 (Truthfulness)

This script continues processing sentences that have already passed Stage 1 (Keyword Filter)
and need to complete Stages 2-5.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv('/workspace/.env')

# Override DATABASE_URL to use host.docker.internal (for Docker containers)
os.environ['DATABASE_URL'] = 'postgresql://postgres:goldmember@host.docker.internal:5432/local_Merlin_3'

sys.path.append('/workspace')

from modules.content.copywriting_evaluator.pipeline_processor import (
    CopywritingEvaluatorPipeline,
    PipelineConfig,
    ProcessingMode,
    ProcessingStage
)
from modules.database.database_manager import DatabaseManager

def load_atomic_truths():
    """Load atomic truths from file"""
    truths_file = '/workspace/.trees/convert-seed-sentences-to-production-ready-content/marketing_automation_atomic_truths.txt'

    if not os.path.exists(truths_file):
        print(f"WARNING: Atomic truths file not found at {truths_file}")
        return []

    with open(truths_file, 'r') as f:
        content = f.read()

    # Extract truth statements (lines starting with [)
    truths = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('['):
            truths.append(line)

    print(f"Loaded {len(truths)} atomic truths from file")
    return truths

def get_sentence_counts(db):
    """Get current sentence counts by status"""

    resume_query = """
    SELECT
        COUNT(*) as total,
        keyword_filter_status,
        truthfulness_status,
        canadian_spelling_status,
        tone_analysis_status,
        skill_analysis_status
    FROM sentence_bank_resume
    GROUP BY
        keyword_filter_status,
        truthfulness_status,
        canadian_spelling_status,
        tone_analysis_status,
        skill_analysis_status
    """

    cover_query = """
    SELECT
        COUNT(*) as total,
        keyword_filter_status,
        truthfulness_status,
        canadian_spelling_status,
        tone_analysis_status,
        skill_analysis_status
    FROM sentence_bank_cover_letter
    GROUP BY
        keyword_filter_status,
        truthfulness_status,
        canadian_spelling_status,
        tone_analysis_status,
        skill_analysis_status
    """

    resume_results = db.execute_query(resume_query, ())
    cover_results = db.execute_query(cover_query, ())

    return {
        'resume': resume_results,
        'cover_letter': cover_results
    }

async def main():
    """Main execution function"""

    print("="*80)
    print("SENTENCE PROCESSING PIPELINE - CONTINUE FROM TRUTHFULNESS (STAGE 2)")
    print("="*80)
    print()

    execution_report = {
        'start_time': datetime.now().isoformat(),
        'initial_state': {},
        'resume_processing': {},
        'cover_letter_processing': {},
        'atomic_truths': {},
        'final_database_state': {},
        'errors': []
    }

    try:
        db = DatabaseManager()

        # ========================================================================
        # STEP 1: CHECK INITIAL STATE
        # ========================================================================
        print("\n" + "="*80)
        print("STEP 1: CHECK INITIAL DATABASE STATE")
        print("="*80)

        # Check initial state
        initial_counts = get_sentence_counts(db)

        print("\nInitial sentence counts:")
        print("\nRESUME:")
        for row in initial_counts['resume']:
            print(f"  {row}")

        print("\nCOVER LETTER:")
        for row in initial_counts['cover_letter']:
            print(f"  {row}")

        # Count sentences ready for truthfulness processing
        truthfulness_resume_count = sum(r['total'] for r in initial_counts['resume'] if r['keyword_filter_status'] == 'approved' and r['truthfulness_status'] == 'pending')
        truthfulness_cover_count = sum(r['total'] for r in initial_counts['cover_letter'] if r['keyword_filter_status'] == 'approved' and r['truthfulness_status'] == 'pending')

        execution_report['initial_state'] = {
            'resume_ready_for_truthfulness': truthfulness_resume_count,
            'cover_letter_ready_for_truthfulness': truthfulness_cover_count,
            'total_ready': truthfulness_resume_count + truthfulness_cover_count
        }

        print(f"\n✓ Found {truthfulness_resume_count + truthfulness_cover_count} sentences ready for truthfulness processing")
        print(f"  Resume: {truthfulness_resume_count}")
        print(f"  Cover letter: {truthfulness_cover_count}")

        # ========================================================================
        # STEP 2: LOAD ATOMIC TRUTHS
        # ========================================================================
        print("\n" + "="*80)
        print("STEP 2: LOAD ATOMIC TRUTHS")
        print("="*80)

        atomic_truths = load_atomic_truths()

        execution_report['atomic_truths'] = {
            'truths_loaded': len(atomic_truths),
            'sample_verification': atomic_truths[:5] if atomic_truths else [],
            'truths_file_path': '/workspace/.trees/convert-seed-sentences-to-production-ready-content/marketing_automation_atomic_truths.txt'
        }

        print(f"\n✓ Loaded {len(atomic_truths)} atomic truths")
        print("\nSample atomic truths:")
        for truth in atomic_truths[:5]:
            print(f"  - {truth}")

        # ========================================================================
        # STEP 3: PROCESS RESUME SENTENCES (FROM TRUTHFULNESS STAGE)
        # ========================================================================
        print("\n" + "="*80)
        print("STEP 3: PROCESS RESUME SENTENCES (STAGES 2-5)")
        print("="*80)

        # Initialize pipeline in TESTING mode for autonomous processing
        config = PipelineConfig(
            mode=ProcessingMode.TESTING,
            batch_size=5,
            immediate_processing=True
        )
        pipeline = CopywritingEvaluatorPipeline(config)

        print("\nProcessing resume sentences from Truthfulness stage...")
        print("Stages: Truthfulness -> Canadian Spelling -> Tone -> Skill")

        try:
            resume_stats = await pipeline.process_sentences(
                table_name='sentence_bank_resume',
                sentence_ids=None,  # Process all pending
                restart_from_stage=ProcessingStage.TRUTHFULNESS  # Start from stage 2
            )

            # Get final counts
            resume_final = get_sentence_counts(db)

            # Count production ready (all stages completed)
            production_ready_query = """
            SELECT COUNT(*) as production_ready
            FROM sentence_bank_resume
            WHERE keyword_filter_status = 'approved'
              AND truthfulness_status = 'approved'
              AND canadian_spelling_status = 'completed'
              AND tone_analysis_status = 'completed'
              AND skill_analysis_status = 'completed'
            """
            production_ready_result = db.execute_query(production_ready_query, ())
            production_ready_count = production_ready_result[0]['production_ready'] if production_ready_result else 0

            execution_report['resume_processing'] = {
                'total_sentences': resume_stats.total_sentences,
                'processed_sentences': resume_stats.processed_sentences,
                'filtered_sentences': resume_stats.filtered_sentences,
                'production_ready': production_ready_count,
                'stage_stats': resume_stats.stage_stats,
                'errors': [],
                'duration_seconds': (resume_stats.end_time - resume_stats.start_time).total_seconds() if resume_stats.end_time and resume_stats.start_time else 0
            }

            print(f"\n✓ Resume processing complete:")
            print(f"  Total: {resume_stats.total_sentences}")
            print(f"  Processed: {resume_stats.processed_sentences}")
            print(f"  Filtered: {resume_stats.filtered_sentences}")
            print(f"  Production ready: {production_ready_count}")

        except Exception as e:
            error_msg = f"Resume processing error: {str(e)}"
            print(f"\n✗ {error_msg}")
            execution_report['resume_processing']['errors'] = [error_msg]
            execution_report['errors'].append(error_msg)
            import traceback
            traceback.print_exc()

        # ========================================================================
        # STEP 4: PROCESS COVER LETTER SENTENCES (FROM TRUTHFULNESS STAGE)
        # ========================================================================
        print("\n" + "="*80)
        print("STEP 4: PROCESS COVER LETTER SENTENCES (STAGES 2-5)")
        print("="*80)

        print("\nProcessing cover letter sentences from Truthfulness stage...")

        try:
            cover_stats = await pipeline.process_sentences(
                table_name='sentence_bank_cover_letter',
                sentence_ids=None,
                restart_from_stage=ProcessingStage.TRUTHFULNESS  # Start from stage 2
            )

            # Get final counts
            cover_final = get_sentence_counts(db)

            # Count production ready
            production_ready_query = """
            SELECT COUNT(*) as production_ready
            FROM sentence_bank_cover_letter
            WHERE keyword_filter_status = 'approved'
              AND truthfulness_status = 'approved'
              AND canadian_spelling_status = 'completed'
              AND tone_analysis_status = 'completed'
              AND skill_analysis_status = 'completed'
            """
            production_ready_result = db.execute_query(production_ready_query, ())
            production_ready_count = production_ready_result[0]['production_ready'] if production_ready_result else 0

            execution_report['cover_letter_processing'] = {
                'total_sentences': cover_stats.total_sentences,
                'processed_sentences': cover_stats.processed_sentences,
                'filtered_sentences': cover_stats.filtered_sentences,
                'production_ready': production_ready_count,
                'stage_stats': cover_stats.stage_stats,
                'errors': [],
                'duration_seconds': (cover_stats.end_time - cover_stats.start_time).total_seconds() if cover_stats.end_time and cover_stats.start_time else 0
            }

            print(f"\n✓ Cover letter processing complete:")
            print(f"  Total: {cover_stats.total_sentences}")
            print(f"  Processed: {cover_stats.processed_sentences}")
            print(f"  Filtered: {cover_stats.filtered_sentences}")
            print(f"  Production ready: {production_ready_count}")

        except Exception as e:
            error_msg = f"Cover letter processing error: {str(e)}"
            print(f"\n✗ {error_msg}")
            execution_report['cover_letter_processing']['errors'] = [error_msg]
            execution_report['errors'].append(error_msg)
            import traceback
            traceback.print_exc()

        # ========================================================================
        # FINAL DATABASE STATE
        # ========================================================================
        print("\n" + "="*80)
        print("FINAL DATABASE STATE")
        print("="*80)

        # Get final production-ready counts
        final_resume_query = "SELECT COUNT(*) FROM sentence_bank_resume WHERE keyword_filter_status = 'approved' AND truthfulness_status = 'approved' AND canadian_spelling_status = 'completed' AND tone_analysis_status = 'completed' AND skill_analysis_status = 'completed'"
        final_cover_query = "SELECT COUNT(*) FROM sentence_bank_cover_letter WHERE keyword_filter_status = 'approved' AND truthfulness_status = 'approved' AND canadian_spelling_status = 'completed' AND tone_analysis_status = 'completed' AND skill_analysis_status = 'completed'"

        final_resume_count = db.execute_query(final_resume_query, ())[0]['count']
        final_cover_count = db.execute_query(final_cover_query, ())[0]['count']

        execution_report['final_database_state'] = {
            'production_ready_resume': final_resume_count,
            'production_ready_cover_letter': final_cover_count,
            'production_ready_total': final_resume_count + final_cover_count
        }

        print(f"\nProduction-ready sentences:")
        print(f"  Resume: {final_resume_count}")
        print(f"  Cover letter: {final_cover_count}")
        print(f"  TOTAL: {final_resume_count + final_cover_count}")

    except Exception as e:
        error_msg = f"Pipeline execution error: {str(e)}"
        print(f"\n✗ CRITICAL ERROR: {error_msg}")
        execution_report['errors'].append(error_msg)
        import traceback
        traceback.print_exc()

    finally:
        execution_report['end_time'] = datetime.now().isoformat()

        # Save report
        report_file = '/workspace/.trees/convert-seed-sentences-to-production-ready-content/pipeline_final.log'
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("PIPELINE EXECUTION - STARTING FROM TRUTHFULNESS (STAGE 2)\n")
            f.write("="*80 + "\n\n")
            f.write(json.dumps(execution_report, indent=2, default=str))

        print(f"\n" + "="*80)
        print("EXECUTION COMPLETE")
        print("="*80)
        print(f"\nReport saved to: {report_file}")

        return execution_report

if __name__ == '__main__':
    report = asyncio.run(main())

    # Print summary
    print("\n" + "="*80)
    print("EXECUTION SUMMARY")
    print("="*80)
    print(f"Total sentences processed: {report.get('initial_state', {}).get('total_ready', 0)}")
    print(f"Production ready: {report.get('final_database_state', {}).get('production_ready_total', 0)}")
    print(f"Errors: {len(report.get('errors', []))}")
