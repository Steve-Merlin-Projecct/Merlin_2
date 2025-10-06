import logging
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from .database_client import DatabaseClient
from .database_models import DocumentJob, JobLog, ApplicationSettings


class DatabaseReader(DatabaseClient):
    """
    Database reader module for fetching information from PostgreSQL.

    Handles all read operations and complex queries for the job application system.
    Inherits from DatabaseClient to utilize connection management functionality.

    Methods are organized by function:
    - Job retrieval (get_job_by_id, get_recent_jobs)
    - Job statistics (get_job_statistics, get_jobs_by_date_range)
    - Search functionality (search_jobs, get_failed_jobs)
    - Settings management (get_setting_by_key, get_all_settings)
    """

    def __init__(self):
        """
        Initialize database reader.

        Calls parent DatabaseClient initialization to set up connection.
        """
        super().__init__()
        logging.info("Database reader module initialized")

    def get_job_by_id(self, job_id):
        """
        Get a specific job by ID

        Args:
            job_id (str): Job ID to retrieve

        Returns:
            dict or None: Job information or None if not found
        """
        try:
            with self.get_session() as session:
                job = session.query(DocumentJob).filter(DocumentJob.job_id == job_id).first()
                return job.to_dict() if job else None
        except SQLAlchemyError as e:
            logging.error(f"Error fetching job {job_id}: {e}")
            return None

    def get_recent_jobs(self, limit=20, document_type=None):
        """
        Get recent jobs, optionally filtered by document type

        Args:
            limit (int): Maximum number of jobs to return
            document_type (str, optional): Filter by document type ('resume', 'cover_letter', etc.)

        Returns:
            list: List of job dictionaries
        """
        try:
            with self.get_session() as session:
                query = session.query(DocumentJob)

                if document_type:
                    query = query.filter(DocumentJob.document_type == document_type)

                jobs = query.order_by(desc(DocumentJob.created_at)).limit(limit).all()
                return [job.to_dict() for job in jobs]
        except SQLAlchemyError as e:
            logging.error(f"Error fetching recent jobs: {e}")
            return []

    def get_jobs_by_status(self, status, limit=50):
        """
        Get jobs by status

        Args:
            status (str): Job status ('processing', 'completed', 'failed')
            limit (int): Maximum number of jobs to return

        Returns:
            list: List of job dictionaries
        """
        try:
            with self.get_session() as session:
                jobs = (
                    session.query(DocumentJob)
                    .filter(DocumentJob.status == status)
                    .order_by(desc(DocumentJob.created_at))
                    .limit(limit)
                    .all()
                )
                return [job.to_dict() for job in jobs]
        except SQLAlchemyError as e:
            logging.error(f"Error fetching jobs by status {status}: {e}")
            return []

    def get_failed_jobs(self, limit=20):
        """
        Get failed jobs with error details

        Args:
            limit (int): Maximum number of jobs to return

        Returns:
            list: List of failed job dictionaries
        """
        try:
            with self.get_session() as session:
                jobs = (
                    session.query(DocumentJob)
                    .filter(DocumentJob.has_error == True)
                    .order_by(desc(DocumentJob.created_at))
                    .limit(limit)
                    .all()
                )
                return [job.to_dict() for job in jobs]
        except SQLAlchemyError as e:
            logging.error(f"Error fetching failed jobs: {e}")
            return []

    def get_jobs_by_date_range(self, start_date, end_date, document_type=None):
        """
        Get jobs within a date range

        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
            document_type (str, optional): Filter by document type

        Returns:
            list: List of job dictionaries
        """
        try:
            with self.get_session() as session:
                query = session.query(DocumentJob).filter(
                    and_(DocumentJob.created_at >= start_date, DocumentJob.created_at <= end_date)
                )

                if document_type:
                    query = query.filter(DocumentJob.document_type == document_type)

                jobs = query.order_by(desc(DocumentJob.created_at)).all()
                return [job.to_dict() for job in jobs]
        except SQLAlchemyError as e:
            logging.error(f"Error fetching jobs by date range: {e}")
            return []

    def get_job_statistics(self):
        """
        Get overall job statistics

        Returns:
            dict: Statistics including total jobs, success rate, etc.
        """
        try:
            with self.get_session() as session:
                total_jobs = session.query(DocumentJob).count()
                completed_jobs = session.query(DocumentJob).filter(DocumentJob.status == "completed").count()
                failed_jobs = session.query(DocumentJob).filter(DocumentJob.has_error == True).count()
                processing_jobs = session.query(DocumentJob).filter(DocumentJob.status == "processing").count()

                # Get counts by document type
                resume_jobs = session.query(DocumentJob).filter(DocumentJob.document_type == "resume").count()
                cover_letter_jobs = (
                    session.query(DocumentJob).filter(DocumentJob.document_type == "cover_letter").count()
                )

                # Calculate success rate
                success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0

                return {
                    "total_jobs": total_jobs,
                    "completed_jobs": completed_jobs,
                    "failed_jobs": failed_jobs,
                    "processing_jobs": processing_jobs,
                    "success_rate": round(success_rate, 2),
                    "document_types": {"resume": resume_jobs, "cover_letter": cover_letter_jobs},
                }
        except SQLAlchemyError as e:
            logging.error(f"Error fetching job statistics: {e}")
            return {}

    def get_job_logs(self, job_id, limit=50):
        """
        Get logs for a specific job

        Args:
            job_id (str): Job ID to get logs for
            limit (int): Maximum number of logs to return

        Returns:
            list: List of log dictionaries
        """
        try:
            with self.get_session() as session:
                logs = (
                    session.query(JobLog)
                    .filter(JobLog.job_id == job_id)
                    .order_by(desc(JobLog.timestamp))
                    .limit(limit)
                    .all()
                )
                return [log.to_dict() for log in logs]
        except SQLAlchemyError as e:
            logging.error(f"Error fetching logs for job {job_id}: {e}")
            return []

    def search_jobs(self, search_term, limit=20):
        """
        Search jobs by title, author, or filename

        Args:
            search_term (str): Term to search for
            limit (int): Maximum number of results

        Returns:
            list: List of matching job dictionaries
        """
        try:
            with self.get_session() as session:
                search_pattern = f"%{search_term}%"
                jobs = (
                    session.query(DocumentJob)
                    .filter(
                        or_(
                            DocumentJob.title.ilike(search_pattern),
                            DocumentJob.author.ilike(search_pattern),
                            DocumentJob.filename.ilike(search_pattern),
                        )
                    )
                    .order_by(desc(DocumentJob.created_at))
                    .limit(limit)
                    .all()
                )
                return [job.to_dict() for job in jobs]
        except SQLAlchemyError as e:
            logging.error(f"Error searching jobs: {e}")
            return []

    def get_application_setting(self, setting_key):
        """
        Get an application setting by key

        Args:
            setting_key (str): Setting key to retrieve

        Returns:
            dict or None: Setting information or None if not found
        """
        try:
            with self.get_session() as session:
                setting = (
                    session.query(ApplicationSettings).filter(ApplicationSettings.setting_key == setting_key).first()
                )
                return setting.to_dict() if setting else None
        except SQLAlchemyError as e:
            logging.error(f"Error fetching setting {setting_key}: {e}")
            return None

    def get_all_settings(self):
        """
        Get all application settings

        Returns:
            list: List of all settings
        """
        try:
            with self.get_session() as session:
                settings = session.query(ApplicationSettings).order_by(ApplicationSettings.setting_key).all()
                return [setting.to_dict() for setting in settings]
        except SQLAlchemyError as e:
            logging.error(f"Error fetching all settings: {e}")
            return []

    def get_jobs_summary_by_author(self, author_name):
        """
        Get job summary for a specific author

        Args:
            author_name (str): Author name to search for

        Returns:
            dict: Summary of jobs for the author
        """
        try:
            with self.get_session() as session:
                total_jobs = session.query(DocumentJob).filter(DocumentJob.author.ilike(f"%{author_name}%")).count()

                completed_jobs = (
                    session.query(DocumentJob)
                    .filter(and_(DocumentJob.author.ilike(f"%{author_name}%"), DocumentJob.status == "completed"))
                    .count()
                )

                recent_jobs = (
                    session.query(DocumentJob)
                    .filter(DocumentJob.author.ilike(f"%{author_name}%"))
                    .order_by(desc(DocumentJob.created_at))
                    .limit(5)
                    .all()
                )

                return {
                    "author": author_name,
                    "total_jobs": total_jobs,
                    "completed_jobs": completed_jobs,
                    "recent_jobs": [job.to_dict() for job in recent_jobs],
                }
        except SQLAlchemyError as e:
            logging.error(f"Error fetching author summary for {author_name}: {e}")
            return {}

    def get_setting_by_key(self, setting_key: str, as_dict: bool = True):
        """
        Get an application setting by key

        Args:
            setting_key (str): Setting key to retrieve
            as_dict (bool): Return as dictionary (default) or SQLAlchemy object

        Returns:
            dict or ApplicationSettings or None: Setting data or None if not found
        """
        try:
            with self.get_session() as session:
                setting = (
                    session.query(ApplicationSettings).filter(ApplicationSettings.setting_key == setting_key).first()
                )

                if setting and as_dict:
                    return setting.to_dict()
                return setting
        except SQLAlchemyError as e:
            logging.error(f"Error fetching setting {setting_key}: {e}")
            return None
