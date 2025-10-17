"""
Database Extensions for Scraper API
Additional methods needed by the scraper API that aren't in the main database classes
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ScraperDatabaseExtensions:
    """
    Extensions to database functionality specifically for scraper operations
    """

    def __init__(self):
        self.db_manager = DatabaseManager()

    def get_scrape_status(self, scrape_id: str) -> Optional[Dict]:
        """
        Get status of a scraping operation

        Args:
            scrape_id: Scraping run ID

        Returns:
            Scrape status information or None if not found
        """
        try:
            with self.db_manager.get_session() as session:
                query = """
                    SELECT 
                        scraper_run_id,
                        COUNT(*) as jobs_count,
                        MIN(created_at) as started_at,
                        MAX(created_at) as last_updated,
                        source_website,
                        scraper_used
                    FROM raw_job_scrapes 
                    WHERE scraper_run_id = %s
                    GROUP BY scraper_run_id, source_website, scraper_used
                """

                result = session.execute(query, (scrape_id,)).fetchone()

                if result:
                    return {
                        "scrape_id": result[0],
                        "jobs_count": result[1],
                        "started_at": result[2].isoformat() if result[2] else None,
                        "last_updated": result[3].isoformat() if result[3] else None,
                        "source_website": result[4],
                        "scraper_used": result[5],
                        "status": "completed",
                    }

                return None

        except Exception as e:
            logger.error(f"Error getting scrape status: {e}")
            return None

    def get_scrape_results(self, scrape_id: str, limit: int = 100) -> Optional[Dict]:
        """
        Get results from a completed scraping operation

        Args:
            scrape_id: Scraping run ID
            limit: Maximum number of results to return

        Returns:
            Scrape results or None if not found
        """
        try:
            with self.db_manager.get_session() as session:
                # Get summary information
                summary_query = """
                    SELECT 
                        COUNT(*) as total_jobs,
                        source_website,
                        scraper_used,
                        MIN(created_at) as started_at,
                        MAX(created_at) as completed_at
                    FROM raw_job_scrapes 
                    WHERE scraper_run_id = %s
                    GROUP BY source_website, scraper_used
                """

                summary_result = session.execute(summary_query, (scrape_id,)).fetchone()

                if not summary_result:
                    return None

                # Get sample job data
                jobs_query = """
                    SELECT 
                        id,
                        source_url,
                        raw_data,
                        created_at
                    FROM raw_job_scrapes 
                    WHERE scraper_run_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """

                jobs_results = session.execute(jobs_query, (scrape_id, limit)).fetchall()

                jobs_data = []
                for job in jobs_results:
                    job_info = {
                        "id": job[0],
                        "source_url": job[1],
                        "created_at": job[3].isoformat() if job[3] else None,
                    }

                    # Extract basic info from raw_data if it's JSON
                    try:
                        import json

                        raw_data = json.loads(job[2]) if isinstance(job[2], str) else job[2]
                        job_info.update(
                            {
                                "title": raw_data.get("positionName", raw_data.get("title", "Unknown")),
                                "company": raw_data.get("company", "Unknown"),
                                "location": raw_data.get("location", "Unknown"),
                            }
                        )
                    except (json.JSONDecodeError, TypeError):
                        job_info.update({"title": "Unknown", "company": "Unknown", "location": "Unknown"})

                    jobs_data.append(job_info)

                return {
                    "scrape_id": scrape_id,
                    "summary": {
                        "total_jobs": summary_result[0],
                        "source_website": summary_result[1],
                        "scraper_used": summary_result[2],
                        "started_at": summary_result[3].isoformat() if summary_result[3] else None,
                        "completed_at": summary_result[4].isoformat() if summary_result[4] else None,
                    },
                    "jobs": jobs_data,
                    "showing": f"{len(jobs_data)} of {summary_result[0]} jobs",
                }

        except Exception as e:
            logger.error(f"Error getting scrape results: {e}")
            return None

    def get_recent_scrape_activity(self, days: int = 7) -> Dict:
        """
        Get recent scraping activity statistics

        Args:
            days: Number of days to look back

        Returns:
            Recent activity statistics
        """
        try:
            with self.db_manager.get_session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)

                # Daily activity summary
                daily_query = """
                    SELECT 
                        DATE(created_at) as scrape_date,
                        COUNT(*) as jobs_scraped,
                        COUNT(DISTINCT scraper_run_id) as scrape_runs
                    FROM raw_job_scrapes 
                    WHERE created_at >= %s
                    GROUP BY DATE(created_at)
                    ORDER BY scrape_date DESC
                """

                daily_results = session.execute(daily_query, (cutoff_date,)).fetchall()

                # Overall statistics
                total_query = """
                    SELECT 
                        COUNT(*) as total_jobs,
                        COUNT(DISTINCT scraper_run_id) as total_runs,
                        COUNT(DISTINCT source_website) as websites_scraped
                    FROM raw_job_scrapes 
                    WHERE created_at >= %s
                """

                total_result = session.execute(total_query, (cutoff_date,)).fetchone()

                daily_activity = []
                for row in daily_results:
                    daily_activity.append(
                        {"date": row[0].isoformat() if row[0] else None, "jobs_scraped": row[1], "scrape_runs": row[2]}
                    )

                return {
                    "period_days": days,
                    "total_jobs": total_result[0] if total_result else 0,
                    "total_runs": total_result[1] if total_result else 0,
                    "websites_scraped": total_result[2] if total_result else 0,
                    "daily_activity": daily_activity,
                }

        except Exception as e:
            logger.error(f"Error getting recent scrape activity: {e}")
            return {
                "period_days": days,
                "total_jobs": 0,
                "total_runs": 0,
                "websites_scraped": 0,
                "daily_activity": [],
                "error": str(e),
            }

    def get_table_count(self, table_name: str) -> int:
        """
        Get count of records in a table

        Args:
            table_name: Name of the table

        Returns:
            Number of records
        """
        try:
            with self.db_manager.get_session() as session:
                # Use parameterized query safely for table names we control
                allowed_tables = ["raw_job_scrapes", "cleaned_job_scrapes", "jobs"]
                if table_name not in allowed_tables:
                    raise ValueError(f"Table {table_name} not allowed")

                query = f"SELECT COUNT(*) FROM {table_name}"
                result = session.execute(query).fetchone()
                return result[0] if result else 0

        except Exception as e:
            logger.error(f"Error getting table count for {table_name}: {e}")
            return 0


# Add methods to DatabaseReader for backward compatibility
def extend_database_reader():
    """
    Extend the DatabaseReader class with scraper-specific methods.

    IMPORTANT: This function should NOT be called at module import time.
    It must be called within the Flask application context after app initialization.

    This prevents database connections from being established during import,
    which would cause app startup failures.

    Usage:
        # In app_modular.py, after app creation:
        with app.app_context():
            from modules.database.database_extensions import extend_database_reader
            extend_database_reader()
    """
    from modules.database.database_reader import DatabaseReader

    extensions = ScraperDatabaseExtensions()

    # Add methods to DatabaseReader
    DatabaseReader.get_scrape_status = lambda self, scrape_id: extensions.get_scrape_status(scrape_id)
    DatabaseReader.get_scrape_results = lambda self, scrape_id, limit=100: extensions.get_scrape_results(
        scrape_id, limit
    )
    DatabaseReader.get_recent_scrape_activity = lambda self, days=7: extensions.get_recent_scrape_activity(days)
    DatabaseReader.get_table_count = lambda self, table_name: extensions.get_table_count(table_name)

    logger.info("DatabaseReader extensions registered successfully")


# NOTE: Module-level call REMOVED for lazy initialization!
# The extend_database_reader() function must now be called explicitly
# from app_modular.py within the Flask application context.
