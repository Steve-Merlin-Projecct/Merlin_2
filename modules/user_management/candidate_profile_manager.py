"""
Candidate Profile Manager

Centralized module for retrieving candidate personal information including
contact details, professional URLs (Calendly, LinkedIn, Portfolio), and
work experience data.

This manager provides a clean interface for document generation systems
to access candidate data stored in the database without directly coupling
to database implementation details.

Version: 1.0.0
Date: October 9, 2025
"""

import os
import logging
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class CandidateProfileManager:
    """
    Manages candidate personal information and professional URLs

    This class provides methods to retrieve candidate data from the database
    for use in document generation, email templates, and other systems that
    require candidate information.

    Key Features:
    - Retrieve complete candidate profile information
    - Access individual candidate URLs (Calendly, LinkedIn, Portfolio)
    - Update candidate information
    - Handle missing data gracefully with sensible defaults
    """

    def __init__(self):
        """Initialize the CandidateProfileManager with database connection settings"""
        self.setup_logging()
        logger.info("CandidateProfileManager initialized")

    def setup_logging(self):
        """Configure logging for candidate profile operations"""
        logging.basicConfig(level=logging.INFO)

    def _get_db_connection(self):
        """
        Get database connection using environment variables

        Returns:
            psycopg2.connection: Database connection with RealDictCursor

        Raises:
            Exception: If database connection fails
        """
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

    def get_candidate_info(self, user_id: str = "steve_glen") -> Dict[str, Any]:
        """
        Retrieve all candidate information for document generation

        This method fetches comprehensive candidate data including personal
        information, contact details, and professional URLs from the database.

        Args:
            user_id (str): User identifier (default: 'steve_glen')

        Returns:
            Dict[str, Any]: Dictionary containing:
                - first_name (str): Candidate's first name
                - last_name (str): Candidate's last name
                - email (str): Email address
                - phone_number (str): Phone number
                - mailing_address (str): Full mailing address
                - calendly_url (str): Original Calendly scheduling URL
                - linkedin_url (str): Original LinkedIn profile URL
                - portfolio_url (str): Original portfolio/website URL

        Example:
            >>> manager = CandidateProfileManager()
            >>> info = manager.get_candidate_info("steve_glen")
            >>> print(info['calendly_url'])
            'https://calendly.com/steve-glen/30min'
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT
                            first_name,
                            last_name,
                            email,
                            phone_number,
                            mailing_address,
                            calendly_url,
                            linkedin_url,
                            portfolio_url
                        FROM user_candidate_info
                        WHERE user_id = %s
                        """,
                        (user_id,),
                    )

                    result = cursor.fetchone()

                    if result:
                        logger.info(f"Retrieved candidate info for user_id={user_id}")
                        return dict(result)
                    else:
                        logger.warning(f"No candidate info found for user_id={user_id}")
                        return self._get_default_candidate_info()

        except Exception as e:
            logger.error(f"Error retrieving candidate info: {e}")
            # Return default info on error to prevent document generation failures
            return self._get_default_candidate_info()

    def get_calendly_url(self, user_id: str = "steve_glen") -> Optional[str]:
        """
        Get original (non-tracked) Calendly URL for user

        Args:
            user_id (str): User identifier (default: 'steve_glen')

        Returns:
            Optional[str]: Calendly URL or None if not set

        Example:
            >>> manager = CandidateProfileManager()
            >>> url = manager.get_calendly_url()
            >>> print(url)
            'https://calendly.com/steve-glen/30min'
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT calendly_url
                        FROM user_candidate_info
                        WHERE user_id = %s
                        """,
                        (user_id,),
                    )

                    result = cursor.fetchone()
                    if result and result["calendly_url"]:
                        return result["calendly_url"]
                    return None

        except Exception as e:
            logger.error(f"Error retrieving Calendly URL: {e}")
            return None

    def get_linkedin_url(self, user_id: str = "steve_glen") -> Optional[str]:
        """
        Get original (non-tracked) LinkedIn URL for user

        Args:
            user_id (str): User identifier (default: 'steve_glen')

        Returns:
            Optional[str]: LinkedIn URL or None if not set

        Example:
            >>> manager = CandidateProfileManager()
            >>> url = manager.get_linkedin_url()
            >>> print(url)
            'https://linkedin.com/in/steve-glen'
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT linkedin_url
                        FROM user_candidate_info
                        WHERE user_id = %s
                        """,
                        (user_id,),
                    )

                    result = cursor.fetchone()
                    if result and result["linkedin_url"]:
                        return result["linkedin_url"]
                    return None

        except Exception as e:
            logger.error(f"Error retrieving LinkedIn URL: {e}")
            return None

    def get_portfolio_url(self, user_id: str = "steve_glen") -> Optional[str]:
        """
        Get original (non-tracked) Portfolio/Website URL for user

        Args:
            user_id (str): User identifier (default: 'steve_glen')

        Returns:
            Optional[str]: Portfolio URL or None if not set

        Example:
            >>> manager = CandidateProfileManager()
            >>> url = manager.get_portfolio_url()
            >>> print(url)
            'https://steveglen.com'
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT portfolio_url
                        FROM user_candidate_info
                        WHERE user_id = %s
                        """,
                        (user_id,),
                    )

                    result = cursor.fetchone()
                    if result and result["portfolio_url"]:
                        return result["portfolio_url"]
                    return None

        except Exception as e:
            logger.error(f"Error retrieving Portfolio URL: {e}")
            return None

    def update_calendly_url(self, calendly_url: str, user_id: str = "steve_glen") -> bool:
        """
        Update user's Calendly URL in the database

        Args:
            calendly_url (str): New Calendly URL to store
            user_id (str): User identifier (default: 'steve_glen')

        Returns:
            bool: True if update successful, False otherwise

        Example:
            >>> manager = CandidateProfileManager()
            >>> success = manager.update_calendly_url("https://calendly.com/steve-glen/consultation")
            >>> print(success)
            True
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE user_candidate_info
                        SET calendly_url = %s
                        WHERE user_id = %s
                        """,
                        (calendly_url, user_id),
                    )
                    conn.commit()

                    if cursor.rowcount > 0:
                        logger.info(f"Updated Calendly URL for user_id={user_id}")
                        return True
                    else:
                        logger.warning(f"No user found with user_id={user_id}")
                        return False

        except Exception as e:
            logger.error(f"Error updating Calendly URL: {e}")
            return False

    def _get_default_candidate_info(self) -> Dict[str, Any]:
        """
        Get default candidate information when database retrieval fails

        Returns:
            Dict[str, Any]: Default candidate information structure

        Note:
            These defaults prevent document generation from failing when
            candidate data is unavailable. Update these values to match
            your system's requirements.
        """
        return {
            "first_name": "Steve",
            "last_name": "Glen",
            "email": "1234.s.t.e.v.e.glen@gmail.com",
            "phone_number": "(780) 555-0123",
            "mailing_address": "Edmonton, AB, Canada",
            "calendly_url": None,
            "linkedin_url": None,
            "portfolio_url": None,
        }


def main():
    """
    Demonstration of CandidateProfileManager usage
    """
    manager = CandidateProfileManager()

    # Get complete candidate information
    info = manager.get_candidate_info("steve_glen")
    print("Candidate Information:")
    print(f"Name: {info.get('first_name')} {info.get('last_name')}")
    print(f"Email: {info.get('email')}")
    print(f"Calendly: {info.get('calendly_url')}")

    # Get individual URLs
    calendly_url = manager.get_calendly_url("steve_glen")
    print(f"\nCalendly URL: {calendly_url}")

    linkedin_url = manager.get_linkedin_url("steve_glen")
    print(f"LinkedIn URL: {linkedin_url}")

    portfolio_url = manager.get_portfolio_url("steve_glen")
    print(f"Portfolio URL: {portfolio_url}")


if __name__ == "__main__":
    main()
