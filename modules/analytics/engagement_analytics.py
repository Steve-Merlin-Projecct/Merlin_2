"""
Engagement Analytics Engine

Core analytics logic for link tracking insights including:
- Engagement summary across applications
- Engagement-to-outcome correlation analysis
- Link function effectiveness ranking
- Individual application engagement details

Version: 1.0.0
Date: October 9, 2025
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class EngagementAnalytics:
    """
    Core analytics engine for extracting insights from link tracking data

    Provides methods to:
    - Calculate engagement metrics across applications
    - Correlate engagement with outcomes (interviews, offers)
    - Rank link types by effectiveness
    - Analyze individual application engagement patterns
    """

    def __init__(self):
        """Initialize analytics engine with database connection"""
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for analytics operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.info("Engagement Analytics Engine initialized")

    def _get_db_connection(self):
        """Get database connection using environment variables"""
        try:
            return psycopg2.connect(
                host=os.environ.get("PGHOST", "localhost"),
                database=os.environ.get("PGDATABASE", "local_Merlin_3"),
                user=os.environ.get("PGUSER", "postgres"),
                password=os.environ.get("PGPASSWORD"),
                port=os.environ.get("PGPORT", "5432"),
                cursor_factory=RealDictCursor,
            )
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def get_engagement_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get overall engagement metrics across all applications

        Args:
            start_date: Filter applications from date (ISO format)
            end_date: Filter applications to date (ISO format)
            status: Filter by application status

        Returns:
            Dictionary containing engagement summary and outcome breakdown
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Build WHERE clause
                    where_conditions = []
                    params = []

                    if start_date:
                        where_conditions.append("ja.created_at >= %s")
                        params.append(start_date)

                    if end_date:
                        where_conditions.append("ja.created_at <= %s")
                        params.append(end_date)

                    if status:
                        where_conditions.append("ja.status = %s")
                        params.append(status)

                    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

                    # Overall summary query
                    cursor.execute(f"""
                        SELECT
                            COUNT(*) as total_applications,
                            COUNT(CASE WHEN total_clicks > 0 THEN 1 END) as applications_with_clicks,
                            ROUND(100.0 * COUNT(CASE WHEN total_clicks > 0 THEN 1 END) /
                                NULLIF(COUNT(*), 0), 1) as engagement_rate,
                            ROUND(AVG(NULLIF(total_clicks, 0)), 2) as avg_clicks_per_application,
                            ROUND(AVG(NULLIF(EXTRACT(EPOCH FROM (first_click_timestamp - created_at))/3600, 0)), 1)
                                as avg_hours_to_first_click
                        FROM job_applications ja
                        {where_clause}
                    """, params)

                    summary = dict(cursor.fetchone())

                    # Outcome breakdown by engagement level
                    outcomes = self._get_outcomes_by_engagement(cursor, where_clause, params)

                    return {
                        "summary": summary,
                        "outcomes": outcomes,
                        "time_period": {
                            "start_date": start_date or "all_time",
                            "end_date": end_date or datetime.now().isoformat()
                        }
                    }

        except Exception as e:
            logger.error(f"Failed to get engagement summary: {e}")
            raise

    def _get_outcomes_by_engagement(
        self,
        cursor,
        where_clause: str,
        params: List
    ) -> Dict[str, Any]:
        """
        Break down outcomes by engagement level

        Returns:
            Dictionary with no_engagement, low_engagement, high_engagement stats
        """
        cursor.execute(f"""
            WITH engagement_levels AS (
                SELECT
                    id,
                    status,
                    CASE
                        WHEN total_clicks = 0 THEN 'no_engagement'
                        WHEN total_clicks < 3 THEN 'low_engagement'
                        ELSE 'high_engagement'
                    END as engagement_level
                FROM job_applications
                {where_clause}
            )
            SELECT
                engagement_level,
                COUNT(*) as count,
                ROUND(100.0 * COUNT(CASE WHEN status = 'interview' THEN 1 END) /
                    NULLIF(COUNT(*), 0), 1) as interview_rate,
                ROUND(100.0 * COUNT(CASE WHEN status = 'offer' THEN 1 END) /
                    NULLIF(COUNT(*), 0), 1) as offer_rate
            FROM engagement_levels
            GROUP BY engagement_level
        """, params)

        results = cursor.fetchall()

        # Format as dict
        outcomes = {}
        for row in results:
            outcomes[row['engagement_level']] = {
                'count': row['count'],
                'interview_rate': float(row['interview_rate'] or 0),
                'offer_rate': float(row['offer_rate'] or 0)
            }

        # Ensure all levels are present
        for level in ['no_engagement', 'low_engagement', 'high_engagement']:
            if level not in outcomes:
                outcomes[level] = {'count': 0, 'interview_rate': 0.0, 'offer_rate': 0.0}

        return outcomes

    def get_engagement_to_outcome_correlation(self) -> Dict[str, Any]:
        """
        Analyze correlation between engagement metrics and application outcomes

        Returns:
            Dictionary with correlation statistics and insights
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get correlation data from the view
                    cursor.execute("""
                        SELECT
                            status,
                            COUNT(*) as applications,
                            ROUND(AVG(total_clicks), 2) as avg_clicks,
                            ROUND(AVG(unique_sessions), 2) as avg_sessions,
                            ROUND(AVG(NULLIF(hours_to_first_click, NULL)), 1) as avg_hours_to_click
                        FROM application_engagement_outcomes
                        GROUP BY status
                        ORDER BY
                            CASE status
                                WHEN 'offer' THEN 1
                                WHEN 'interview' THEN 2
                                WHEN 'applied' THEN 3
                                WHEN 'rejected' THEN 4
                                ELSE 5
                            END
                    """)

                    correlations = [dict(row) for row in cursor.fetchall()]

                    # Generate insights
                    insights = self._generate_correlation_insights(correlations)

                    return {
                        "correlations": correlations,
                        "insights": insights
                    }

        except Exception as e:
            logger.error(f"Failed to get correlation data: {e}")
            raise

    def _generate_correlation_insights(self, correlations: List[Dict]) -> List[str]:
        """Generate human-readable insights from correlation data"""
        insights = []

        # Find status with highest engagement
        if correlations:
            highest_engagement = max(
                correlations,
                key=lambda x: float(x.get('avg_clicks') or 0)
            )

            if highest_engagement.get('avg_clicks', 0) > 0:
                insights.append(
                    f"Applications with '{highest_engagement['status']}' status "
                    f"have the highest average engagement ({highest_engagement['avg_clicks']} clicks)"
                )

        # Compare interview vs rejected
        interview_data = next((c for c in correlations if c['status'] == 'interview'), None)
        rejected_data = next((c for c in correlations if c['status'] == 'rejected'), None)

        if interview_data and rejected_data:
            interview_clicks = float(interview_data.get('avg_clicks') or 0)
            rejected_clicks = float(rejected_data.get('avg_clicks') or 0)

            if interview_clicks > rejected_clicks * 1.5:
                insights.append(
                    f"Interview applications show {interview_clicks/rejected_clicks:.1f}x "
                    f"higher engagement than rejections"
                )

        return insights

    def get_link_function_effectiveness(self) -> Dict[str, Any]:
        """
        Rank link types by their effectiveness (conversion to interviews/offers)

        Returns:
            Dictionary with ranked link functions and effectiveness metrics
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Query the effectiveness view
                    cursor.execute("""
                        SELECT
                            link_function,
                            applications_with_link,
                            total_clicks,
                            avg_clicks_per_application,
                            interviews_generated,
                            offers_generated,
                            interview_conversion_rate
                        FROM link_function_effectiveness
                        WHERE link_function IS NOT NULL
                        ORDER BY interview_conversion_rate DESC NULLS LAST
                        LIMIT 10
                    """)

                    link_functions = [dict(row) for row in cursor.fetchall()]

                    # Add effectiveness rank
                    for idx, link in enumerate(link_functions, 1):
                        link['effectiveness_rank'] = idx

                    # Generate recommendations
                    recommendations = self._generate_link_recommendations(link_functions)

                    return {
                        "link_functions": link_functions,
                        "insights": recommendations
                    }

        except Exception as e:
            logger.error(f"Failed to get link effectiveness: {e}")
            raise

    def _generate_link_recommendations(self, link_functions: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on link performance"""
        recommendations = []

        if not link_functions:
            return ["Insufficient data for recommendations"]

        # Highest performing link
        top_link = link_functions[0]
        if float(top_link.get('interview_conversion_rate') or 0) > 0:
            recommendations.append(
                f"{top_link['link_function']} links show highest conversion "
                f"({top_link['interview_conversion_rate']}%) - ensure prominent placement"
            )

        # Check for Calendly specifically
        calendly = next((lf for lf in link_functions if 'Calendly' in lf.get('link_function', '')), None)
        if calendly and float(calendly.get('interview_conversion_rate') or 0) > 15:
            recommendations.append(
                "Calendly clicks indicate high intent - consider auto-triggering follow-up emails"
            )

        # Check for LinkedIn
        linkedin = next((lf for lf in link_functions if 'LinkedIn' in lf.get('link_function', '')), None)
        if linkedin and float(linkedin.get('avg_clicks_per_application') or 0) > 1.5:
            recommendations.append(
                "LinkedIn profile receives multiple views - indicates candidate research phase"
            )

        return recommendations

    def get_application_engagement_details(self, application_id: str) -> Dict[str, Any]:
        """
        Get detailed engagement data for a specific application

        Args:
            application_id: UUID of the application

        Returns:
            Dictionary with detailed engagement metrics and click timeline
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get application engagement data
                    cursor.execute("""
                        SELECT
                            application_id,
                            status,
                            application_date,
                            total_clicks,
                            unique_sessions,
                            first_click_timestamp,
                            last_click_timestamp,
                            hours_to_first_click,
                            clicked_functions,
                            most_clicked_function
                        FROM application_engagement_outcomes
                        WHERE application_id = %s
                    """, (application_id,))

                    engagement_data = cursor.fetchone()

                    if not engagement_data:
                        return {"error": "Application not found"}

                    # Get click timeline
                    cursor.execute("""
                        SELECT
                            lc.clicked_at,
                            lc.click_source,
                            lt.link_function,
                            lt.description
                        FROM link_clicks lc
                        JOIN link_tracking lt ON lc.tracking_id = lt.tracking_id
                        WHERE lt.application_id = %s
                        ORDER BY lc.clicked_at ASC
                    """, (application_id,))

                    click_timeline = [dict(row) for row in cursor.fetchall()]

                    return {
                        "engagement_summary": dict(engagement_data),
                        "click_timeline": click_timeline,
                        "total_click_events": len(click_timeline)
                    }

        except Exception as e:
            logger.error(f"Failed to get application engagement details: {e}")
            raise
