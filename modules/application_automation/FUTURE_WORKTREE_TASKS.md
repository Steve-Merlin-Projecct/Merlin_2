---
title: "Future Worktree Tasks"
type: technical_doc
component: application_automation
status: draft
tags: []
---

# Future Worktree Tasks & Project Separation Plan
## Application Automation Module

**Last Updated:** 2025-10-14
**Current Status:** MVP Complete in monorepo
**Next Step:** Separate into standalone project

---

## Architecture Decision: API-Only Communication ✅

**Decision Made:** Actor communicates with database **ONLY through Flask API**

**Rationale:**
- ✅ Security: No database credentials in Actor
- ✅ Encapsulation: Database not exposed to internet
- ✅ Flexibility: Can change database without Actor changes
- ✅ Scalability: API can be load balanced, cached
- ✅ Auditability: All operations logged through API

**Current Implementation:** Already follows this pattern correctly.

---

## Phase 1: Project Separation (Next Worktree Cycle)

### Task 1.1: Create New GitHub Repository
**Priority:** High
**Effort:** 1 hour

**Steps:**
```bash
# 1. Create new repository
gh repo create apify-indeed-application-filler --public \
  --description "Automated Indeed job application form filling using Apify & Playwright" \
  --gitignore Python

# 2. Clone locally
cd ~/projects
git clone https://github.com/yourusername/apify-indeed-application-filler
cd apify-indeed-application-filler
```

**Deliverables:**
- [ ] New GitHub repository created
- [ ] Repository cloned locally
- [ ] Initial README.md added

---

### Task 1.2: Extract Actor Code from Monorepo
**Priority:** High
**Effort:** 2-3 hours

**Files to Copy:**

```bash
# From monorepo to new repo
cp -r modules/application_automation/actor_main.py ./src/main.py
cp -r modules/application_automation/form_filler.py ./src/
cp -r modules/application_automation/data_fetcher.py ./src/
cp -r modules/application_automation/screenshot_manager.py ./src/
cp -r modules/application_automation/form_mappings/ ./
cp -r modules/application_automation/.actor/ ./
cp -r modules/application_automation/tests/test_form_mappings.py ./tests/
cp -r modules/application_automation/tests/test_api_simple.py ./tests/
```

**Files to CREATE (Actor-Specific):**
- `src/__init__.py`
- `src/config.py` - Configuration management
- `src/exceptions.py` - Custom exceptions
- `src/utils.py` - Helper functions
- `README.md` - Actor-specific documentation
- `LICENSE` - MIT or appropriate license
- `.gitignore` - Python + Apify ignores
- `pyproject.toml` - Project metadata

**Files to EXCLUDE (Flask-Specific):**
- ❌ `automation_api.py` (Flask routes - stays in monorepo)
- ❌ `models.py` (SQLAlchemy models - stays in monorepo)
- ❌ `migrations/` (Database migrations - stays in monorepo)
- ❌ `tests/test_integration.py` (Flask integration tests - stays in monorepo)

**Deliverables:**
- [ ] Actor code extracted to new repo
- [ ] Directory structure optimized for standalone project
- [ ] Flask-specific code excluded

---

### Task 1.3: Configure Development Environment (Docker + VSCode)
**Priority:** High
**Effort:** 2-3 hours

**Goal:** Match current devcontainer setup from monorepo

#### Step 1: Create `.devcontainer/devcontainer.json`

```json
{
  "name": "Apify Indeed Application Filler",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/node:1": {
      "version": "18"
    }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "ms-python.flake8",
        "redhat.vscode-yaml",
        "eamodio.gitlens",
        "usernamehw.errorlens",
        "streetsidesoftware.code-spell-checker"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "python.linting.flake8Enabled": true,
        "python.formatting.provider": "black",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
          "source.organizeImports": true
        },
        "[python]": {
          "editor.defaultFormatter": "ms-python.black-formatter"
        }
      }
    }
  },
  "postCreateCommand": "pip install -r requirements.txt && playwright install chromium",
  "remoteUser": "vscode",
  "mounts": [
    "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
  ]
}
```

#### Step 2: Create `docker-compose.yml` (Optional - for local Apify testing)

```yaml
version: '3.8'

services:
  actor-dev:
    build:
      context: .
      dockerfile: .actor/Dockerfile
    environment:
      - FLASK_API_URL=${FLASK_API_URL:-http://host.docker.internal:5000}
      - WEBHOOK_API_KEY=${WEBHOOK_API_KEY}
      - APIFY_TOKEN=${APIFY_TOKEN}
    volumes:
      - ./src:/app/src
      - ./form_mappings:/app/form_mappings
      - ./tests:/app/tests
    command: python src/main.py
```

#### Step 3: Create `.actor/Dockerfile` (Apify-Optimized)

```dockerfile
FROM apify/actor-python:3.11

# Install Playwright and dependencies
RUN pip install playwright==1.48.0 && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src
COPY form_mappings ./form_mappings

# Set up Apify Actor entry point
CMD ["python", "-m", "src.main"]
```

#### Step 4: Create `requirements.txt`

```
# Core dependencies
apify>=2.0.0
playwright>=1.48.0
requests>=2.32.0
python-dotenv>=1.0.0

# Development dependencies
pytest>=8.4.0
pytest-asyncio>=0.23.0
black>=25.1.0
flake8>=7.3.0
mypy>=1.8.0
```

#### Step 5: Create `.env.example`

```bash
# Flask API Configuration
FLASK_API_URL=http://localhost:5000
WEBHOOK_API_KEY=your_api_key_here

# Apify Configuration (only needed for local testing)
APIFY_TOKEN=your_apify_token_here
```

**Deliverables:**
- [ ] `.devcontainer/` configured
- [ ] `docker-compose.yml` created
- [ ] `.actor/Dockerfile` optimized
- [ ] `requirements.txt` Actor-specific
- [ ] `.env.example` documented

---

### Task 1.4: Refactor Code for Standalone Project
**Priority:** High
**Effort:** 3-4 hours

**Changes Needed:**

#### 1. Update Import Paths

**Before (Monorepo):**
```python
from modules.application_automation.form_filler import FormFiller
from modules.application_automation.data_fetcher import FlaskAPIClient
```

**After (Standalone):**
```python
from src.form_filler import FormFiller
from src.data_fetcher import FlaskAPIClient
```

#### 2. Create `src/config.py`

```python
"""
Configuration Management for Apify Actor
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Flask API Configuration
    FLASK_API_URL: str = os.getenv("FLASK_API_URL", "http://localhost:5000")
    WEBHOOK_API_KEY: str = os.getenv("WEBHOOK_API_KEY", "")

    # Apify Configuration
    APIFY_TOKEN: Optional[str] = os.getenv("APIFY_TOKEN")

    # Actor Configuration
    SCREENSHOT_QUALITY: int = int(os.getenv("SCREENSHOT_QUALITY", "80"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT_MS: int = int(os.getenv("TIMEOUT_MS", "60000"))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.WEBHOOK_API_KEY:
            raise ValueError("WEBHOOK_API_KEY is required")
        if not cls.FLASK_API_URL:
            raise ValueError("FLASK_API_URL is required")


# Global config instance
config = Config()
```

#### 3. Update `src/main.py` (Actor Entry Point)

```python
"""
Apify Actor Entry Point - Indeed Application Automation
"""
import asyncio
from apify import Actor
from src.config import config
from src.form_filler import FormFiller
from src.data_fetcher import FlaskAPIClient
from src.screenshot_manager import ScreenshotManager


async def main():
    """
    Main Actor entry point
    """
    async with Actor:
        # Get Actor input
        actor_input = await Actor.get_input()

        # Validate configuration
        config.validate()

        # Log Actor start
        Actor.log.info(f"Starting Indeed application automation")
        Actor.log.info(f"Job ID: {actor_input.get('job_id')}")

        try:
            # Initialize components
            api_client = FlaskAPIClient(config.FLASK_API_URL, config.WEBHOOK_API_KEY)
            form_filler = FormFiller()
            screenshot_manager = ScreenshotManager()

            # Fetch application data
            job_data = await api_client.fetch_job_details(actor_input['job_id'])

            # Fill application form
            result = await form_filler.fill_application(job_data)

            # Report results back to Flask
            await api_client.report_submission(result)

            # Push data to Apify Dataset
            await Actor.push_data(result)

            Actor.log.info("Application completed successfully")

        except Exception as e:
            Actor.log.exception(f"Actor failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
```

#### 4. Create `src/exceptions.py`

```python
"""
Custom Exceptions for Application Automation
"""


class ApplicationAutomationError(Exception):
    """Base exception for application automation"""
    pass


class FormDetectionError(ApplicationAutomationError):
    """Failed to detect form fields"""
    pass


class FormFillError(ApplicationAutomationError):
    """Failed to fill form fields"""
    pass


class SubmissionError(ApplicationAutomationError):
    """Failed to submit application"""
    pass


class APIConnectionError(ApplicationAutomationError):
    """Failed to connect to Flask API"""
    pass
```

**Deliverables:**
- [ ] Import paths updated
- [ ] Configuration module created
- [ ] Actor entry point refactored
- [ ] Custom exceptions defined
- [ ] Code runs successfully in new repo

---

### Task 1.5: Update Documentation for Standalone Project
**Priority:** Medium
**Effort:** 2 hours

**Files to Update:**

#### 1. Create New `README.md`

```markdown
# Indeed Application Filler - Apify Actor

Automated Indeed job application form filling using Playwright browser automation.

## Features
- Indeed Quick Apply automation
- Standard Indeed application forms
- Screenshot capture for review
- API integration with job application backend
- Comprehensive error handling

## Installation
[Installation steps specific to Actor]

## Configuration
[Environment variables]

## Usage
[How to run Actor]

## Development
[Local development setup with Docker]

## API Integration
[Flask API endpoints used]

## License
MIT
```

#### 2. Update Documentation Files

- Copy and adapt: `E2E_TESTING_GUIDE.md` (Actor-specific sections)
- Copy and adapt: `DEPLOYMENT_CHECKLIST.md` (Apify-only steps)
- Keep: `FUTURE_DEVELOPMENT_PLAN.md` (same roadmap)
- Remove: Flask-specific integration guides

**Deliverables:**
- [ ] New README.md for standalone Actor
- [ ] Documentation adapted for Actor-only context
- [ ] Examples updated with standalone paths

---

### Task 1.6: Set Up CI/CD for Standalone Project
**Priority:** Medium
**Effort:** 2-3 hours

#### Create `.github/workflows/test.yml`

```yaml
name: Test Actor

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install chromium

    - name: Run linting
      run: |
        flake8 src tests --max-line-length=100

    - name: Run formatting check
      run: |
        black --check src tests

    - name: Run type checking
      run: |
        mypy src --ignore-missing-imports

    - name: Run tests
      run: |
        pytest tests/ -v
```

#### Create `.github/workflows/deploy-apify.yml`

```yaml
name: Deploy to Apify

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Apify
      env:
        APIFY_TOKEN: ${{ secrets.APIFY_TOKEN }}
      run: |
        npm install -g apify-cli
        apify push
```

**Deliverables:**
- [ ] CI/CD pipeline configured
- [ ] Automated testing on PRs
- [ ] Automated deployment to Apify on merge

---

## Phase 2: Monorepo Updates (Same Worktree Cycle)

### Task 2.1: Update Flask Backend to Reference External Actor
**Priority:** High
**Effort:** 1 hour

**Changes to `automation_api.py`:**

```python
# Before: Local reference
from modules.application_automation.actor_main import run_actor

# After: External Actor via Apify API
from apify_client import ApifyClient

def trigger_automation(job_id, application_id):
    """Trigger external Apify Actor"""
    client = ApifyClient(os.getenv("APIFY_TOKEN"))

    actor_input = {
        "job_id": job_id,
        "application_id": application_id,
        "flask_api_url": os.getenv("FLASK_API_URL"),
        "api_key": os.getenv("WEBHOOK_API_KEY")
    }

    # Call external Actor
    run = client.actor(os.getenv("APPLICATION_AUTOMATION_ACTOR_ID")).call(
        run_input=actor_input
    )

    return {"actor_run_id": run["id"], "status": "triggered"}
```

**Deliverables:**
- [ ] Flask API updated to call external Actor
- [ ] Local Actor code removed from imports
- [ ] Environment variables updated

---

### Task 2.2: Archive Old Actor Code in Monorepo
**Priority:** Low
**Effort:** 30 minutes

```bash
# Move to archived_files
mkdir -p archived_files/application_automation_v1
mv modules/application_automation/actor_main.py archived_files/application_automation_v1/
mv modules/application_automation/form_filler.py archived_files/application_automation_v1/
mv modules/application_automation/data_fetcher.py archived_files/application_automation_v1/
mv modules/application_automation/screenshot_manager.py archived_files/application_automation_v1/

# Keep in monorepo:
# - automation_api.py (Flask routes)
# - models.py (database models)
# - migrations/ (database migrations)
# - form_mappings/ (shared with Actor via sync)
```

**Deliverables:**
- [ ] Old Actor code archived
- [ ] Flask API code retained
- [ ] Documentation updated

---

### Task 2.3: Create Actor Integration Documentation
**Priority:** Medium
**Effort:** 1 hour

**New file: `modules/application_automation/ACTOR_INTEGRATION.md`**

```markdown
# Actor Integration Guide

The Application Automation Actor is now deployed as a separate project.

## Repository
https://github.com/yourusername/apify-indeed-application-filler

## Integration Points

### Flask → Actor
Endpoint: POST /api/application-automation/trigger
Triggers external Apify Actor

### Actor → Flask
Endpoints used by Actor:
- GET /api/jobs/{job_id} - Fetch job details
- GET /api/applicant/profile - Fetch applicant profile
- POST /api/application-automation/submissions - Report results

## Configuration
[Environment variables needed]

## Deployment
[How to deploy Actor separately]
```

**Deliverables:**
- [ ] Integration documentation created
- [ ] API contract documented
- [ ] Deployment procedures updated

---

## Phase 3: Sync Strategy for Form Mappings

### Task 3.1: Decide on Form Mappings Sync Strategy
**Priority:** Medium
**Effort:** 2 hours

**Options:**

**Option A: Git Submodule**
```bash
# In Actor repo
git submodule add https://github.com/yourusername/form-mappings form_mappings
```

**Option B: Duplicate & Manual Sync**
- Keep separate copies
- Manually sync when updated
- Simpler, no git submodule complexity

**Option C: NPM/PyPI Package**
- Publish form mappings as package
- Both projects install as dependency
- More complex, better for scale

**Recommendation:** Start with Option B (duplicate), move to Option C if mappings change frequently.

**Deliverables:**
- [ ] Sync strategy decided
- [ ] Implementation plan created
- [ ] Sync process documented

---

## Phase 4: Testing & Validation

### Task 4.1: Test Standalone Actor Locally
**Priority:** High
**Effort:** 2 hours

```bash
# In new Actor repo
cd apify-indeed-application-filler

# Run in Docker devcontainer
code .
# VSCode opens devcontainer

# Test Actor locally
python src/main.py

# Or use Apify CLI
apify run
```

**Test Cases:**
- [ ] Actor starts successfully
- [ ] Connects to Flask API
- [ ] Fetches job data
- [ ] Fills form (mock mode)
- [ ] Captures screenshots
- [ ] Reports results back

**Deliverables:**
- [ ] All test cases pass
- [ ] No import errors
- [ ] Configuration validated

---

### Task 4.2: Deploy Actor to Apify Staging
**Priority:** High
**Effort:** 1 hour

```bash
# Push to Apify
apify login
apify push

# Test on Apify platform
apify call --input '{"job_id": "test_123"}'
```

**Validation:**
- [ ] Actor deploys successfully
- [ ] Runs on Apify infrastructure
- [ ] Can reach Flask API
- [ ] Logs show expected behavior

**Deliverables:**
- [ ] Actor deployed to Apify
- [ ] Test run successful
- [ ] Logs reviewed and clean

---

### Task 4.3: Integration Test (Flask + Actor)
**Priority:** High
**Effort:** 1 hour

**End-to-End Test:**
1. Trigger automation via Flask API
2. Actor starts on Apify
3. Actor fetches data from Flask
4. Actor fills form (mock or real)
5. Actor reports back to Flask
6. Database updated
7. Screenshots accessible

**Validation Checklist:**
- [ ] Flask trigger endpoint works
- [ ] Actor receives correct input
- [ ] Actor can authenticate with Flask API
- [ ] Data flows correctly both directions
- [ ] Database records created
- [ ] No errors in logs

**Deliverables:**
- [ ] End-to-end test passes
- [ ] Integration validated
- [ ] Performance acceptable

---

## Phase 5: Documentation & Handoff

### Task 5.1: Create Deployment Runbook
**Priority:** Medium
**Effort:** 2 hours

**Document:** `DEPLOYMENT_RUNBOOK.md`

**Contents:**
- Prerequisites checklist
- Step-by-step deployment procedure
- Rollback procedure
- Troubleshooting guide
- Contact information

**Deliverables:**
- [ ] Runbook completed
- [ ] Tested by following runbook
- [ ] Shared with team

---

### Task 5.2: Update Architecture Diagrams
**Priority:** Low
**Effort:** 1 hour

**Create/Update:**
- System architecture diagram (separated repos)
- Data flow diagram (Flask ↔ Actor)
- Deployment diagram (Apify + Digital Ocean)

**Tools:** draw.io, Mermaid, or similar

**Deliverables:**
- [ ] Diagrams updated
- [ ] Added to documentation
- [ ] Exported as images

---

### Task 5.3: Knowledge Transfer
**Priority:** Medium
**Effort:** 2 hours

**Activities:**
- Walkthrough of new repo structure
- Demo of local development setup
- Explanation of deployment process
- Q&A session

**Deliverables:**
- [ ] Team walkthrough completed
- [ ] Questions answered
- [ ] Documentation reviewed

---

## Future Worktree Cycles (Beyond Separation)

### Cycle 2: Hybrid Detection Implementation
**From:** `FUTURE_DEVELOPMENT_PLAN.md` Phase 3

**Tasks:**
- [ ] Research GPT-4 Vision vs Gemini Vision
- [ ] Implement AI field detection fallback
- [ ] Create selector caching system
- [ ] Test on 50+ unknown forms
- [ ] Optimize costs

**New Worktree:** `task/05-hybrid-detection`

---

### Cycle 3: Greenhouse Platform Support
**From:** `FUTURE_DEVELOPMENT_PLAN.md` Phase 4.1

**Tasks:**
- [ ] Research Greenhouse form structure
- [ ] Create Greenhouse form mappings
- [ ] Implement Greenhouse-specific handlers
- [ ] Test with 20+ Greenhouse applications
- [ ] Document Greenhouse quirks

**New Worktree:** `task/06-greenhouse-support`

---

### Cycle 4: Lever Platform Support
**From:** `FUTURE_DEVELOPMENT_PLAN.md` Phase 4.2

**Tasks:**
- [ ] Research Lever application forms
- [ ] Create Lever form mappings
- [ ] Test with 15+ Lever applications

**New Worktree:** `task/07-lever-support`

---

### Cycle 5: Multi-Page Form Support
**From:** `FUTURE_DEVELOPMENT_PLAN.md` Phase 2.1

**Tasks:**
- [ ] Implement multi-step form navigation
- [ ] Add form validation error handling
- [ ] Create checkpointing system
- [ ] Test with complex multi-page forms

**New Worktree:** `task/08-multipage-forms`

---

## Checklist: Project Separation Complete

**Pre-Separation:**
- [ ] Architecture decision documented (API-only communication)
- [ ] Tasks documented in this file
- [ ] Team alignment on separation approach

**During Separation:**
- [ ] New GitHub repository created
- [ ] Actor code extracted and refactored
- [ ] Development environment configured (Docker + VSCode)
- [ ] Tests updated and passing
- [ ] Documentation adapted for standalone project
- [ ] CI/CD pipeline configured

**Post-Separation:**
- [ ] Flask backend updated to call external Actor
- [ ] Old Actor code archived in monorepo
- [ ] Integration documentation created
- [ ] Form mapping sync strategy implemented
- [ ] End-to-end testing completed
- [ ] Actor deployed to Apify production

**Validation:**
- [ ] Standalone Actor runs locally in Docker
- [ ] Actor deploys to Apify successfully
- [ ] Flask can trigger Actor via Apify API
- [ ] Actor can communicate with Flask API
- [ ] All API endpoints tested and working
- [ ] Database operations validated
- [ ] Screenshots captured and accessible
- [ ] Error handling works as expected
- [ ] Performance meets requirements (<90s per application)
- [ ] Documentation complete and accurate

---

## Notes & Considerations

### Development Environment Parity

**Goal:** Match exact setup from current monorepo devcontainer

**Key Requirements:**
- Python 3.11
- Docker-in-Docker support
- Node.js 18 (for Apify CLI)
- Playwright + Chromium
- Same VSCode extensions
- Same linting/formatting tools

**Testing:** Ensure Actor runs identically in:
1. Local Docker devcontainer
2. Apify platform
3. CI/CD pipeline

### API Contract Stability

**Important:** Flask API is the contract between Actor and backend

**Versioning Strategy:**
- Use API versioning (e.g., `/api/v1/...`)
- Maintain backward compatibility
- Document breaking changes clearly
- Test Actor with each API change

**Communication:**
- Notify Actor repo when API changes
- Update Actor integration tests
- Deploy Actor updates after API changes

### Form Mapping Maintenance

**Challenge:** Indeed changes forms frequently

**Strategy:**
- Monitor Actor failure rate
- Investigate failures for selector issues
- Update form_mappings/indeed.json
- Deploy updated Actor
- Consider automated selector validation

**Cadence:** Review monthly or when failure rate >20%

### Cost Management

**Current MVP:** $15-30/month (Apify only)

**After Separation:**
- Apify: Same cost
- GitHub Actions: Free tier likely sufficient
- No additional costs expected

**Monitoring:** Track Apify usage to avoid overages

---

## Contact & Resources

**Monorepo:** https://github.com/Steve-Merlin-Projecct/Merlin_2
**New Actor Repo:** (To be created)
**Apify Console:** https://console.apify.com
**Documentation:** See README files in both repos

**Questions?** Create issue in relevant repository.

---

**End of Future Worktree Tasks**
