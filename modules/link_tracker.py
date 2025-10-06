"""
Link Tracking System
Generates unique tracking links and handles click tracking
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Optional
from .database.database_client import DatabaseClient


class LinkTracker:
    """
    Handles creation and tracking of unique links for job applications
    """

    def __init__(self):
        self.db_client = DatabaseClient()
        self.base_url = "http://localhost:5000"  # Will be updated for production

    def generate_tracked_links(self, job_id: str, application_id: str) -> Dict[str, str]:
        """
        Generate tracked links for all application components
        """
        links = {
            "linkedin": "https://linkedin.com/in/steveglen",
            "portfolio": "https://steveglen.com",
            "calendar": "https://calendly.com/steveglen/30min",
            "email": "mailto:therealstevenglen@gmail.com",
        }

        tracked_links = {}

        with self.db_client.get_session() as session:
            for link_type, original_url in links.items():
                # Generate unique tracking ID
                tracking_id = str(uuid.uuid4())[:8]  # Short ID for cleaner URLs

                # Store tracking record
                session.execute(
                    """
                    INSERT INTO link_tracking (
                        tracking_id, job_id, application_id, link_type, original_url
                    ) VALUES (%s, %s, %s, %s, %s)
                """,
                    (tracking_id, job_id, application_id, link_type, original_url),
                )

                # Create tracked URL
                tracked_url = f"{self.base_url}/track/{tracking_id}"
                tracked_links[link_type] = tracked_url

        logging.info(f"Generated {len(tracked_links)} tracked links for application {application_id}")
        return tracked_links

    def record_click(self, tracking_id: str, ip_address: str = None, user_agent: str = None) -> Optional[str]:
        """
        Record click and return original URL for redirect
        """
        with self.db_client.get_session() as session:
            # Get tracking record
            result = session.execute(
                """
                SELECT original_url, click_count FROM link_tracking 
                WHERE tracking_id = %s
            """,
                (tracking_id,),
            ).fetchone()

            if not result:
                return None

            original_url, current_count = result

            # Update click count and timestamps
            session.execute(
                """
                UPDATE link_tracking SET 
                    click_count = %s,
                    last_clicked_at = %s,
                    first_clicked_at = COALESCE(first_clicked_at, %s)
                WHERE tracking_id = %s
            """,
                (current_count + 1, datetime.utcnow(), datetime.utcnow(), tracking_id),
            )

        logging.info(f"Recorded click for tracking ID {tracking_id}")
        return original_url

    def get_tracking_stats(self, application_id: str) -> Dict:
        """
        Get click statistics for an application
        """
        with self.db_client.get_session() as session:
            result = session.execute(
                """
                SELECT link_type, click_count, first_clicked_at, last_clicked_at
                FROM link_tracking 
                WHERE application_id = %s
            """,
                (application_id,),
            ).fetchall()

            stats = {}
            total_clicks = 0

            for row in result:
                link_type, clicks, first_click, last_click = row
                stats[link_type] = {"clicks": clicks, "first_clicked": first_click, "last_clicked": last_click}
                total_clicks += clicks

            stats["total_clicks"] = total_clicks
            return stats
