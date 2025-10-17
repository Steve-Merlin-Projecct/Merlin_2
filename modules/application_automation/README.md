# Application Automation Module

## Overview

The Application Automation module provides automated job application form filling using Apify Actors and Playwright. This MVP version supports Indeed application forms with plans to expand to other platforms (Greenhouse, Lever, Workday, etc.).

**Version:** 1.0.0 (MVP)
**Platform Support:** Indeed only
**Workflow:** Auto-submit with post-review

## Architecture

### Components

```
application_automation/
├── actor_main.py           # Apify Actor entry point
├── form_filler.py          # Core Playwright automation logic
├── data_fetcher.py         # Fetch application data from Flask API
├── screenshot_manager.py   # Screenshot capture and storage
├── automation_api.py       # Flask API endpoints
├── models.py              # Database models
├── form_mappings/         # Pre-mapped form selectors
│   └── indeed.json        # Indeed form mappings
├── tests/                 # Test suite
└── README.md              # This file
```

### Workflow

1. **Trigger**: Flask API receives request to automate application
2. **Actor Start**: Apify Actor is triggered with job and application IDs
3. **Data Fetch**: Actor fetches applicant profile, job details, and documents from Flask API
4. **Form Fill**: Actor navigates to application URL and fills form using pre-mapped selectors
5. **Screenshot**: Captures before/after screenshots for review
6. **Submit**: Auto-submits the application form
7. **Verify**: Checks for submission confirmation
8. **Report**: Sends results back to Flask API for storage
9. **Review**: User reviews screenshots and confirms submission

## Features

### MVP Features (v1.0.0)
- ✅ Indeed application form automation (standard and quick apply)
- ✅ Pre-mapped form selectors for reliable field detection
- ✅ Secure API communication with Flask backend
- ✅ Screenshot capture before/after submission
- ✅ Auto-submit with post-review workflow
- ✅ Comprehensive error handling and logging
- ✅ Database tracking of all submission attempts
- ✅ Integration with existing storage backend

### Future Enhancements
- 🔲 Hybrid detection (pre-mapped + AI fallback using GPT-4 Vision)
- 🔲 Support for additional platforms (Greenhouse, Lever, Workday)
- 🔲 Multi-page application form navigation
- 🔲 Custom screening questions handling
- 🔲 Dynamic selector learning from successful applications
- 🔲 Pre-submit confirmation workflow option

## Installation

### 1. Install Dependencies

```bash
# From project root
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Database Setup

Run the SQL migration to create the `application_submissions` table:

```bash
# Using psql
psql -U your_user -d your_database -f modules/application_automation/models.py

# Or using database tools
python database_tools/run_migration.py
```

### 3. Environment Variables

Add to your `.env` file:

```bash
# Apify Configuration
APIFY_TOKEN=your_apify_token_here
APPLICATION_AUTOMATION_ACTOR_ID=your-username/application-automation

# Flask API (for Actor)
FLASK_API_URL=https://your-api-domain.com
WEBHOOK_API_KEY=your_api_key_here

# Storage Backend (already configured)
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./storage/generated_documents
```

### 4. Register Blueprint

Add to `app_modular.py`:

```python
from modules.application_automation.automation_api import automation_api

app.register_blueprint(automation_api)
```

### 5. Deploy Apify Actor

```bash
# From the application_automation directory
cd modules/application_automation

# Create Apify project structure
mkdir .actor
echo '{"actorSpecification": 1, "name": "application-automation"}' > .actor/actor.json

# Create Dockerfile
cat > .actor/Dockerfile <<EOF
FROM apify/actor-python:3.11
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps
COPY . ./
CMD ["python", "actor_main.py"]
EOF

# Deploy to Apify
apify login
apify push
```

## Usage

### Trigger Application Automation

```bash
curl -X POST https://your-api.com/api/application-automation/trigger \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "job_12345",
    "application_id": "app_67890"
  }'
```

Response:
```json
{
  "success": true,
  "actor_run_id": "run_xyz123",
  "actor_status": "RUNNING",
  "submission_id": "uuid-here",
  "message": "Application automation started"
}
```

### List Submissions

```bash
curl -X GET "https://your-api.com/api/application-automation/submissions?status=submitted&limit=10" \
  -H "X-API-Key: your_api_key"
```

### Get Submission Details

```bash
curl -X GET https://your-api.com/api/application-automation/submissions/uuid-here \
  -H "X-API-Key: your_api_key"
```

### Mark as Reviewed

```bash
curl -X PUT https://your-api.com/api/application-automation/submissions/uuid-here/review \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "reviewed_by": "user_123",
    "review_notes": "Verified submission successful"
  }'
```

### Get Statistics

```bash
curl -X GET https://your-api.com/api/application-automation/stats \
  -H "X-API-Key: your_api_key"
```

## API Endpoints

### POST `/api/application-automation/trigger`
Trigger Apify Actor to automate a job application.

**Request Body:**
```json
{
  "job_id": "string",
  "application_id": "string"
}
```

**Response:**
```json
{
  "success": true,
  "actor_run_id": "string",
  "actor_status": "string",
  "submission_id": "string",
  "message": "string"
}
```

### POST `/api/application-automation/submissions`
Record submission result from Apify Actor (called by Actor).

**Request Body:**
```json
{
  "application_id": "string",
  "job_id": "string",
  "status": "submitted|failed",
  "form_platform": "indeed",
  "form_type": "string",
  "fields_filled": ["string"],
  "submission_confirmed": boolean,
  "confirmation_message": "string",
  "screenshots": [{"filename": "string", "url": "string"}],
  "error_message": "string",
  "error_details": {}
}
```

### GET `/api/application-automation/submissions/<submission_id>`
Get submission details by ID.

### GET `/api/application-automation/submissions?status=&job_id=&limit=`
List submissions with optional filters.

### PUT `/api/application-automation/submissions/<submission_id>/review`
Mark submission as reviewed.

**Request Body:**
```json
{
  "reviewed_by": "string",
  "review_notes": "string"
}
```

### GET `/api/application-automation/stats`
Get automation statistics for the last 30 days.

## Form Mappings

Form mappings are defined in JSON files under `form_mappings/`. Each mapping contains:

- **Platform**: Platform identifier (e.g., "indeed")
- **Form Types**: Different form variations (quick apply, standard)
- **Fields**: Form field definitions with multiple selector strategies
- **Submit Button**: Submit button selectors
- **Confirmation Indicators**: Success detection strategies

### Indeed Form Mapping

See `form_mappings/indeed.json` for the complete Indeed mapping. Key features:

- **Standard Indeed Apply**: Full form with name, email, phone, resume, cover letter
- **Quick Apply**: One-click apply with saved profile
- **Multiple Selectors**: Each field has multiple selector strategies for robustness
- **Validation**: Field validation patterns for data integrity

### Adding New Platform Mappings

To add support for a new platform:

1. Create `form_mappings/platform_name.json`
2. Define form types and field selectors
3. Add detection strategy
4. Update `form_filler.py` to support new platform
5. Test thoroughly

## Testing

### Local Testing (without Apify)

```python
import asyncio
from modules.application_automation import DataFetcher, FormFiller

async def test_automation():
    # Fetch data
    fetcher = DataFetcher(
        api_base_url="http://localhost:5000",
        api_key="your_test_key"
    )
    data = fetcher.fetch_application_data(
        job_id="test_job_123",
        application_id="test_app_456"
    )

    # Fill form
    filler = FormFiller(headless=False)  # headless=False for debugging
    result = await filler.fill_application_form(data, "test_app_456")

    print(f"Success: {result.success}")
    print(f"Fields filled: {result.fields_filled}")
    print(f"Screenshots: {len(result.screenshots)}")

asyncio.run(test_automation())
```

### Run Tests

```bash
# Run all tests
pytest modules/application_automation/tests/

# Run specific test
pytest modules/application_automation/tests/test_form_filler.py -v

# Run with coverage
pytest modules/application_automation/tests/ --cov=modules/application_automation
```

## Security

### API Authentication
- All endpoints require `X-API-Key` header
- API key validated against `WEBHOOK_API_KEY` environment variable
- Rate limiting applied (inherited from Flask rate limiter)

### Data Security
- No sensitive data logged (PII filtered)
- Screenshots stored using secure storage backend
- API communication over HTTPS only
- Apify Secrets used for sensitive configuration

### Browser Security
- User agent randomization
- Proxy support (via Apify)
- Headless mode for production
- Automatic cleanup of temp files

## Troubleshooting

### Actor Fails to Start
- Check `APIFY_TOKEN` is valid
- Verify `APPLICATION_AUTOMATION_ACTOR_ID` is correct
- Ensure Actor is deployed and published

### Form Field Not Found
- Check form mappings in `form_mappings/indeed.json`
- Run with `headless=False` to debug visually
- Check browser console for errors
- Verify Indeed hasn't changed their form structure

### Screenshots Not Saved
- Check storage backend configuration
- Verify write permissions
- Check storage backend logs
- Ensure storage backend is initialized

### Submission Not Confirmed
- Check confirmation indicators in form mappings
- Verify network didn't timeout
- Check for CAPTCHA or manual verification required
- Review post-submit screenshot

## Monitoring

### Key Metrics
- **Success Rate**: Percentage of successful submissions
- **Confirmation Rate**: Percentage of confirmed submissions
- **Error Types**: Common error patterns
- **Average Time**: Time per application
- **Screenshot Count**: Average screenshots per submission

### Logging
- All operations logged with context
- Errors include stack traces
- API calls logged with timing
- Apify Actor logs available in Apify console

### Alerts
Set up alerts for:
- Actor failures
- Low success rate (<80%)
- High error rate (>20%)
- API authentication failures

## Limitations (MVP)

1. **Platform Support**: Indeed only (MVP constraint)
2. **Form Detection**: Pre-mapped selectors only (no AI fallback yet)
3. **Screening Questions**: Not supported (simple forms only)
4. **Multi-Page Forms**: Limited support
5. **CAPTCHA**: Manual intervention required
6. **Rate Limiting**: Subject to Indeed's rate limits

## Roadmap

### v1.1 (Next Release)
- Multi-page form support
- Screening questions handling
- Improved error recovery
- Form field validation
- Pre-submit screenshot review option

### v2.0 (Future)
- Hybrid detection (pre-mapped + AI fallback)
- GPT-4 Vision for dynamic form detection
- Support for Greenhouse, Lever, Workday
- Advanced CAPTCHA handling
- Dynamic selector learning

### v3.0 (Long Term)
- Custom question answering using AI
- Resume tailoring per application
- Cover letter customization
- Application tracking and analytics
- Multi-platform batch applications

## Support

For issues, questions, or feature requests:
1. Check this README
2. Review logs in Apify console
3. Check Flask API logs
4. Review screenshot evidence
5. Create detailed bug report with logs

## Contributing

When adding new features:
1. Update form mappings if needed
2. Add comprehensive tests
3. Update this README
4. Add inline documentation
5. Test locally before deploying
6. Update API documentation

## License

Internal use only - Part of Merlin Job Application System v4.3.2
