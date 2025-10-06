"""
Secure Link Tracker

Enhanced version of LinkTracker with comprehensive security controls.
Replaces the original link_tracker.py with security-hardened implementation.

Version: 2.16.5
Date: July 28, 2025
"""

import os
import uuid
import hashlib
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from .security_controls import SecurityControls

logger = logging.getLogger(__name__)


class SecureLinkTracker:
    """
    Security-hardened link tracking system for job applications

    Features:
    - Input validation and sanitization
    - SQL injection prevention
    - Secure tracking ID generation
    - Rate limiting and abuse prevention
    - Comprehensive security logging
    """

    def __init__(self):
        """Initialize the secure link tracker with security controls."""
        self.security = SecurityControls()
        # TODO: Update base_redirect_url to production domain when deployed
        self.base_redirect_url = os.getenv("BASE_REDIRECT_URL", "http://localhost:5000/track")
        self._setup_logging()

    def _setup_logging(self):
        """Configure secure logging for link tracking operations."""
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logger.info("SecureLinkTracker initialized with security controls")

    def _get_secure_db_connection(self):
        """Get secure database connection with proper error handling."""
        try:
            conn = psycopg2.connect(
                host=os.environ.get("PGHOST"),
                database=os.environ.get("PGDATABASE"),
                user=os.environ.get("PGUSER"),
                password=os.environ.get("PGPASSWORD"),
                port=os.environ.get("PGPORT"),
                cursor_factory=RealDictCursor,
                sslmode="require",  # Enforce SSL connection
            )
            return conn
        except psycopg2.Error as e:
            logger.error("Database connection failed - generic error")
            self.security.log_security_event("DB_CONNECTION_FAILED", {"error_type": type(e).__name__}, "ERROR")
            raise Exception("Database connection failed")
        except Exception as e:
            logger.error("Database connection failed - unexpected error")
            raise Exception("Database connection failed")

    def create_tracked_link(
        self,
        original_url: str,
        link_function: str,
        job_id: Optional[str] = None,
        application_id: Optional[str] = None,
        link_type: str = "external",
        description: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a tracked link with comprehensive security validation.

        Args:
            original_url: The actual destination URL
            link_function: Function type ('LinkedIn', 'Calendly', etc.)
            job_id: Associated job UUID (optional)
            application_id: Associated application UUID (optional)
            link_type: Category of link
            description: Optional description
            client_ip: Client IP for security logging

        Returns:
            Dict containing tracking_id, redirect_url, and metadata
        """
        try:
            # Input validation
            url_valid, url_error = self.security.validate_url(original_url)
            if not url_valid:
                self.security.log_security_event(
                    "INVALID_URL_CREATION_ATTEMPT",
                    {"url": original_url[:100], "error": url_error, "ip": client_ip},
                    "WARNING",
                )
                raise ValueError(f"Invalid URL: {url_error}")

            function_valid, function_error = self.security.validate_link_function(link_function)
            if not function_valid:
                raise ValueError(f"Invalid link function: {function_error}")

            type_valid, type_error = self.security.validate_link_type(link_type)
            if not type_valid:
                raise ValueError(f"Invalid link type: {type_error}")

            if job_id:
                job_valid, job_error = self.security.validate_uuid(job_id, "job_id")
                if not job_valid:
                    raise ValueError(f"Invalid job ID: {job_error}")

            if application_id:
                app_valid, app_error = self.security.validate_uuid(application_id, "application_id")
                if not app_valid:
                    raise ValueError(f"Invalid application ID: {app_error}")

            # Sanitize inputs
            original_url = self.security.sanitize_input(original_url, 1000)
            link_function = self.security.sanitize_input(link_function, 50)
            link_type = self.security.sanitize_input(link_type, 50)
            if description:
                description = self.security.sanitize_input(description, 500)

            # Generate secure tracking ID
            tracking_id = self.security.generate_secure_tracking_id()

            # Create redirect URL
            redirect_url = f"{self.base_redirect_url}/{tracking_id}"

            # Store in database using parameterized query
            with self._get_secure_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO link_tracking (
                            tracking_id, job_id, application_id, link_function,
                            link_type, original_url, redirect_url, description,
                            created_at, created_by, is_active
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                            datetime.now(),
                            "system",
                            True,
                        ),
                    )

                    result = cursor.fetchone()
                    conn.commit()

                    logger.info(f"Created secure tracked link: {tracking_id}")

                    self.security.log_security_event(
                        "LINK_CREATED",
                        {"tracking_id": tracking_id, "link_function": link_function, "ip": client_ip},
                        "INFO",
                    )

                    return {
                        "tracking_id": result["tracking_id"],
                        "redirect_url": result["redirect_url"],
                        "original_url": original_url,
                        "link_function": link_function,
                        "link_type": link_type,
                        "job_id": job_id,
                        "application_id": application_id,
                        "created_at": result["created_at"].isoformat(),
                        "is_active": True,
                    }

        except ValueError as e:
            logger.warning(f"Validation error creating tracked link: {e}")
            raise
        except Exception as e:
            logger.error("Failed to create tracked link - generic error")
            self.security.log_security_event(
                "LINK_CREATION_FAILED", {"error_type": type(e).__name__, "ip": client_ip}, "ERROR"
            )
            raise Exception("Failed to create tracked link")

    def get_original_url(self, tracking_id: str, client_ip: Optional[str] = None) -> Optional[str]:
        """
        Get original URL for tracking ID with security validation.

        Args:
            tracking_id: The tracking identifier
            client_ip: Client IP for security logging

        Returns:
            Original URL if valid and active, None otherwise
        """
        try:
            # Validate tracking ID format
            valid, error = self.security.validate_tracking_id(tracking_id)
            if not valid:
                self.security.log_security_event(
                    "INVALID_TRACKING_ID_ACCESS",
                    {"tracking_id": tracking_id, "error": error, "ip": client_ip},
                    "WARNING",
                )
                return None

            # Sanitize tracking ID
            tracking_id = self.security.sanitize_input(tracking_id, 100)

            with self._get_secure_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Use parameterized query to prevent SQL injection
                    cursor.execute(
                        """
                        SELECT original_url, is_active, link_function
                        FROM link_tracking
                        WHERE tracking_id = %s AND is_active = true
                    """,
                        (tracking_id,),
                    )

                    result = cursor.fetchone()

                    if result:
                        self.security.log_security_event(
                            "VALID_REDIRECT_REQUEST",
                            {"tracking_id": tracking_id, "link_function": result["link_function"], "ip": client_ip},
                            "INFO",
                        )
                        return result["original_url"]
                    else:
                        self.security.log_security_event(
                            "INVALID_TRACKING_ID_REQUEST", {"tracking_id": tracking_id, "ip": client_ip}, "WARNING"
                        )
                        return None

        except Exception as e:
            logger.error("Failed to retrieve original URL - generic error")
            self.security.log_security_event(
                "URL_RETRIEVAL_FAILED", {"tracking_id": tracking_id, "ip": client_ip}, "ERROR"
            )
            return None

    def record_click(
        self,
        tracking_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer_url: Optional[str] = None,
        session_id: Optional[str] = None,
        click_source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record click event with security validation.

        Args:
            tracking_id: The tracking identifier
            ip_address: Client IP address
            user_agent: Browser user agent
            referrer_url: Referring page URL
            session_id: User session identifier
            click_source: Source category
            metadata: Additional metadata

        Returns:
            Click record information
        """
        try:
            # Validate tracking ID
            valid, error = self.security.validate_tracking_id(tracking_id)
            if not valid:
                self.security.log_security_event(
                    "INVALID_CLICK_TRACKING_ID",
                    {"tracking_id": tracking_id, "error": error, "ip": ip_address},
                    "WARNING",
                )
                raise ValueError(f"Invalid tracking ID: {error}")

            # Sanitize inputs
            tracking_id = self.security.sanitize_input(tracking_id, 100)
            if user_agent:
                user_agent = self.security.sanitize_input(user_agent, 1000)
            if referrer_url:
                referrer_url = self.security.sanitize_input(referrer_url, 1000)
            if session_id:
                session_id = self.security.sanitize_input(session_id, 100)
            if click_source:
                click_source = self.security.sanitize_input(click_source, 50)

            # Validate metadata
            if metadata and not isinstance(metadata, dict):
                metadata = {}

            # Generate click ID
            click_id = str(uuid.uuid4())

            with self._get_secure_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Use parameterized query
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
                            datetime.now(),
                            ip_address,
                            user_agent,
                            referrer_url,
                            session_id,
                            click_source,
                            psycopg2.extras.Json(metadata or {}),
                        ),
                    )

                    result = cursor.fetchone()
                    conn.commit()

                    logger.info(f"Recorded click: {click_id}")

                    self.security.log_security_event(
                        "CLICK_RECORDED",
                        {
                            "click_id": click_id,
                            "tracking_id": tracking_id,
                            "click_source": click_source,
                            "ip": ip_address,
                        },
                        "INFO",
                    )

                    return {
                        "click_id": result["click_id"],
                        "tracking_id": tracking_id,
                        "clicked_at": result["clicked_at"].isoformat(),
                        "click_source": click_source,
                        "status": "recorded",
                    }

        except ValueError as e:
            logger.warning(f"Validation error recording click: {e}")
            raise
        except Exception as e:
            logger.error("Failed to record click - generic error")
            self.security.log_security_event(
                "CLICK_RECORDING_FAILED", {"tracking_id": tracking_id, "ip": ip_address}, "ERROR"
            )
            raise Exception("Failed to record click")

    def get_link_analytics(self, tracking_id: str, client_ip: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get analytics for tracking ID with security validation.

        Args:
            tracking_id: The tracking identifier
            client_ip: Client IP for security logging

        Returns:
            Analytics data or None if invalid
        """
        try:
            # Validate tracking ID
            valid, error = self.security.validate_tracking_id(tracking_id)
            if not valid:
                self.security.log_security_event(
                    "INVALID_ANALYTICS_REQUEST",
                    {"tracking_id": tracking_id, "error": error, "ip": client_ip},
                    "WARNING",
                )
                return None

            # Sanitize tracking ID
            tracking_id = self.security.sanitize_input(tracking_id, 100)

            with self._get_secure_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get link info
                    cursor.execute(
                        """
                        SELECT tracking_id, job_id, application_id, link_function,
                               link_type, original_url, created_at, is_active, description
                        FROM link_tracking
                        WHERE tracking_id = %s
                    """,
                        (tracking_id,),
                    )

                    link_info = cursor.fetchone()

                    if not link_info:
                        return None

                    # Get click statistics
                    cursor.execute(
                        """
                        SELECT COUNT(*) as total_clicks,
                               COUNT(DISTINCT session_id) as unique_sessions,
                               MIN(clicked_at) as first_click,
                               MAX(clicked_at) as last_click,
                               COUNT(CASE WHEN clicked_at > NOW() - INTERVAL '24 hours' THEN 1 END) as clicks_24h,
                               COUNT(CASE WHEN clicked_at > NOW() - INTERVAL '7 days' THEN 1 END) as clicks_7d
                        FROM link_clicks
                        WHERE tracking_id = %s
                    """,
                        (tracking_id,),
                    )

                    click_stats = cursor.fetchone()

                    # Get recent clicks (limited for privacy)
                    cursor.execute(
                        """
                        SELECT clicked_at, click_source, 
                               CASE WHEN clicked_at > NOW() - INTERVAL '90 days' 
                                    THEN left(ip_address::text, 8) || 'xxx'
                                    ELSE 'anonymized' END as ip_partial
                        FROM link_clicks
                        WHERE tracking_id = %s
                        ORDER BY clicked_at DESC
                        LIMIT 10
                    """,
                        (tracking_id,),
                    )

                    click_timeline = cursor.fetchall()

                    self.security.log_security_event(
                        "ANALYTICS_ACCESSED", {"tracking_id": tracking_id, "ip": client_ip}, "INFO"
                    )

                    return {
                        "link_info": dict(link_info),
                        "click_statistics": dict(click_stats),
                        "click_timeline": [dict(click) for click in click_timeline],
                    }

        except Exception as e:
            logger.error("Failed to get analytics - generic error")
            self.security.log_security_event(
                "ANALYTICS_RETRIEVAL_FAILED", {"tracking_id": tracking_id, "ip": client_ip}, "ERROR"
            )
            return None

    def deactivate_link(self, tracking_id: str, client_ip: Optional[str] = None) -> bool:
        """
        Deactivate a tracking link with security validation.

        Args:
            tracking_id: The tracking identifier
            client_ip: Client IP for security logging

        Returns:
            True if successfully deactivated
        """
        try:
            # Validate tracking ID
            valid, error = self.security.validate_tracking_id(tracking_id)
            if not valid:
                return False

            # Sanitize tracking ID
            tracking_id = self.security.sanitize_input(tracking_id, 100)

            with self._get_secure_db_connection() as conn:
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
                        self.security.log_security_event(
                            "LINK_DEACTIVATED", {"tracking_id": tracking_id, "ip": client_ip}, "INFO"
                        )
                        return True

                    return False

        except Exception as e:
            logger.error("Failed to deactivate link - generic error")
            return False
