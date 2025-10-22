"""
Module: database_writer.py
Purpose: Database write operations for jobs, applications, and settings
Created: 2024-08-18
Modified: 2025-10-21
Dependencies: SQLAlchemy, database_client, database_models
Related: database_reader.py, database_manager.py, database_client.py
Description: Handles all write operations including creates, updates, deletes for
             job application system. Organized by function: job creation/updates,
             status management, settings management, logging, and data cleanup.
             Inherits from DatabaseClient for connection management.
"""

import logging
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from .database_client import DatabaseClient
from .database_models import DocumentJob, JobLog, ApplicationSettings


class DatabaseWriter(DatabaseClient):
    """
    Database writer module for posting/updating/changing information in PostgreSQL.

    Handles all write operations including creates, updates, and deletes for the
    job application system. Inherits from DatabaseClient to utilize connection
    management functionality.

    Methods are organized by function:
    - Job creation and updates (create_job, update_job_success, update_job_failure)
    - Status management (update_job_status, mark_jobs_for_cleanup)
    - Settings management (create_or_update_setting, delete_setting)
    - Job logging (log_job_event)
    - Data cleanup (cleanup_old_jobs)
    """

    def __init__(self):
        """
        Initialize database writer.

        Calls parent DatabaseClient initialization to set up connection.
        """
        super().__init__()
        logging.info("Database writer module initialized")

    def create_job(self, document_type, webhook_data=None, title=None, author=None):
        """
        Create a new document generation job

        Args:
            document_type (str): Type of document ('resume', 'cover_letter', etc.)
            webhook_data (dict, optional): Original webhook data
            title (str, optional): Document title
            author (str, optional): Document author

        Returns:
            str: Job ID of created job
        """
        try:
            with self.get_session() as session:
                job = DocumentJob(
                    document_type=document_type,
                    webhook_data=webhook_data,
                    title=title,
                    author=author,
                    status="processing",
                    created_at=datetime.utcnow(),
                )

                session.add(job)
                session.flush()  # Flush to get the job_id

                job_id = str(job.job_id)
                logging.info(f"Created new job: {job_id} ({document_type})")
                return job_id

        except SQLAlchemyError as e:
            logging.error(f"Error creating job: {e}")
            raise

    def update_job_success(self, job_id, file_info):
        """
        Update job with successful completion details

        Args:
            job_id (str): Job ID to update
            file_info (dict): File information including path, size, etc.

        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            with self.get_session() as session:
                job = session.query(DocumentJob).filter(DocumentJob.job_id == job_id).first()

                if job:
                    job.status = "completed"
                    job.completed_at = datetime.utcnow()
                    job.file_path = file_info.get("file_path")
                    job.filename = file_info.get("filename")
                    job.file_size = file_info.get("file_size")
                    job.storage_type = file_info.get("storage_type")
                    job.object_storage_path = file_info.get("object_storage_path")
                    job.has_error = False

                    logging.info(f"Updated job {job_id} as completed")
                    return True
                else:
                    logging.warning(f"Job not found for update: {job_id}")
                    return False

        except SQLAlchemyError as e:
            logging.error(f"Error updating job success {job_id}: {e}")
            return False

    def update_job_failure(self, job_id, error_code, error_message, error_details=None):
        """
        Update job with failure details

        Args:
            job_id (str): Job ID to update
            error_code (str): Error code for categorization
            error_message (str): Human-readable error description
            error_details (dict, optional): Additional error context

        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            with self.get_session() as session:
                job = session.query(DocumentJob).filter(DocumentJob.job_id == job_id).first()

                if job:
                    job.status = "failed"
                    job.completed_at = datetime.utcnow()
                    job.has_error = True
                    job.error_code = error_code
                    job.error_message = error_message
                    job.error_details = error_details

                    logging.info(f"Updated job {job_id} as failed: {error_code}")
                    return True
                else:
                    logging.warning(f"Job not found for failure update: {job_id}")
                    return False

        except SQLAlchemyError as e:
            logging.error(f"Error updating job failure {job_id}: {e}")
            return False

    def add_job_log(self, job_id, message, log_level="INFO", details=None):
        """
        Add a log entry for a job

        Args:
            job_id (str): Job ID to log for
            message (str): Log message
            log_level (str): Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
            details (dict, optional): Additional structured data

        Returns:
            str: Log ID of created log entry
        """
        try:
            with self.get_session() as session:
                log_entry = JobLog(
                    job_id=job_id, message=message, log_level=log_level, details=details, timestamp=datetime.utcnow()
                )

                session.add(log_entry)
                session.flush()  # Flush to get the log_id

                log_id = str(log_entry.log_id)
                logging.debug(f"Added log entry {log_id} for job {job_id}")
                return log_id

        except SQLAlchemyError as e:
            logging.error(f"Error adding job log: {e}")
            raise

    def set_application_setting(self, setting_key, setting_value, setting_type="string", description=None):
        """
        Set an application setting (create or update)

        Args:
            setting_key (str): Setting key
            setting_value (str): Setting value
            setting_type (str): Type of setting ('string', 'json', 'integer', 'boolean')
            description (str, optional): Setting description

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                # Check if setting already exists
                existing_setting = (
                    session.query(ApplicationSettings).filter(ApplicationSettings.setting_key == setting_key).first()
                )

                if existing_setting:
                    # Update existing setting
                    existing_setting.setting_value = setting_value
                    existing_setting.setting_type = setting_type
                    existing_setting.description = description
                    existing_setting.updated_at = datetime.utcnow()

                    logging.info(f"Updated application setting: {setting_key}")
                else:
                    # Create new setting
                    new_setting = ApplicationSettings(
                        setting_key=setting_key,
                        setting_value=setting_value,
                        setting_type=setting_type,
                        description=description,
                    )
                    session.add(new_setting)

                    logging.info(f"Created application setting: {setting_key}")

                return True

        except SQLAlchemyError as e:
            logging.error(f"Error setting application setting {setting_key}: {e}")
            return False

    def delete_application_setting(self, setting_key):
        """
        Delete an application setting

        Args:
            setting_key (str): Setting key to delete

        Returns:
            bool: True if deleted, False if not found or error
        """
        try:
            with self.get_session() as session:
                setting = (
                    session.query(ApplicationSettings).filter(ApplicationSettings.setting_key == setting_key).first()
                )

                if setting:
                    session.delete(setting)
                    logging.info(f"Deleted application setting: {setting_key}")
                    return True
                else:
                    logging.warning(f"Setting not found for deletion: {setting_key}")
                    return False

        except SQLAlchemyError as e:
            logging.error(f"Error deleting application setting {setting_key}: {e}")
            return False

    def create_or_update_setting(self, setting_key, setting_value, setting_type="string", description=None):
        """
        Create or update an application setting

        Args:
            setting_key (str): Setting key
            setting_value (str): Setting value
            setting_type (str): Type of setting ('string', 'json', 'integer', 'boolean')
            description (str, optional): Setting description

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                setting = (
                    session.query(ApplicationSettings).filter(ApplicationSettings.setting_key == setting_key).first()
                )

                if setting:
                    # Update existing setting
                    setting.setting_value = setting_value
                    setting.setting_type = setting_type
                    setting.updated_at = datetime.utcnow()
                    if description:
                        setting.description = description
                    logging.info(f"Updated application setting: {setting_key}")
                else:
                    # Create new setting
                    setting = ApplicationSettings(
                        setting_key=setting_key,
                        setting_value=setting_value,
                        setting_type=setting_type,
                        description=description,
                    )
                    session.add(setting)
                    logging.info(f"Created application setting: {setting_key}")

                return True

        except SQLAlchemyError as e:
            logging.error(f"Error creating/updating application setting {setting_key}: {e}")
            return False

    def delete_old_jobs(self, days_old=30, status_filter=None):
        """
        Delete old jobs to clean up database

        Args:
            days_old (int): Delete jobs older than this many days
            status_filter (str, optional): Only delete jobs with this status

        Returns:
            int: Number of jobs deleted
        """
        try:
            with self.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days_old)

                query = session.query(DocumentJob).filter(DocumentJob.created_at < cutoff_date)

                if status_filter:
                    query = query.filter(DocumentJob.status == status_filter)

                # First, delete associated logs
                job_ids_to_delete = [str(job.job_id) for job in query.all()]

                if job_ids_to_delete:
                    # Delete logs first (foreign key dependency)
                    logs_deleted = session.query(JobLog).filter(JobLog.job_id.in_(job_ids_to_delete)).delete()

                    # Then delete jobs
                    jobs_deleted = query.delete()

                    logging.info(f"Deleted {jobs_deleted} old jobs and {logs_deleted} associated logs")
                    return jobs_deleted
                else:
                    logging.info("No old jobs found for deletion")
                    return 0

        except SQLAlchemyError as e:
            logging.error(f"Error deleting old jobs: {e}")
            return 0

    def update_job_metadata(self, job_id, title=None, author=None):
        """
        Update job metadata (title, author)

        Args:
            job_id (str): Job ID to update
            title (str, optional): New title
            author (str, optional): New author

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                job = session.query(DocumentJob).filter(DocumentJob.job_id == job_id).first()

                if job:
                    if title is not None:
                        job.title = title
                    if author is not None:
                        job.author = author

                    logging.info(f"Updated metadata for job {job_id}")
                    return True
                else:
                    logging.warning(f"Job not found for metadata update: {job_id}")
                    return False

        except SQLAlchemyError as e:
            logging.error(f"Error updating job metadata {job_id}: {e}")
            return False

    def bulk_update_job_status(self, job_ids, new_status):
        """
        Update status for multiple jobs at once

        Args:
            job_ids (list): List of job IDs to update
            new_status (str): New status to set

        Returns:
            int: Number of jobs updated
        """
        try:
            with self.get_session() as session:
                updated_count = (
                    session.query(DocumentJob)
                    .filter(DocumentJob.job_id.in_(job_ids))
                    .update({"status": new_status}, synchronize_session=False)
                )

                logging.info(f"Bulk updated {updated_count} jobs to status: {new_status}")
                return updated_count

        except SQLAlchemyError as e:
            logging.error(f"Error bulk updating job status: {e}")
            return 0
