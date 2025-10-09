---
title: Coding Standards & Best Practices
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: standards
status: active
tags:
- coding
- standards
---

# Coding Standards & Best Practices

## Purpose
This document establishes comprehensive coding standards for the Automated Job Application System. These standards ensure consistency, maintainability, security, and quality across the entire codebase.

## Python Code Standards

### 1. Code Formatting

#### Line Length and Layout
```python
# Maximum line length: 120 characters
# Configured in .black.toml
MAX_LINE_LENGTH = 120

# Use Black formatter for consistent formatting
# Example of well-formatted function:
def process_job_application(
    job_title: str,
    company_name: str,
    application_date: datetime,
    resume_template: Optional[str] = None,
) -> Dict[str, Any]:
    """Process job application with proper formatting."""
    return {
        "job_title": job_title,
        "company_name": company_name,
        "application_date": application_date.isoformat(),
        "status": "submitted",
    }
```

#### Import Organization
```python
# Standard library imports
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Third-party imports
import flask
from sqlalchemy import text
from werkzeug.security import generate_password_hash

# Local application imports
from modules.database import database_manager
from modules.email_integration import gmail_sender
from modules.utils import security_utils
```

### 2. Naming Conventions

#### Variables and Functions
```python
# Use descriptive, snake_case names
user_preferences = load_user_preferences()
job_application_count = calculate_application_count()

# Avoid abbreviated or unclear names
# BAD: usr_prefs, calc_app_cnt
# GOOD: user_preferences, job_application_count

# Boolean variables should be clear about their state
is_application_submitted = True
has_valid_credentials = check_credentials()
can_send_email = verify_email_permissions()
```

#### Classes and Methods
```python
# Classes use PascalCase
class JobApplicationManager:
    """Manages job application workflow and tracking."""
    
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.application_history: List[Dict[str, Any]] = []
    
    def submit_application(
        self, 
        job_posting: JobPosting, 
        resume_path: str
    ) -> ApplicationResult:
        """Submit job application with proper error handling."""
        pass

# Method names use snake_case and describe actions
def generate_cover_letter(self, job_posting: JobPosting) -> str:
    """Generate personalized cover letter for job posting."""
    pass

def validate_email_credentials(self) -> bool:
    """Validate Gmail OAuth credentials are current."""
    pass
```

#### Constants and Configuration
```python
# Constants use SCREAMING_SNAKE_CASE
MAX_APPLICATIONS_PER_DAY = 50
DEFAULT_RESUME_TEMPLATE = "harvard_mcs_template"
EMAIL_RATE_LIMIT_MINUTES = 6 * 24 * 60  # 6 days in minutes

# Configuration keys should be descriptive
DATABASE_CONNECTION_TIMEOUT = 30
GMAIL_API_RETRY_ATTEMPTS = 3
JOB_SEARCH_RADIUS_MILES = 25
```

### 3. Type Annotations

#### Function Signatures
```python
from typing import Dict, List, Optional, Union, Any, Tuple

# All public functions must have type annotations
def analyze_job_compatibility(
    job_description: str,
    user_skills: List[str],
    experience_years: int,
    salary_range: Optional[Tuple[int, int]] = None
) -> Dict[str, Union[float, str, bool]]:
    """
    Analyze compatibility between job posting and user profile.
    
    Args:
        job_description: Full text of job posting
        user_skills: List of user's technical skills
        experience_years: Years of relevant experience
        salary_range: Optional min/max salary expectations
    
    Returns:
        Dictionary containing compatibility score and analysis
    """
    pass

# Use Optional for nullable parameters
def send_application_email(
    recipient_email: str,
    subject: str,
    body: str,
    attachments: Optional[List[str]] = None
) -> bool:
    """Send application email with optional attachments."""
    pass
```

#### Class Type Hints
```python
from typing import ClassVar, Protocol

class DatabaseConnection(Protocol):
    """Protocol defining database connection interface."""
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]: ...
    def commit_transaction(self) -> None: ...

class JobTracker:
    """Track job applications and responses."""
    
    # Class variables with type hints
    max_concurrent_applications: ClassVar[int] = 10
    default_timeout: ClassVar[float] = 30.0
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        self.db: DatabaseConnection = db_connection
        self.active_applications: Dict[str, ApplicationStatus] = {}
```

### 4. Documentation Standards

#### Function Documentation
```python
def generate_resume_from_template(
    template_path: str,
    user_data: Dict[str, Any],
    job_posting: JobPosting,
    output_path: Optional[str] = None
) -> Tuple[str, bool]:
    """
    Generate personalized resume from template and user data.
    
    This function loads a Word document template, replaces placeholder
    variables with user-specific information, and generates a customized
    resume tailored to the specific job posting.
    
    Args:
        template_path: Path to the .docx template file
        user_data: Dictionary containing user profile information
            Expected keys: name, email, phone, skills, experience
        job_posting: JobPosting object with job details
        output_path: Optional custom output path, auto-generated if None
    
    Returns:
        Tuple of (output_file_path, success_status)
        
    Raises:
        FileNotFoundError: If template file doesn't exist
        PermissionError: If unable to write to output directory
        TemplateProcessingError: If template processing fails
        
    Example:
        >>> user_info = {"name": "John Doe", "email": "john@example.com"}
        >>> job = JobPosting(title="Software Engineer", company="TechCorp")
        >>> path, success = generate_resume_from_template(
        ...     "templates/resume.docx", user_info, job
        ... )
        >>> print(f"Resume saved to: {path}")
    """
    pass
```

#### Class Documentation
```python
class EmailIntegrationManager:
    """
    Manages Gmail OAuth integration and email sending capabilities.
    
    This class handles the complete email workflow including:
    - OAuth 2.0 authentication with Gmail API
    - Token management and refresh
    - Email composition and sending
    - Attachment handling for resumes and cover letters
    - Rate limiting and error recovery
    
    The class maintains persistent OAuth tokens and handles automatic
    token refresh as needed. It implements enterprise-grade error
    handling and retry logic for reliable email delivery.
    
    Attributes:
        credentials_path: Path to Gmail API credentials file
        token_path: Path to stored OAuth token
        rate_limiter: Controls email sending frequency
        retry_config: Configuration for failed email retry attempts
    
    Example:
        >>> email_manager = EmailIntegrationManager()
        >>> email_manager.authenticate()
        >>> success = email_manager.send_application_email(
        ...     "hr@company.com", "Job Application", body, ["resume.pdf"]
        ... )
    """
    
    def __init__(self, credentials_path: str = "storage/gmail_credentials.json"):
        """Initialize email manager with credential path."""
        pass
```

### 5. Security Standards

#### Database Query Security
```python
# ALWAYS use parameterized queries - NEVER string concatenation
from sqlalchemy import text

# GOOD: Parameterized query
def get_user_applications(user_id: int, status: str) -> List[Dict[str, Any]]:
    """Get user applications with specific status."""
    query = text("""
        SELECT id, job_title, company_name, status, created_at
        FROM job_applications 
        WHERE user_id = :user_id AND status = :status
        ORDER BY created_at DESC
    """)
    
    result = db.session.execute(
        query, 
        {"user_id": user_id, "status": status}
    )
    return [dict(row) for row in result]

# BAD: String concatenation (SQL injection risk)
def get_user_applications_bad(user_id: int, status: str):
    query = f"SELECT * FROM applications WHERE user_id = {user_id} AND status = '{status}'"
    # This is vulnerable to SQL injection - NEVER DO THIS
```

#### Input Validation
```python
from typing import Union
import re

def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_job_title(title: str) -> str:
    """Sanitize job title for safe storage and display."""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', title)
    # Limit length
    return sanitized[:200]

def validate_user_input(data: Dict[str, Any]) -> Dict[str, str]:
    """Validate user input and return error messages."""
    errors = {}
    
    if not data.get('email') or not validate_email_address(data['email']):
        errors['email'] = 'Valid email address required'
    
    if not data.get('name') or len(data['name']) < 2:
        errors['name'] = 'Name must be at least 2 characters'
        
    return errors
```

#### Secret Management
```python
import os
from typing import Optional

def get_database_url() -> str:
    """Get database URL from environment variables."""
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise ValueError("DATABASE_URL environment variable not set")
    return url

def get_api_key(service_name: str) -> Optional[str]:
    """Get API key for specified service."""
    key_name = f"{service_name.upper()}_API_KEY"
    return os.environ.get(key_name)

# NEVER hardcode secrets
# BAD: api_key = "sk-1234567890abcdef"
# GOOD: api_key = get_api_key("openai")
```

### 6. Error Handling

#### Exception Handling Patterns
```python
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def process_job_application(application_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Process job application with comprehensive error handling.
    
    Returns:
        Tuple of (success_status, error_message)
    """
    try:
        # Validate input data
        validation_errors = validate_application_data(application_data)
        if validation_errors:
            return False, f"Validation failed: {validation_errors}"
        
        # Process application
        result = submit_application_to_system(application_data)
        
        logger.info(f"Successfully processed application for {application_data.get('job_title')}")
        return True, None
        
    except ValidationError as e:
        logger.warning(f"Application validation failed: {e}")
        return False, f"Invalid application data: {e}"
        
    except DatabaseError as e:
        logger.error(f"Database error during application processing: {e}")
        return False, "Unable to save application. Please try again."
        
    except ExternalAPIError as e:
        logger.error(f"External service error: {e}")
        return False, "Service temporarily unavailable. Please try again later."
        
    except Exception as e:
        logger.error(f"Unexpected error processing application: {e}", exc_info=True)
        return False, "An unexpected error occurred. Please contact support."
```

#### Logging Standards
```python
import logging

# Configure logging at module level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('storage/logs/application.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def track_application_submission(job_id: str, user_id: int) -> None:
    """Track application submission with appropriate logging."""
    try:
        # Log successful operations at INFO level
        logger.info(f"User {user_id} submitted application for job {job_id}")
        
        # Log business logic decisions at DEBUG level
        logger.debug(f"Application validation passed for job {job_id}")
        
        # Log security events at WARNING level
        if suspicious_activity_detected(user_id):
            logger.warning(f"Suspicious activity detected for user {user_id}")
            
    except Exception as e:
        # Log errors with full exception details
        logger.error(f"Failed to track application submission: {e}", exc_info=True)
```

### 7. Testing Standards

#### Unit Test Structure
```python
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

class TestJobApplicationManager(unittest.TestCase):
    """Test cases for JobApplicationManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.manager = JobApplicationManager(user_id=1)
        self.sample_job = JobPosting(
            title="Software Engineer",
            company="TechCorp",
            description="Python development position"
        )
    
    def test_submit_application_success(self):
        """Test successful application submission."""
        with patch('modules.email_integration.send_email') as mock_send:
            mock_send.return_value = True
            
            result = self.manager.submit_application(
                self.sample_job,
                "path/to/resume.pdf"
            )
            
            self.assertTrue(result.success)
            self.assertIsNotNone(result.application_id)
            mock_send.assert_called_once()
    
    def test_submit_application_email_failure(self):
        """Test application submission with email failure."""
        with patch('modules.email_integration.send_email') as mock_send:
            mock_send.return_value = False
            
            result = self.manager.submit_application(
                self.sample_job,
                "path/to/resume.pdf"
            )
            
            self.assertFalse(result.success)
            self.assertIn("email", result.error_message.lower())
```

### 8. Performance Guidelines

#### Database Query Optimization
```python
# Use batch operations for multiple records
def update_multiple_applications(application_updates: List[Dict[str, Any]]) -> None:
    """Update multiple applications in a single transaction."""
    with db.session.begin():
        for update in application_updates:
            db.session.execute(
                text("""
                    UPDATE job_applications 
                    SET status = :status, updated_at = :updated_at
                    WHERE id = :application_id
                """),
                update
            )

# Use proper indexing and avoid N+1 queries
def get_applications_with_companies(user_id: int) -> List[Dict[str, Any]]:
    """Get applications with company details in single query."""
    query = text("""
        SELECT 
            ja.id, ja.job_title, ja.status, ja.created_at,
            c.name as company_name, c.website as company_website
        FROM job_applications ja
        JOIN companies c ON ja.company_id = c.id
        WHERE ja.user_id = :user_id
        ORDER BY ja.created_at DESC
    """)
    
    result = db.session.execute(query, {"user_id": user_id})
    return [dict(row) for row in result]
```

#### Memory Management
```python
from typing import Iterator

def process_large_dataset(data_source: str) -> Iterator[Dict[str, Any]]:
    """Process large datasets using generators to manage memory."""
    with open(data_source, 'r') as file:
        for line in file:
            # Process one record at a time
            record = parse_job_posting(line)
            if is_valid_posting(record):
                yield record

# Use context managers for resource cleanup
def process_document_template(template_path: str) -> str:
    """Process document template with proper resource management."""
    with open(template_path, 'rb') as template_file:
        document = Document(template_file)
        # Process document
        processed_content = apply_template_variables(document)
        return processed_content
    # File automatically closed after with block
```

## File Organization Standards

### Directory Structure
```
project_root/
├── modules/                    # Core application modules
│   ├── database/              # Database layer
│   ├── email_integration/     # Email functionality
│   ├── scraping/             # Job scraping
│   └── utils/                # Shared utilities
├── docs/                      # Documentation
├── tests/                     # Test files
├── tools/                     # Development tools and scripts
├── static/                    # Web assets (CSS, JS)
├── storage/                   # File storage and logs
└── archived_files/           # Legacy and backup files
```

### File Naming Conventions
- Python files: `snake_case.py`
- Configuration files: `lowercase.toml`, `lowercase.json`
- Documentation: `UPPERCASE.md` for main docs, `lowercase.md` for specific guides
- Scripts: `snake_case.sh`
- Templates: `descriptive_name.docx`

## Commit Message Standards

### Format
```
<type>(<scope>): <description>

<body>

<footer>
```

### Examples
```
feat(email): add rate limiting for job application emails

Implement 6-day waiting period between emails to same company.
Add database tracking for email history and automated enforcement.

Closes #123
```

```
fix(security): prevent SQL injection in job search queries

Convert raw SQL strings to parameterized queries using SQLAlchemy text().
Affects content_manager.py and tone_analyzer.py modules.

Security-Impact: High
```

```
docs(standards): add comprehensive coding standards documentation

Create detailed guidelines for Python development including:
- Code formatting and style requirements
- Security best practices
- Documentation standards
- Testing guidelines
```

---

**Document Maintained By:** Development Team  
**Last Updated:** July 30, 2025  
**Enforcement:** Automated via Black, Flake8, and code review  
**Version:** 1.0  