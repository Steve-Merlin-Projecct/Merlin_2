# Documentation Requirements Guide
**Version:** 1.0
**Date:** October 6, 2025
**Environment:** Claude Code

## Overview

This guide defines the comprehensive documentation requirements for all code and features implemented through the Automated Task Workflow. Documentation is **required** and should be created as part of the implementation tasks, not as an afterthought.

## Documentation Principles

1. **Documentation is Code:** Documentation is as important as the implementation itself
2. **Context Over Brevity:** Explain the "why" and "how it fits", not just the "what"
3. **Future-Proof:** Write for developers who will maintain this code in 6 months
4. **Living Documentation:** Update documentation when code changes
5. **Organized by Purpose:** Place documentation where developers will look for it

## Two Types of Documentation Required

### 1. Inline Code Documentation
**Purpose:** Explain code behavior and implementation details within the code itself

**Location:** Directly in source files (`.py`, `.js`, `.go`, etc.)

### 2. Component Documentation
**Purpose:** Explain system architecture, data flow, and integration points

**Location:** `/docs/component_docs/[module-name]/`

## Inline Code Documentation

### Required for Every File

**File-level docstring:**
```python
"""
User Authentication Module

This module handles user authentication, session management, and password
security for the job application system. It provides OAuth integration,
password hashing, and token-based session management.

Key Components:
    - User model (SQLAlchemy ORM)
    - Authentication service (login/logout/session management)
    - Password utilities (hashing, validation, strength checking)

Dependencies:
    - bcrypt: Password hashing
    - Flask-Login: Session management
    - SQLAlchemy: Database ORM
    - modules/database: Database connection

Database Tables:
    - users: User credentials and profile data
    - sessions: Active user sessions

Related Documentation:
    - /docs/component_docs/authentication/auth_system.md
    - /docs/api/auth_endpoints.md

Author: AI Assistant (Claude Code)
Date: 2025-10-06
Version: 1.0
"""
```

### Required for Every Class

```python
class UserAuthenticationService:
    """
    Service class for user authentication operations.

    This service handles user login, logout, session creation, and validation.
    It integrates with the User model and provides a clean interface for
    authentication operations throughout the application.

    Attributes:
        db_session: SQLAlchemy database session for user queries
        session_timeout: Session timeout duration in seconds (default: 3600)
        max_login_attempts: Maximum failed login attempts before lockout (default: 5)

    Usage Example:
        >>> auth_service = UserAuthenticationService(db_session)
        >>> user = auth_service.login("user@example.com", "password123")
        >>> if user:
        >>>     session_token = auth_service.create_session(user)

    Related Files:
        - modules/auth/user_model.py: User data model
        - modules/auth/password_utils.py: Password hashing utilities
        - modules/database/session_manager.py: Database session management

    Security Considerations:
        - Passwords are never stored in plaintext
        - Failed login attempts are logged and rate-limited
        - Sessions expire after inactivity timeout
        - All database queries use parameterized statements
    """
```

### Required for Every Function

```python
def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password against security strength requirements.

    This function checks if a password meets the minimum security standards
    required by the system. It enforces length, complexity, and common password
    blacklist requirements.

    Password Requirements:
        - Minimum 12 characters in length
        - At least one uppercase letter (A-Z)
        - At least one lowercase letter (a-z)
        - At least one digit (0-9)
        - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
        - Not in common password blacklist

    Args:
        password (str): The password string to validate. Can contain any printable
            characters including spaces. Length is checked before complexity.

    Returns:
        tuple[bool, str]: A tuple containing:
            - bool: True if password is valid, False otherwise
            - str: Empty string if valid, or specific error message if invalid
                  Example errors:
                  - "Password must be at least 12 characters"
                  - "Password must contain at least one uppercase letter"
                  - "Password is too common and easily guessable"

    Raises:
        TypeError: If password is not a string
        ValueError: If password is None

    Examples:
        >>> validate_password_strength("short")
        (False, "Password must be at least 12 characters")

        >>> validate_password_strength("SecureP@ssw0rd123")
        (True, "")

        >>> validate_password_strength("password123456")
        (False, "Password is too common and easily guessable")

    Security Notes:
        - This validation runs on both client-side and server-side
        - Blacklist contains top 10,000 most common passwords
        - Password strength meter UI uses same logic for consistency

    Related Functions:
        - hash_password(): Hashes validated passwords using bcrypt
        - check_common_passwords(): Checks against password blacklist

    Data Processed:
        - Input: Raw password string (user-provided, potentially unsafe)
        - Output: Validation status (safe for logging) and error message
        - No passwords are logged or stored by this function

    Performance:
        - Average execution time: <5ms
        - Blacklist lookup: O(1) using set data structure
    """
```

### Inline Comments for Complex Logic

```python
def calculate_job_match_score(job_data: dict, user_profile: dict) -> float:
    """Calculate compatibility score between job and user profile."""

    # Initialize weighted scoring components
    # Weights determined by A/B testing (see docs/decisions/003-job-matching-weights.md)
    skill_weight = 0.40    # Skills match is most important
    location_weight = 0.20 # Location preference
    salary_weight = 0.20   # Salary expectations
    culture_weight = 0.20  # Company culture fit

    # Extract and normalize skills for comparison
    # Skills stored as lowercase to handle case-insensitive matching
    job_skills = {skill.lower() for skill in job_data.get('required_skills', [])}
    user_skills = {skill.lower() for skill in user_profile.get('skills', [])}

    # Calculate skill overlap using Jaccard similarity
    # Jaccard = |intersection| / |union|
    # Example: {python, sql} ∩ {python, java, sql} = {python, sql}
    #          {python, sql} ∪ {python, java, sql} = {python, java, sql}
    #          Jaccard = 2/3 = 0.67
    if job_skills and user_skills:
        intersection = len(job_skills & user_skills)
        union = len(job_skills | user_skills)
        skill_score = intersection / union if union > 0 else 0.0
    else:
        skill_score = 0.0

    # Location scoring uses geographical distance
    # Remote jobs get automatic 1.0 score
    # Within 25 miles: 1.0, 25-50 miles: 0.7, 50-100 miles: 0.4, >100 miles: 0.0
    if job_data.get('remote', False):
        location_score = 1.0
    else:
        distance_miles = calculate_distance(
            job_data['location'],
            user_profile['preferred_location']
        )
        location_score = calculate_location_score(distance_miles)

    # Salary scoring compares job offer to user expectations
    # Score decreases linearly if offer is below expectations
    # Capped at 1.0 if offer exceeds expectations
    job_salary = job_data.get('salary_max', 0)
    expected_salary = user_profile.get('desired_salary', 0)

    if expected_salary > 0:
        salary_score = min(1.0, job_salary / expected_salary)
    else:
        salary_score = 0.5  # Neutral score if no expectation set

    # Culture fit based on company values alignment
    # Uses cosine similarity on value embeddings (see culture_matcher.py)
    culture_score = calculate_culture_fit(
        job_data.get('company_values', []),
        user_profile.get('preferred_values', [])
    )

    # Calculate weighted final score
    # Score is 0.0-1.0, where 1.0 is perfect match
    final_score = (
        skill_score * skill_weight +
        location_score * location_weight +
        salary_score * salary_weight +
        culture_score * culture_weight
    )

    return round(final_score, 2)  # Round to 2 decimal places for consistency
```

## Component Documentation

### Required Directory Structure

```
/docs/component_docs/
├── [module-name]/
│   ├── [feature-name].md           # Main documentation
│   ├── architecture.md             # Architecture overview (optional)
│   ├── api.md                      # API documentation (if applicable)
│   └── examples.md                 # Usage examples (optional)
```

**Examples:**
```
/docs/component_docs/
├── authentication/
│   ├── auth_system.md              # Main auth documentation
│   ├── oauth_flow.md               # OAuth implementation details
│   └── password_security.md        # Password handling
├── database/
│   ├── database_schema.md          # Auto-generated schema docs
│   └── database_schema_automation.md
├── email_integration/
│   ├── gmail_oauth_integration.md
│   └── email_sending_flow.md
└── job_matching/
    ├── scoring_algorithm.md
    └── ml_model_integration.md
```

### Component Documentation Template

```markdown
# [Feature Name] Documentation

**Status:** [Development/Testing/Production]
**Last Updated:** [Date]
**Version:** [Version Number]
**Author:** AI Assistant (Claude Code)

## Overview

[2-3 paragraph high-level description of what this component does and why it exists]

**Purpose:** [One sentence purpose statement]

**Key Functionality:**
- [Primary function 1]
- [Primary function 2]
- [Primary function 3]

## Architecture

### System Context

[Explain how this component fits into the larger system]

**Dependencies (Upstream):**
- `module/file.py` - [Why this is needed]
- `external_library` - [Purpose and version]

**Dependents (Downstream):**
- `module/other_file.py` - [What uses this component]
- `another_module/` - [How it's used]

### Component Diagram

```
[Optional: ASCII diagram or reference to architecture diagram]

User Request
    ↓
[This Component]
    ├─→ Database
    ├─→ External API
    └─→ Other Module
```

## Implementation Files

### Core Files

**`path/to/main_file.py`**
- **Purpose:** [What this file does]
- **Key Classes/Functions:**
  - `ClassName` - [What it does]
  - `function_name()` - [What it does]
- **Database Tables:** [Tables it interacts with]
- **External APIs:** [APIs it calls]

**`path/to/helper_file.py`**
- **Purpose:** [What this file does]
- **Key Utilities:**
  - `utility_function()` - [What it does]

### Supporting Files

**`path/to/config.py`**
- Configuration settings and constants

**`path/to/models.py`**
- Data models and schemas

### Test Files

**`tests/test_main_file.py`**
- Unit tests for main functionality
- Coverage: [X]%

## Data Flow

### Input Data

**Data Sources:**
1. [Source 1] - [Format and structure]
2. [Source 2] - [Format and structure]

**Data Format:**
```json
{
  "field_name": "description and type",
  "example": "actual example value"
}
```

**Validation:**
- [Validation rule 1]
- [Validation rule 2]

### Processing

**Steps:**
1. **[Step Name]:** [What happens in this step]
   - Input: [What data comes in]
   - Processing: [What transformation occurs]
   - Output: [What data goes out]

2. **[Step Name]:** [What happens]
   - Input: [Data]
   - Processing: [Logic]
   - Output: [Result]

### Output Data

**Data Destinations:**
1. [Destination 1] - [Format]
2. [Destination 2] - [Format]

**Output Format:**
```json
{
  "result_field": "description and type",
  "example": "actual example value"
}
```

## Database Interactions

### Tables Used

**`table_name`**
- **Operations:** Read / Write / Update / Delete
- **Columns Accessed:** `column1`, `column2`, `column3`
- **Indexes Used:** `index_name` (for performance)
- **Foreign Keys:** Relationships to other tables

**`another_table`**
- **Operations:** Read only
- **Joins:** Joined with `table_name` on `common_column`

### Query Patterns

```sql
-- Example query showing typical database interaction
SELECT column1, column2
FROM table_name
WHERE condition = value
ORDER BY column1;
```

**Performance Considerations:**
- [Index usage]
- [Query optimization notes]
- [Expected query volume]

## API Endpoints (if applicable)

### `POST /api/endpoint-name`

**Purpose:** [What this endpoint does]

**Authentication:** [Required/Optional, type]

**Request:**
```json
{
  "field": "value",
  "example": "data"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {}
}
```

**Error Responses:**
- `400 Bad Request` - [When this occurs]
- `401 Unauthorized` - [When this occurs]
- `500 Internal Server Error` - [When this occurs]

## Configuration

### Environment Variables

**Required:**
- `ENV_VAR_NAME` - [Description, default value if any]
- `ANOTHER_VAR` - [Description]

**Optional:**
- `OPTIONAL_VAR` - [Description, default behavior]

### Configuration Files

**`config/settings.json`**
```json
{
  "setting_name": "value",
  "description": "what this controls"
}
```

## Error Handling

### Common Errors

**Error Type 1: `SpecificException`**
- **Cause:** [What causes this error]
- **Impact:** [What happens when it occurs]
- **Resolution:** [How to fix it]
- **Logged:** [What is logged]

**Error Type 2: `AnotherException`**
- **Cause:** [What causes this]
- **Impact:** [Effect on system]
- **Resolution:** [Fix steps]

### Retry Logic

[If applicable, explain retry mechanisms]

## Security Considerations

- **Authentication:** [How authentication is handled]
- **Authorization:** [Permission requirements]
- **Data Protection:** [How sensitive data is protected]
- **Input Validation:** [How inputs are validated]
- **SQL Injection Protection:** [Parameterized queries, ORM usage]
- **Rate Limiting:** [If applicable]

## Performance

**Expected Performance:**
- Average response time: [X ms]
- Throughput: [Y requests/second]
- Database query time: [Z ms]

**Optimization Techniques:**
- [Caching strategy]
- [Index usage]
- [Batch processing]

**Monitoring:**
- Metrics tracked: [List metrics]
- Alert thresholds: [When alerts trigger]

## Testing

### Test Coverage

- Unit tests: `tests/test_file.py` - [X]% coverage
- Integration tests: `tests/integration/test_file.py`
- End-to-end tests: [If applicable]

### Running Tests

```bash
# Run unit tests
pytest tests/test_file.py

# Run with coverage
pytest --cov=module_name tests/

# Run integration tests
pytest tests/integration/
```

### Test Data

[Description of test data requirements and fixtures]

## Usage Examples

### Basic Usage

```python
# Example 1: Basic usage pattern
from module_name import ComponentClass

component = ComponentClass()
result = component.do_something(input_data)
```

### Advanced Usage

```python
# Example 2: Advanced usage with error handling
try:
    component = ComponentClass(config_options)
    result = component.complex_operation(
        param1="value1",
        param2="value2"
    )
    process_result(result)
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    handle_error(e)
```

## Integration Points

### Upstream Integrations

**[System/Module Name]**
- **Integration Type:** [API call, database read, file import, etc.]
- **Data Received:** [What data flows in]
- **Frequency:** [How often]

### Downstream Integrations

**[System/Module Name]**
- **Integration Type:** [How data is sent]
- **Data Sent:** [What data flows out]
- **Frequency:** [How often]

## Troubleshooting

### Problem: [Common Issue 1]

**Symptoms:**
- [Observable symptom 1]
- [Observable symptom 2]

**Diagnosis:**
1. Check [specific log file or metric]
2. Verify [configuration or state]

**Solution:**
[Step-by-step fix]

### Problem: [Common Issue 2]

**Symptoms:**
- [What you'll see]

**Diagnosis:**
[How to identify]

**Solution:**
[How to fix]

## Future Enhancements

[Optional: Document planned improvements or known limitations]

## Related Documentation

- [/docs/component_docs/related/file.md](link) - [Description]
- [/docs/api/endpoints.md](link) - [Description]
- [/docs/decisions/XXX-decision-name.md](link) - [Related architectural decision]

## Changelog

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-06 | Initial implementation | AI Assistant |

---

**Document Owner:** Development Team
**Last Reviewed:** 2025-10-06
**Next Review:** After major changes or 3 months
```

## When to Create Component Documentation

**Create component documentation when:**
- Implementing a new module or feature
- Creating a new integration point
- Building a reusable service or utility
- Implementing complex business logic
- Creating public APIs or interfaces

**Update component documentation when:**
- Modifying data flow or architecture
- Changing API contracts or interfaces
- Adding or removing database tables
- Updating configuration requirements
- Fixing significant bugs that change behavior

## Documentation Task Requirements

### In Task Lists

Every task list should include documentation tasks:

```markdown
- [ ] 5.0 Documentation
  - [ ] 5.1 Add comprehensive inline documentation to all new files
  - [ ] 5.2 Create component documentation in /docs/component_docs/[module]/
  - [ ] 5.3 Document data flow and integration points
  - [ ] 5.4 Add API documentation (if applicable)
  - [ ] 5.5 Update related documentation for modified files
  - [ ] 5.6 Review documentation for accuracy and completeness
```

### Before Marking Parent Task Complete

**Documentation checklist:**
- [ ] Every new file has file-level docstring
- [ ] Every class has comprehensive docstring
- [ ] Every function has docstring with args, returns, examples
- [ ] Complex logic has inline comments explaining "why"
- [ ] Component documentation created in `/docs/component_docs/[module]/`
- [ ] Component documentation covers: purpose, architecture, data flow, APIs, database interactions
- [ ] Related documentation updated (if modifying existing features)

## Integration with Task Execution

See [Task Execution Guide](./task-execution-guide.md) for how documentation tasks fit into the execution workflow.

**Key principle:** Documentation is part of implementation, not a separate phase.

---

**Document Owner:** Development Team
**Related Guides:**
- [Task Execution Guide](./task-execution-guide.md)
- [Task Generation Guide](./task-generation-guide.md)
- [CLAUDE.md](../../CLAUDE.md) - Project documentation standards

**Last Reviewed:** October 6, 2025
