"""
Form State Manager for Multi-Page Form Checkpointing

This module manages form filling state and checkpointing for multi-page applications.
It provides functionality to save progress after each page, load checkpoints on retry,
and track page-specific filled fields.

Design Principles:
- Atomic database operations for consistency
- Checkpoint expiration to prevent stale resumes
- Comprehensive metadata tracking
- Graceful handling of database errors

Author: Application Automation System
Version: 1.1.0
Created: 2025-10-17
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import ApplicationSubmission

logger = logging.getLogger(__name__)


@dataclass
class CheckpointData:
    """
    Structured data for form filling checkpoint

    This dataclass represents the state of a partially-filled form, allowing
    the automation to resume from where it left off in case of failures.

    Attributes:
        current_page: Current page number being filled
        total_pages: Total pages in form (None if unknown)
        pages_completed: List of page numbers successfully completed
        page_fields: Dictionary mapping page numbers to lists of filled fields
        last_screenshot: Filename of most recent screenshot
        timestamp: When checkpoint was created (ISO format)
        metadata: Additional metadata (URLs, errors, etc.)
    """

    current_page: int
    total_pages: Optional[int]
    pages_completed: List[int] = field(default_factory=list)
    page_fields: Dict[int, List[str]] = field(default_factory=dict)
    last_screenshot: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckpointData":
        """Create from dictionary"""
        return cls(**data)

    def is_stale(self, max_age_hours: int = 1) -> bool:
        """
        Check if checkpoint is stale (too old to be useful)

        Args:
            max_age_hours: Maximum age in hours before checkpoint is considered stale

        Returns:
            True if checkpoint is stale, False otherwise
        """
        try:
            checkpoint_time = datetime.fromisoformat(self.timestamp)
            age = datetime.utcnow() - checkpoint_time
            is_stale = age > timedelta(hours=max_age_hours)

            if is_stale:
                logger.warning(
                    f"Checkpoint is stale: age={age.total_seconds()/3600:.2f}h, "
                    f"max_age={max_age_hours}h"
                )

            return is_stale
        except Exception as e:
            logger.error(f"Failed to check checkpoint staleness: {e}")
            return True  # Treat as stale if we can't parse timestamp

    def is_valid(self) -> bool:
        """
        Validate checkpoint data structure

        Returns:
            True if checkpoint has required fields and valid data, False otherwise
        """
        if self.current_page < 1:
            logger.error(f"Invalid current_page: {self.current_page}")
            return False

        if self.total_pages is not None and self.total_pages < self.current_page:
            logger.error(
                f"Invalid total_pages: {self.total_pages} < current_page: {self.current_page}"
            )
            return False

        if any(p < 1 for p in self.pages_completed):
            logger.error(f"Invalid page numbers in pages_completed: {self.pages_completed}")
            return False

        return True

    def add_page_fields(self, page_num: int, fields: List[str]):
        """
        Add filled fields for a specific page

        Args:
            page_num: Page number
            fields: List of field names filled on this page
        """
        if page_num not in self.page_fields:
            self.page_fields[page_num] = []
        self.page_fields[page_num].extend(fields)
        logger.debug(f"Added {len(fields)} fields for page {page_num}")

    def mark_page_complete(self, page_num: int):
        """
        Mark a page as completed

        Args:
            page_num: Page number to mark as complete
        """
        if page_num not in self.pages_completed:
            self.pages_completed.append(page_num)
            logger.debug(f"Marked page {page_num} as complete")


class FormStateManager:
    """
    Manages form filling state and checkpointing for multi-page applications

    This class provides methods to save and load checkpoints, enabling the
    automation system to resume from where it left off after failures.

    Example usage:
        manager = FormStateManager(db_session)

        # Save checkpoint after filling page 1
        await manager.save_checkpoint(
            submission_id="abc-123",
            page_num=1,
            fields_filled=["name", "email"],
            metadata={"url": "https://..."}
        )

        # Load checkpoint on retry
        checkpoint = await manager.load_checkpoint("abc-123")
        if checkpoint and not checkpoint.is_stale():
            print(f"Resuming from page {checkpoint.current_page}")
    """

    def __init__(self, db_session: Session):
        """
        Initialize form state manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        logger.info("FormStateManager initialized")

    async def save_checkpoint(
        self,
        submission_id: str,
        page_num: int,
        fields_filled: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        total_pages: Optional[int] = None,
    ) -> bool:
        """
        Save form filling checkpoint to database

        This method saves the current state of form filling, allowing resumption
        after failures. It updates the checkpoint_data JSONB column with structured
        data about which pages and fields have been completed.

        Args:
            submission_id: UUID of application submission
            page_num: Current page number (1-indexed)
            fields_filled: List of field names filled on this page
            metadata: Optional metadata (URLs, timestamps, etc.)
            total_pages: Total pages in form (if known)

        Returns:
            True if checkpoint saved successfully, False otherwise

        Example:
            success = await manager.save_checkpoint(
                submission_id="abc-123",
                page_num=2,
                fields_filled=["resume", "cover_letter"],
                metadata={"url": "https://apply.com/page2"},
                total_pages=3
            )
        """
        try:
            # Query submission
            submission = (
                self.db_session.query(ApplicationSubmission)
                .filter_by(submission_id=submission_id)
                .first()
            )

            if not submission:
                logger.error(f"Submission not found: {submission_id}")
                return False

            # Load existing checkpoint or create new
            if submission.checkpoint_data:
                try:
                    checkpoint = CheckpointData.from_dict(submission.checkpoint_data)
                except Exception as e:
                    logger.warning(f"Failed to load existing checkpoint, creating new: {e}")
                    checkpoint = CheckpointData(current_page=page_num, total_pages=total_pages)
            else:
                checkpoint = CheckpointData(current_page=page_num, total_pages=total_pages)

            # Update checkpoint with new data
            checkpoint.current_page = page_num
            checkpoint.add_page_fields(page_num, fields_filled)
            checkpoint.mark_page_complete(page_num)
            checkpoint.timestamp = datetime.utcnow().isoformat()

            if total_pages:
                checkpoint.total_pages = total_pages

            if metadata:
                checkpoint.metadata.update(metadata)

            # Update database record
            submission.checkpoint_data = checkpoint.to_dict()
            submission.current_page = page_num
            submission.total_pages = total_pages

            # Add to pages_completed array
            if submission.pages_completed is None:
                submission.pages_completed = []
            if page_num not in submission.pages_completed:
                submission.pages_completed.append(page_num)

            # Commit transaction
            self.db_session.commit()

            logger.info(
                f"Checkpoint saved: submission={submission_id}, page={page_num}, "
                f"fields={len(fields_filled)}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            self.db_session.rollback()
            return False

    async def load_checkpoint(self, submission_id: str) -> Optional[CheckpointData]:
        """
        Load form filling checkpoint from database

        This method retrieves the saved checkpoint for a submission, allowing
        the automation to resume from where it left off.

        Args:
            submission_id: UUID of application submission

        Returns:
            CheckpointData object if checkpoint exists and is valid, None otherwise

        Example:
            checkpoint = await manager.load_checkpoint("abc-123")
            if checkpoint and not checkpoint.is_stale():
                print(f"Resume from page {checkpoint.current_page}")
                print(f"Completed pages: {checkpoint.pages_completed}")
        """
        try:
            # Query submission
            submission = (
                self.db_session.query(ApplicationSubmission)
                .filter_by(submission_id=submission_id)
                .first()
            )

            if not submission:
                logger.error(f"Submission not found: {submission_id}")
                return None

            if not submission.checkpoint_data:
                logger.info(f"No checkpoint found for submission: {submission_id}")
                return None

            # Deserialize checkpoint
            checkpoint = CheckpointData.from_dict(submission.checkpoint_data)

            # Validate checkpoint
            if not checkpoint.is_valid():
                logger.warning(f"Checkpoint validation failed for submission: {submission_id}")
                return None

            if checkpoint.is_stale():
                logger.warning(
                    f"Checkpoint is stale for submission: {submission_id}, "
                    f"will not resume from it"
                )
                return None

            logger.info(
                f"Checkpoint loaded: submission={submission_id}, "
                f"current_page={checkpoint.current_page}, "
                f"completed_pages={checkpoint.pages_completed}"
            )
            return checkpoint

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

    async def clear_checkpoint(self, submission_id: str) -> bool:
        """
        Clear checkpoint data after successful completion

        This method clears the checkpoint data from the database after
        the form has been successfully submitted.

        Args:
            submission_id: UUID of application submission

        Returns:
            True if checkpoint cleared successfully, False otherwise

        Example:
            # After successful submission
            await manager.clear_checkpoint("abc-123")
        """
        try:
            # Query submission
            submission = (
                self.db_session.query(ApplicationSubmission)
                .filter_by(submission_id=submission_id)
                .first()
            )

            if not submission:
                logger.error(f"Submission not found: {submission_id}")
                return False

            # Clear checkpoint data
            submission.checkpoint_data = {}
            # Note: Keep current_page, total_pages, pages_completed for historical record

            # Commit transaction
            self.db_session.commit()

            logger.info(f"Checkpoint cleared for submission: {submission_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to clear checkpoint: {e}")
            self.db_session.rollback()
            return False

    async def update_page_progress(
        self, submission_id: str, page_num: int, navigation_action: Optional[str] = None
    ):
        """
        Update page progress tracking without full checkpoint save

        This is a lightweight update for tracking page navigation history.

        Args:
            submission_id: UUID of application submission
            page_num: Page number navigated to
            navigation_action: Action taken (e.g., "next", "back", "submit")

        Example:
            await manager.update_page_progress("abc-123", 2, "next")
        """
        try:
            submission = (
                self.db_session.query(ApplicationSubmission)
                .filter_by(submission_id=submission_id)
                .first()
            )

            if not submission:
                logger.error(f"Submission not found: {submission_id}")
                return

            # Update current page
            submission.current_page = page_num

            # Add to navigation history
            if submission.navigation_history is None:
                submission.navigation_history = []

            navigation_entry = {
                "to_page": page_num,
                "action": navigation_action or "navigate",
                "timestamp": datetime.utcnow().isoformat(),
            }

            submission.navigation_history.append(navigation_entry)

            # Commit transaction
            self.db_session.commit()

            logger.debug(
                f"Page progress updated: submission={submission_id}, "
                f"page={page_num}, action={navigation_action}"
            )

        except Exception as e:
            logger.error(f"Failed to update page progress: {e}")
            self.db_session.rollback()

    async def record_validation_error(
        self, submission_id: str, field_name: str, error_message: str, page_num: int
    ):
        """
        Record a validation error encountered during form filling

        Args:
            submission_id: UUID of application submission
            field_name: Name of field that failed validation
            error_message: Error message from form
            page_num: Page number where error occurred

        Example:
            await manager.record_validation_error(
                "abc-123",
                "email",
                "Invalid email format",
                1
            )
        """
        try:
            submission = (
                self.db_session.query(ApplicationSubmission)
                .filter_by(submission_id=submission_id)
                .first()
            )

            if not submission:
                logger.error(f"Submission not found: {submission_id}")
                return

            # Add to validation errors array
            if submission.validation_errors is None:
                submission.validation_errors = []

            error_entry = {
                "field": field_name,
                "error": error_message,
                "page": page_num,
                "timestamp": datetime.utcnow().isoformat(),
            }

            submission.validation_errors.append(error_entry)

            # Commit transaction
            self.db_session.commit()

            logger.info(
                f"Validation error recorded: submission={submission_id}, "
                f"field={field_name}, page={page_num}"
            )

        except Exception as e:
            logger.error(f"Failed to record validation error: {e}")
            self.db_session.rollback()
