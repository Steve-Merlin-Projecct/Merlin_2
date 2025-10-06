"""
Enhanced Link Tracking System

Provides comprehensive link tracking functionality for job applications including:
- Job and application association tracking
- Link function categorization (LinkedIn, Calendly, etc.)
- Multiple click event logging
- Redirect URL management
- Analytics and reporting

Version: 2.16.5
Date: July 27, 2025
"""

import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlencode, quote
import psycopg2
from psycopg2.extras import RealDictCursor
import os

logger = logging.getLogger(__name__)


class LinkTracker:
    """
    Comprehensive link tracking system for job applications

    Tracks:
    - Job and application associations
    - Link functions (LinkedIn, Calendly, Company Website, etc.)
    - Individual click events with timestamps
    - User behavior analytics
    """

    def __init__(self):
        """Initialize the link tracker with database connection."""
        self.base_redirect_url = "https://automated-job-application-system.replit.app/track"
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for link tracking operations."""
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logger.info("LinkTracker initialized for comprehensive job application tracking")

    def _get_db_connection(self):
        """Get database connection using environment variables."""
        try:
            return psycopg2.connect(
                host=os.environ.get("PGHOST"),
                database=os.environ.get("PGDATABASE"),
                user=os.environ.get("PGUSER"),
                password=os.environ.get("PGPASSWORD"),
                port=os.environ.get("PGPORT"),
                cursor_factory=RealDictCursor,
            )
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def create_tracked_link(
        self,
        original_url: str,
        link_function: str,
        job_id: Optional[str] = None,
        application_id: Optional[str] = None,
        link_type: str = "external",
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a tracked link with job/application association.

        Args:
            original_url: The actual destination URL
            link_function: Function type ('LinkedIn', 'Calendly', 'Company_Website', 'Apply_Now', etc.)
            job_id: Associated job UUID (optional)
            application_id: Associated application UUID (optional)
            link_type: Category of link ('profile', 'job_posting', 'application', 'networking')
            description: Optional description of the link purpose

        Returns:
            Dict containing tracking_id, redirect_url, and link metadata
        """
        try:
            # Generate unique tracking ID
            tracking_id = self._generate_tracking_id(original_url, link_function)

            # Create redirect URL
            redirect_url = f"{self.base_redirect_url}/{tracking_id}"

            # Store in database
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO link_tracking (
                            tracking_id, job_id, application_id, link_function,
                            link_type, original_url, redirect_url, description
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (tracking_id) DO UPDATE SET
                            job_id = EXCLUDED.job_id,
                            application_id = EXCLUDED.application_id,
                            description = EXCLUDED.description
                        RETURNING tracking_id, redirect_url, created_at
                    """,
                        (
                            tracking_id,
                            job_id,
                            application_id,
                            link_function,
                            link_type,
                            original_url,
                            redirect_url,
                            description,
                        ),
                    )

                    result = cursor.fetchone()
                    conn.commit()

                    logger.info(f"Created tracked link: {tracking_id} for {link_function}")

                    return {
                        "tracking_id": result["tracking_id"],
                        "redirect_url": result["redirect_url"],
                        "original_url": original_url,
                        "link_function": link_function,
                        "link_type": link_type,
                        "job_id": job_id,
                        "application_id": application_id,
                        "created_at": result["created_at"],
                    }

        except Exception as e:
            logger.error(f"Failed to create tracked link: {e}")
            raise

    def record_click(
        self,
        tracking_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer_url: Optional[str] = None,
        session_id: Optional[str] = None,
        click_source: str = "direct",
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Record a click event for a tracked link.

        Args:
            tracking_id: The tracking identifier
            ip_address: Client IP address
            user_agent: Browser user agent string
            referrer_url: Referring page URL
            session_id: User session identifier
            click_source: Source of click ('email', 'dashboard', 'direct', 'api')
            metadata: Additional metadata as JSON

        Returns:
            Dict containing click_id and click metadata
        """
        try:
            click_id = str(uuid.uuid4())
            clicked_at = datetime.now()

            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO link_clicks (
                            click_id, tracking_id, clicked_at, ip_address,
                            user_agent, referrer_url, session_id, click_source, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING click_id, clicked_at
                    """,
                        (
                            click_id,
                            tracking_id,
                            clicked_at,
                            ip_address,
                            user_agent,
                            referrer_url,
                            session_id,
                            click_source,
                            metadata or {},
                        ),
                    )

                    result = cursor.fetchone()
                    conn.commit()

                    logger.info(f"Recorded click: {click_id} for tracking_id: {tracking_id}")

                    return {
                        "click_id": result["click_id"],
                        "tracking_id": tracking_id,
                        "clicked_at": result["clicked_at"],
                        "click_source": click_source,
                    }

        except Exception as e:
            logger.error(f"Failed to record click: {e}")
            raise

    def get_original_url(self, tracking_id: str) -> Optional[str]:
        """
        Get the original URL for a tracking ID.

        Args:
            tracking_id: The tracking identifier

        Returns:
            Original URL if found, None otherwise
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT original_url, is_active
                        FROM link_tracking
                        WHERE tracking_id = %s
                    """,
                        (tracking_id,),
                    )

                    result = cursor.fetchone()

                    if result and result["is_active"]:
                        return result["original_url"]
                    return None

        except Exception as e:
            logger.error(f"Failed to get original URL: {e}")
            return None

    def get_link_analytics(self, tracking_id: str) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a specific tracked link.

        Args:
            tracking_id: The tracking identifier

        Returns:
            Dict containing link analytics and click history
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get link information
                    cursor.execute(
                        """
                        SELECT lt.*, j.title as job_title, ja.status as application_status
                        FROM link_tracking lt
                        LEFT JOIN jobs j ON lt.job_id = j.id
                        LEFT JOIN job_applications ja ON lt.application_id = ja.id
                        WHERE lt.tracking_id = %s
                    """,
                        (tracking_id,),
                    )

                    link_info = cursor.fetchone()

                    if not link_info:
                        return {}

                    # Get click statistics
                    cursor.execute(
                        """
                        SELECT 
                            COUNT(*) as total_clicks,
                            COUNT(DISTINCT session_id) as unique_sessions,
                            MIN(clicked_at) as first_click,
                            MAX(clicked_at) as last_click,
                            COUNT(CASE WHEN clicked_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as clicks_24h,
                            COUNT(CASE WHEN clicked_at >= NOW() - INTERVAL '7 days' THEN 1 END) as clicks_7d
                        FROM link_clicks
                        WHERE tracking_id = %s
                    """,
                        (tracking_id,),
                    )

                    click_stats = cursor.fetchone()

                    # Get click timeline
                    cursor.execute(
                        """
                        SELECT clicked_at, click_source, ip_address
                        FROM link_clicks
                        WHERE tracking_id = %s
                        ORDER BY clicked_at DESC
                        LIMIT 50
                    """,
                        (tracking_id,),
                    )

                    click_timeline = cursor.fetchall()

                    return {
                        "link_info": dict(link_info),
                        "click_statistics": dict(click_stats),
                        "click_timeline": [dict(click) for click in click_timeline],
                    }

        except Exception as e:
            logger.error(f"Failed to get link analytics: {e}")
            return {}

    def get_job_link_summary(self, job_id: str) -> Dict[str, Any]:
        """
        Get summary of all tracked links for a specific job.

        Args:
            job_id: The job UUID

        Returns:
            Dict containing link summary by function type
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT 
                            lt.link_function,
                            lt.link_type,
                            COUNT(DISTINCT lt.tracking_id) as link_count,
                            COUNT(lc.click_id) as total_clicks,
                            COUNT(DISTINCT lc.session_id) as unique_sessions,
                            MIN(lc.clicked_at) as first_click,
                            MAX(lc.clicked_at) as last_click
                        FROM link_tracking lt
                        LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
                        WHERE lt.job_id = %s AND lt.is_active = true
                        GROUP BY lt.link_function, lt.link_type
                        ORDER BY total_clicks DESC
                    """,
                        (job_id,),
                    )

                    results = cursor.fetchall()

                    summary = {
                        "job_id": job_id,
                        "link_functions": [],
                        "total_links": 0,
                        "total_clicks": 0,
                        "unique_sessions": 0,
                    }

                    for row in results:
                        function_data = dict(row)
                        summary["link_functions"].append(function_data)
                        summary["total_links"] += function_data["link_count"]
                        summary["total_clicks"] += function_data["total_clicks"] or 0
                        summary["unique_sessions"] += function_data["unique_sessions"] or 0

                    return summary

        except Exception as e:
            logger.error(f"Failed to get job link summary: {e}")
            return {}

    def get_application_link_summary(self, application_id: str) -> Dict[str, Any]:
        """
        Get summary of all tracked links for a specific application.

        Args:
            application_id: The application UUID

        Returns:
            Dict containing application link summary
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT 
                            lt.link_function,
                            lt.tracking_id,
                            lt.original_url,
                            lt.description,
                            COUNT(lc.click_id) as click_count,
                            MIN(lc.clicked_at) as first_click,
                            MAX(lc.clicked_at) as last_click
                        FROM link_tracking lt
                        LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
                        WHERE lt.application_id = %s AND lt.is_active = true
                        GROUP BY lt.link_function, lt.tracking_id, lt.original_url, lt.description
                        ORDER BY click_count DESC
                    """,
                        (application_id,),
                    )

                    results = cursor.fetchall()

                    return {
                        "application_id": application_id,
                        "tracked_links": [dict(row) for row in results],
                        "total_tracked_links": len(results),
                        "total_clicks": sum(row["click_count"] or 0 for row in results),
                    }

        except Exception as e:
            logger.error(f"Failed to get application link summary: {e}")
            return {}

    def get_link_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive link performance report.

        Args:
            days: Number of days to include in report

        Returns:
            Dict containing performance metrics and trends
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Overall statistics
                    cursor.execute(
                        """
                        SELECT 
                            COUNT(DISTINCT lt.tracking_id) as total_links,
                            COUNT(DISTINCT lt.job_id) as jobs_with_links,
                            COUNT(DISTINCT lt.application_id) as applications_with_links,
                            COUNT(lc.click_id) as total_clicks
                        FROM link_tracking lt
                        LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
                        WHERE lt.created_at >= %s
                    """,
                        (cutoff_date,),
                    )

                    overall_stats = cursor.fetchone()

                    # Performance by function
                    cursor.execute(
                        """
                        SELECT 
                            lt.link_function,
                            COUNT(DISTINCT lt.tracking_id) as link_count,
                            COUNT(lc.click_id) as total_clicks,
                            ROUND(AVG(click_counts.clicks_per_link), 2) as avg_clicks_per_link
                        FROM link_tracking lt
                        LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
                        LEFT JOIN (
                            SELECT tracking_id, COUNT(*) as clicks_per_link
                            FROM link_clicks
                            GROUP BY tracking_id
                        ) click_counts ON lt.tracking_id = click_counts.tracking_id
                        WHERE lt.created_at >= %s
                        GROUP BY lt.link_function
                        ORDER BY total_clicks DESC
                    """,
                        (cutoff_date,),
                    )

                    function_performance = cursor.fetchall()

                    # Daily click trends
                    cursor.execute(
                        """
                        SELECT 
                            DATE(lc.clicked_at) as click_date,
                            COUNT(*) as clicks
                        FROM link_clicks lc
                        JOIN link_tracking lt ON lc.tracking_id = lt.tracking_id
                        WHERE lc.clicked_at >= %s
                        GROUP BY DATE(lc.clicked_at)
                        ORDER BY click_date
                    """,
                        (cutoff_date,),
                    )

                    daily_trends = cursor.fetchall()

                    return {
                        "report_period": {
                            "start_date": cutoff_date.isoformat(),
                            "end_date": datetime.now().isoformat(),
                            "days": days,
                        },
                        "overall_statistics": dict(overall_stats),
                        "function_performance": [dict(row) for row in function_performance],
                        "daily_trends": [dict(row) for row in daily_trends],
                    }

        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {}

    def deactivate_link(self, tracking_id: str) -> bool:
        """
        Deactivate a tracked link (stop tracking clicks).

        Args:
            tracking_id: The tracking identifier

        Returns:
            True if successfully deactivated, False otherwise
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE link_tracking
                        SET is_active = false
                        WHERE tracking_id = %s
                        RETURNING tracking_id
                    """,
                        (tracking_id,),
                    )

                    result = cursor.fetchone()
                    conn.commit()

                    if result:
                        logger.info(f"Deactivated tracking for link: {tracking_id}")
                        return True
                    return False

        except Exception as e:
            logger.error(f"Failed to deactivate link: {e}")
            return False

    def _generate_tracking_id(self, original_url: str, link_function: str) -> str:
        """
        Generate a unique tracking ID based on URL and function.

        Args:
            original_url: The original destination URL
            link_function: The link function type

        Returns:
            Unique tracking identifier
        """
        # Create a hash-based tracking ID that includes timestamp for uniqueness
        timestamp = str(int(datetime.now().timestamp()))
        content = f"{original_url}:{link_function}:{timestamp}"
        hash_obj = hashlib.sha256(content.encode())
        return f"lt_{hash_obj.hexdigest()[:16]}"

    def create_job_application_links(
        self, job_id: str, application_id: str, job_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Create standard tracked links for a job application package.

        Args:
            job_id: The job UUID
            application_id: The application UUID
            job_data: Job information containing URLs

        Returns:
            Dict mapping link functions to tracking URLs
        """
        tracked_links = {}

        # Standard link functions for job applications
        link_configs = [
            {
                "function": "LinkedIn",
                "url": "https://linkedin.com/in/steve-glen",
                "type": "profile",
                "description": "Professional LinkedIn profile",
            },
            {
                "function": "Calendly",
                "url": "https://calendly.com/steve-glen/30min",
                "type": "networking",
                "description": "Schedule interview meeting",
            },
            {
                "function": "Company_Website",
                "url": job_data.get("company_website", ""),
                "type": "job_posting",
                "description": "Company website research",
            },
            {
                "function": "Apply_Now",
                "url": job_data.get("apply_url", ""),
                "type": "application",
                "description": "Direct application link",
            },
            {
                "function": "Job_Posting",
                "url": job_data.get("job_url", ""),
                "type": "job_posting",
                "description": "Original job posting",
            },
        ]

        for config in link_configs:
            if config["url"]:  # Only create links if URL exists
                try:
                    result = self.create_tracked_link(
                        original_url=config["url"],
                        link_function=config["function"],
                        job_id=job_id,
                        application_id=application_id,
                        link_type=config["type"],
                        description=config["description"],
                    )
                    tracked_links[config["function"]] = result["redirect_url"]

                except Exception as e:
                    logger.error(f"Failed to create {config['function']} link: {e}")

        logger.info(f"Created {len(tracked_links)} tracked links for application {application_id}")
        return tracked_links
