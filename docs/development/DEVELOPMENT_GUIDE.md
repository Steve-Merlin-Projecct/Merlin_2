# Development Guide

**Version**: 2.16.8  
**Date**: July 30, 2025  
**For**: Developers, Contributors, System Integrators

## Quick Start

### Environment Setup
```bash
# Clone and setup
git clone <repository-url>
cd automated-job-application-system

# Install dependencies (handled automatically by Replit)
# Dependencies are managed via uv and defined in pyproject.toml

# Set environment variables
export DATABASE_URL="postgresql://user:pass@host:port/db"
export WEBHOOK_API_KEY="<64-character-secure-key>"
export GOOGLE_GEMINI_API_KEY="<your-gemini-key>"
export LINK_TRACKING_API_KEY="<64-character-secure-key>"

# Run application
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### Development Workflow
```bash
# Start development server
make dev-start

# Run security tests
python test_end_to_end_security_assessment.py

# Update database schema documentation
make db-update

# Run specific component tests
python test_link_tracking_security.py
```

## Code Organization

### Module Structure
```
modules/
├── ai_job_description_analysis/    # AI processing and analysis
├── database/                       # Database management and operations
├── document_generation/            # Template-based document creation
├── email_integration/              # Gmail OAuth and email automation
├── link_tracking/                  # Link analytics with security
├── resilience/                     # Failure recovery and retry logic
├── scraping/                       # Job scraping and data pipeline
├── security/                       # Security patches and configuration
└── workflow/                       # End-to-end workflow orchestration
```

### Key Files
```
├── app_modular.py          # Main Flask application with blueprints
├── main.py                 # Application entry point
├── replit.md               # Project documentation and preferences
├── pyproject.toml          # Python dependencies and configuration
└── .env                    # Environment variables (local development)
```

## Coding Standards

**📚 Complete Standards Documentation:** See [Coding Standards](CODING_STANDARDS.md) for comprehensive guidelines

**🔧 Automated Tooling:** See [Automated Tooling Guide](AUTOMATED_TOOLING_GUIDE.md) for tool configuration

**📋 Code Review Process:** See [Code Review Decision Guide](CODE_REVIEW_DECISION_GUIDE.md) for review frameworks

### Quick Reference - Python Code Style
```python
# Use descriptive variable names
user_preference_package = load_steve_glen_preferences()

# Comprehensive error handling
try:
    result = api_call()
except APIException as e:
    logger.error(f"API call failed: {e}")
    return {'error': 'Service temporarily unavailable'}, 503

# Security-first approach
@require_api_key
@rate_limit(limit=50, window=3600)
def secure_endpoint():
    # Validate all inputs
    valid, error = security.validate_input(request.json)
    if not valid:
        return {'error': f'Validation failed: {error}'}, 400
```

### Automated Code Quality Tools
```bash
# Format code with Black (120 character line length)
black .

# Lint with Flake8
flake8

# Check for dead code with Vulture
vulture --min-confidence 80

# All tools are configured in project root:
# .black.toml, .flake8, .vulture.toml
```

### Security Guidelines
```python
# Always use parameterized queries
cursor.execute("""
    SELECT id, title FROM jobs 
    WHERE company_id = %s AND status = %s
""", (company_id, 'active'))

# Validate all user inputs
def create_link(data):
    # Validate URL
    valid, error = security_controls.validate_url(data.get('url'))
    if not valid:
        return {'error': f'Invalid URL: {error}'}, 400
    
    # Sanitize inputs
    sanitized_data = {
        'url': security_controls.sanitize_input(data['url']),
        'function': security_controls.validate_link_function(data['function'])
    }
```

### Database Operations
```python
# Use the unified database manager
from modules.database.database_manager import DatabaseManager

db = DatabaseManager()

# Read operations
jobs = db.reader.get_jobs_by_status('active')

# Write operations  
job_id = db.writer.create_job({
    'title': 'Software Engineer',
    'company_id': company_uuid,
    'status': 'pending'
})

# Always handle transactions
try:
    with db.get_session() as session:
        # Multiple operations
        session.commit()
except Exception as e:
    session.rollback()
    raise
```

## Development Patterns

### Blueprint Registration
```python
# In main module file (e.g., link_tracking_api.py)
from flask import Blueprint

component_bp = Blueprint('component', __name__, url_prefix='/api/component')

@component_bp.route('/endpoint', methods=['POST'])
@require_api_key
@rate_limit(limit=50, window=3600)
def secure_endpoint():
    # Implementation
    pass

# In app_modular.py
from modules.component.api import component_bp
app.register_blueprint(component_bp)
```

### Security Integration
```python
# Import security controls
from modules.link_tracking.security_controls import SecurityControls, require_api_key, rate_limit

# Apply security decorators
@require_api_key
@rate_limit(limit=100, window=3600)
def protected_endpoint():
    # Validate inputs
    security = SecurityControls()
    valid, error = security.validate_input(request.json)
    
    # Log security events
    security.log_security_event('API_ACCESS', {
        'endpoint': request.endpoint,
        'ip': request.remote_addr
    }, 'INFO')
```

### Error Handling Pattern
```python
def api_endpoint():
    try:
        # Business logic
        result = process_request(request.json)
        return {'status': 'success', 'data': result}, 200
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return {'error': 'Invalid input data'}, 400
        
    except AuthenticationError as e:
        logger.warning(f"Auth error: {e}")
        return {'error': 'Authentication required'}, 401
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {'error': 'Internal server error'}, 500
```

## Testing Guidelines

### Security Testing
```python
# Always test security controls
def test_authentication_required():
    response = client.post('/api/secure-endpoint', json={})
    assert response.status_code == 401
    
def test_input_validation():
    malicious_input = "<script>alert('xss')</script>"
    response = client.post('/api/endpoint', json={'data': malicious_input})
    assert response.status_code == 400
```

### Component Testing
```python
# Test component functionality
def test_document_generation():
    generator = DocumentGenerator()
    result = generator.generate_document({
        'template': 'resume',
        'data': test_data
    })
    assert result['status'] == 'success'
    assert 'file_path' in result
```

### Integration Testing
```python
# Test end-to-end workflows
def test_complete_application_workflow():
    # Create job
    job = create_test_job()
    
    # Analyze with AI
    analysis = ai_analyzer.analyze_job(job)
    
    # Generate documents
    documents = document_generator.generate_for_job(job, analysis)
    
    # Send application
    result = email_sender.send_application(job, documents)
    
    assert result['status'] == 'sent'
```

## Database Development

### Schema Changes
```bash
# NEVER manually edit auto-generated files
# Instead, make changes to the database and run automation

# Make database schema changes
psql -d $DATABASE_URL -c "ALTER TABLE jobs ADD COLUMN new_field TEXT;"

# Update documentation automatically
python database_tools/update_schema.py

# Commit changes
git add .
git commit -m "Add new_field to jobs table"
```

### Database Operations
```python
# Use database manager for all operations
from modules.database.database_manager import DatabaseManager

db = DatabaseManager()

# Create operations
job_id = db.writer.create_job({
    'title': 'Software Engineer',
    'company_id': uuid.uuid4(),
    'salary_min': 75000,
    'salary_max': 95000
})

# Read operations with relationships
job_with_company = db.reader.get_job_with_company(job_id)

# Update operations
db.writer.update_job_status(job_id, 'analyzed')
```

## Security Development

### Authentication Implementation
```python
# Implement new authenticated endpoint
@require_api_key
def new_secure_endpoint():
    # Endpoint automatically protected
    pass

# Custom authentication check
def custom_auth_endpoint():
    if not validate_custom_auth():
        return {'error': 'Custom auth required'}, 401
```

### Input Validation
```python
# Use security controls for validation
from modules.link_tracking.security_controls import SecurityControls

security = SecurityControls()

# Validate different input types
valid_url, error = security.validate_url(user_url)
valid_id, error = security.validate_tracking_id(tracking_id)
sanitized = security.sanitize_input(user_input, max_length=500)
```

### Security Event Logging
```python
# Log security events appropriately
security.log_security_event('USER_LOGIN', {
    'user_id': user_id,
    'ip': request.remote_addr,
    'success': True
}, 'INFO')

security.log_security_event('SUSPICIOUS_ACTIVITY', {
    'pattern': 'multiple_failed_logins',
    'ip': request.remote_addr,
    'count': failed_attempts
}, 'WARNING')
```

## Performance Guidelines

### Database Optimization
```python
# Use proper indexing queries
# These fields are already indexed for performance:
# - jobs.title, jobs.company_id, jobs.created_at
# - companies.name, link_tracking.tracking_id
# - cleaned_job_scrapes.job_title, cleaned_job_scrapes.company_name

# Query with indexed fields
jobs = db.reader.get_jobs_by_title_pattern('engineer')  # Uses title index
recent_jobs = db.reader.get_recent_jobs()  # Uses created_at index
```

### Caching Patterns
```python
# Use in-memory caching for expensive operations
from functools import lru_cache

@lru_cache(maxsize=100)
def get_user_preferences(user_id):
    # Expensive database operation
    return db.reader.get_user_preferences(user_id)

# Cache results for AI analysis
analysis_cache = {}
def cached_ai_analysis(job_text):
    cache_key = hashlib.md5(job_text.encode()).hexdigest()
    if cache_key not in analysis_cache:
        analysis_cache[cache_key] = ai_analyzer.analyze(job_text)
    return analysis_cache[cache_key]
```

## API Development

### REST API Patterns
```python
# Follow consistent API patterns
@blueprint.route('/resource', methods=['GET'])
def list_resources():
    return {'resources': data, 'total': count}, 200

@blueprint.route('/resource', methods=['POST'])
def create_resource():
    return {'resource': created_data, 'id': new_id}, 201

@blueprint.route('/resource/<id>', methods=['GET'])
def get_resource(id):
    return {'resource': data}, 200

@blueprint.route('/resource/<id>', methods=['PUT'])
def update_resource(id):
    return {'resource': updated_data}, 200

@blueprint.route('/resource/<id>', methods=['DELETE'])
def delete_resource(id):
    return {'message': 'Resource deleted'}, 200
```

### API Documentation
```python
# Document all endpoints with docstrings
@blueprint.route('/api/jobs/<job_id>/analyze', methods=['POST'])
@require_api_key
@rate_limit(limit=20, window=3600)
def analyze_job(job_id):
    """
    Analyze a job posting using AI.
    
    Args:
        job_id (str): UUID of the job to analyze
        
    POST Body:
        {
            "analysis_type": "comprehensive",
            "include_ats": true
        }
        
    Returns:
        {
            "analysis": {
                "skills": [...],
                "authenticity": 0.95,
                "ats_keywords": [...]
            },
            "status": "completed"
        }
        
    Status Codes:
        200: Analysis completed successfully
        400: Invalid job ID or request data
        401: Authentication required
        429: Rate limit exceeded
        500: Internal server error
    """
```

## Deployment Guidelines

### Environment Configuration
```bash
# Production environment variables
export FLASK_ENV=production
export DATABASE_URL="postgresql://user:pass@production-host/db"
export WEBHOOK_API_KEY="<64-character-production-key>"
export LINK_TRACKING_API_KEY="<64-character-production-key>"
export GOOGLE_GEMINI_API_KEY="<production-gemini-key>"

# Security configuration
export SECURITY_LOG_LEVEL="WARNING"
export RATE_LIMIT_STORAGE="redis://production-redis:6379"
```

### Production Checklist
```bash
# Pre-deployment checklist
□ All environment variables set with production values
□ Database migrations completed
□ Security assessment passed (7.5/10+ rating)
□ All tests passing including security tests
□ Documentation updated and current
□ Monitoring and alerting configured
□ Backup procedures verified
□ SSL certificates installed and valid
```

## Troubleshooting

### Common Issues

**Database Schema Out of Sync**
```bash
# Fix with automated tools
python database_tools/update_schema.py
git add .
git commit -m "Update database schema documentation"
```

**Security Test Failures**
```bash
# Check API keys are properly set
echo $WEBHOOK_API_KEY | wc -c  # Should be 64+ characters
echo $LINK_TRACKING_API_KEY | wc -c  # Should be 64+ characters

# Run security tests individually
python -m pytest test_link_tracking_security.py -v
```

**Import Errors**
```bash
# Verify module structure
python -c "from modules.link_tracking.security_controls import SecurityControls"

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database Connection Issues**
```bash
# Test database connection
python -c "
import os
import psycopg2
conn = psycopg2.connect(os.environ['DATABASE_URL'])
print('Database connected successfully')
conn.close()
"
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable Flask debug mode (development only)
app.debug = True

# Component-specific debug logging
logging.getLogger('modules.link_tracking').setLevel(logging.DEBUG)
```

## Contributing Guidelines

### Code Review Process

**📋 Complete Review Guide:** See [Code Review Decision Guide](CODE_REVIEW_DECISION_GUIDE.md) for detailed framework

**Quick Checklist:**
1. **Security Review**: All changes involving security controls require security review
2. **Code Quality**: All code must pass Black formatting and Flake8 linting
3. **Database Changes**: Schema changes must include automated documentation updates
4. **API Changes**: New endpoints must include comprehensive documentation
5. **Testing**: All changes must include appropriate test coverage
6. **Documentation**: Follow [Coding Standards](CODING_STANDARDS.md) for documentation requirements

### Git Workflow
```bash
# Feature development
git checkout -b feature/new-feature
# Make changes
git add .
git commit -m "Add new feature with security controls"

# Schema changes trigger automatic documentation
# This is handled by pre-commit hooks

git push origin feature/new-feature
# Create pull request
```

### Documentation Requirements
- All new modules must include comprehensive docstrings
- API endpoints must include usage examples
- Security features must include threat model documentation
- Database changes must include relationship documentation

---

This development guide provides the foundation for maintaining and extending the automated job application system while preserving its security-first architecture and comprehensive functionality.