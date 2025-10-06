import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from .database_client import Base


class DocumentJob(Base):
    """
    Table for tracking document generation jobs.

    Stores comprehensive information about document generation requests,
    including job status, file details, document metadata, and error handling.
    Each job represents a single document generation request from the webhook.

    Attributes:
        job_id: UUID primary key for the job
        file_path: Path to generated file (NULL if error)
        filename: Name of generated file (NULL if error)
        file_size: Size of file in bytes
        title: Document title
        author: Document author
        document_type: Type of document ('resume', 'cover_letter', etc.)
        status: Job status ('processing', 'completed', 'failed')
        created_at: Timestamp when job was created
        completed_at: Timestamp when job completed
        webhook_data: Original webhook data as JSON
        has_error: Boolean flag for error state
        error_code: Error code if failed
        error_message: Human-readable error message
        error_details: Detailed error information as JSON
        storage_type: Type of storage used ('object_storage', 'local')
        object_storage_path: Path in object storage if applicable
    """

    __tablename__ = "document_jobs"

    # Primary key - auto-generated UUID
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # File information
    file_path = Column(String(500), nullable=True)  # NULL if error occurred
    filename = Column(String(255), nullable=True)  # NULL if error occurred
    file_size = Column(Integer, nullable=True)  # File size in bytes

    # Document metadata
    title = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    document_type = Column(String(50), nullable=False)  # 'resume', 'cover_letter', etc.

    # Job tracking
    status = Column(String(50), default="processing")  # 'processing', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Webhook data (stored as JSON for flexibility)
    webhook_data = Column(JSON, nullable=True)

    # Error handling
    has_error = Column(Boolean, default=False)
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)

    # Storage information
    storage_type = Column(String(50), nullable=True)  # 'object_storage', 'local'
    object_storage_path = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<DocumentJob(job_id={self.job_id}, status={self.status}, document_type={self.document_type})>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "job_id": str(self.job_id),
            "file_path": self.file_path,
            "filename": self.filename,
            "file_size": self.file_size,
            "title": self.title,
            "author": self.author,
            "document_type": self.document_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "webhook_data": self.webhook_data,
            "has_error": self.has_error,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "storage_type": self.storage_type,
            "object_storage_path": self.object_storage_path,
        }


class JobLog(Base):
    """
    Table for detailed job logging and audit trail
    Stores step-by-step progress and debugging information
    """

    __tablename__ = "job_logs"

    # Primary key
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to document_jobs
    job_id = Column(UUID(as_uuid=True), nullable=False)

    # Log details
    timestamp = Column(DateTime, default=datetime.utcnow)
    log_level = Column(String(20), default="INFO")  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Additional structured data

    def __repr__(self):
        return f"<JobLog(job_id={self.job_id}, level={self.log_level}, message={self.message[:50]}...)>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "log_id": str(self.log_id),
            "job_id": str(self.job_id),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "log_level": self.log_level,
            "message": self.message,
            "details": self.details,
        }


class ApplicationSettings(Base):
    """
    Table for storing application configuration and settings
    Key-value store for dynamic configuration
    """

    __tablename__ = "application_settings"

    # Primary key
    setting_key = Column(String(100), primary_key=True)

    # Setting data
    setting_value = Column(Text, nullable=True)
    setting_type = Column(String(20), default="string")  # 'string', 'json', 'integer', 'boolean'
    description = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ApplicationSettings(key={self.setting_key}, type={self.setting_type})>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "setting_key": self.setting_key,
            "setting_value": self.setting_value,
            "setting_type": self.setting_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
