# Next Worktree Package
## Outstanding Work from task/04-apply-assistant

**Created:** 2025-10-17
**Current Branch:** task/04-apply-assistant
**Status:** Work Complete - Ready for Next Cycle

---

## 📋 Summary

This worktree completed the Application Automation Module MVP with comprehensive testing and documentation. All work has been committed and is ready for merge. The following tasks are packaged for future worktree cycles.

**Last Commit:** `bdd1d6c - docs: Add comprehensive future development tasks and project separation plan`

---

## 🎯 Recommended Next Worktree: Project Separation

### Worktree Name Suggestion
`task/05-actor-separation` or `feature/standalone-actor`

### Objective
Separate the Apify Actor from the monorepo into a standalone GitHub repository while maintaining API integration with the Flask backend.

### Priority: HIGH
**Estimated Effort:** 15-20 hours across 5 phases

### Tasks Overview

#### Phase 1: New Repository Setup (4-5 hours)
- [ ] Create new GitHub repository `apify-indeed-application-filler`
- [ ] Extract Actor code from monorepo (`actor_main.py`, `form_filler.py`, `data_fetcher.py`, `screenshot_manager.py`)
- [ ] Configure Docker devcontainer matching monorepo setup
- [ ] Set up `.actor/Dockerfile` for Apify deployment
- [ ] Create standalone `requirements.txt`

**Reference:** `modules/application_automation/FUTURE_WORKTREE_TASKS.md` (Tasks 1.1-1.3)

#### Phase 2: Code Refactoring (3-4 hours)
- [ ] Update import paths (from `modules.application_automation.*` to `src.*`)
- [ ] Create `src/config.py` for configuration management
- [ ] Refactor `src/main.py` as Actor entry point
- [ ] Create `src/exceptions.py` for custom exceptions
- [ ] Update all file references

**Reference:** `modules/application_automation/FUTURE_WORKTREE_TASKS.md` (Task 1.4)

#### Phase 3: Monorepo Integration (2-3 hours)
- [ ] Update Flask `automation_api.py` to call external Actor via Apify API
- [ ] Remove local Actor imports from Flask backend
- [ ] Archive old Actor code in `archived_files/application_automation_v1/`
- [ ] Update environment variables (`APIFY_TOKEN`, `APPLICATION_AUTOMATION_ACTOR_ID`)
- [ ] Create integration documentation

**Reference:** `modules/application_automation/FUTURE_WORKTREE_TASKS.md` (Tasks 2.1-2.3)

#### Phase 4: Testing & Validation (3-4 hours)
- [ ] Test standalone Actor locally in Docker
- [ ] Deploy Actor to Apify staging environment
- [ ] End-to-end integration test (Flask → Actor → Flask)
- [ ] Validate database operations
- [ ] Verify screenshot capture and storage

**Reference:** `modules/application_automation/FUTURE_WORKTREE_TASKS.md` (Tasks 4.1-4.3)

#### Phase 5: CI/CD & Documentation (2-3 hours)
- [ ] Create `.github/workflows/test.yml` for Actor repo
- [ ] Create `.github/workflows/deploy-apify.yml` for auto-deployment
- [ ] Write standalone `README.md` for Actor repo
- [ ] Create `DEPLOYMENT_RUNBOOK.md`
- [ ] Update architecture diagrams

**Reference:** `modules/application_automation/FUTURE_WORKTREE_TASKS.md` (Tasks 1.5-1.6, 5.1-5.2)

### Key Decisions to Make

**Form Mappings Sync Strategy:**
- **Option A:** Git submodule (complex but auto-sync)
- **Option B:** Duplicate & manual sync (simple, recommended for MVP)
- **Option C:** NPM/PyPI package (best for scale, overkill for now)

**Recommendation:** Start with Option B, migrate to Option C if mappings change frequently.

### Success Criteria
- ✅ Standalone Actor runs locally in Docker devcontainer
- ✅ Actor deploys successfully to Apify
- ✅ Flask can trigger Actor via Apify API
- ✅ Actor communicates with Flask API (bidirectional)
- ✅ All tests pass (unit, integration, e2e)
- ✅ Performance <90s per application
- ✅ Documentation complete and accurate

### Files to Reference
- **Task Details:** `modules/application_automation/FUTURE_WORKTREE_TASKS.md`
- **Architecture Decision:** API-only communication (already implemented correctly)
- **Deployment Guide:** `modules/application_automation/DEPLOYMENT_CHECKLIST.md`

---

## 🚀 Alternative Next Worktree Options

### Option 2: Hybrid Detection Implementation
**Worktree:** `task/06-hybrid-detection`
**Priority:** HIGH (Critical for platform expansion)
**Effort:** 3-4 weeks

**Objective:** Implement AI-powered field detection fallback for unknown forms

**Key Tasks:**
- [ ] Research GPT-4 Vision vs Gemini Vision (cost/performance)
- [ ] Implement screenshot-based field detection
- [ ] Create prompt engineering for form analysis
- [ ] Build selector caching system
- [ ] Test accuracy on 50+ unknown forms

**Reference:** `modules/application_automation/FUTURE_DEVELOPMENT_PLAN.md` (Phase 3)

**Cost Consideration:** $50-100/month for AI API calls

---

### Option 3: Rate Limiting Completion
**Worktree:** `task/05-rate-limiting-completion`
**Priority:** MEDIUM
**Effort:** 7-9 hours

**Objective:** Complete remaining 15% endpoint coverage and add testing

**Key Tasks:**
1. **Endpoint Coverage (2 hours)**
   - [ ] Protect remaining database endpoints (`/api/db/jobs/<job_id>`, `/api/db/statistics`, etc.)
   - [ ] Protect email endpoints (`/api/email/send-job-application`, `/api/email/test`)
   - [ ] Protect main app endpoints (`/api/process-scrapes`, `/api/intelligent-scrape`)

2. **Integration Testing (2 hours)**
   - [ ] Write rate limit enforcement tests
   - [ ] Test memory usage tracking
   - [ ] Test violation logging
   - [ ] Test authentication integration

3. **Dashboard Integration (3 hours)**
   - [ ] Add rate limit metrics widget to dashboard
   - [ ] Create memory usage gauge chart
   - [ ] Display cache analysis visualization
   - [ ] Add violation alerts

4. **Query Analyzer Module (3 hours, optional)**
   - [ ] Implement automatic query logging
   - [ ] Build duplicate detection
   - [ ] Generate cache recommendations

**Reference:** `FUTURE_TASKS_RATE_LIMITING.md`

---

### Option 4: Dashboard V2 Critical Fixes
**Worktree:** `task/05-dashboard-v2-fixes`
**Priority:** HIGH (Currently Blocked)
**Effort:** 12-15 hours

**⚠️ CRITICAL BLOCKER:** Database migrations reference non-existent columns

**Objective:** Fix blocked migrations and complete dashboard views

**Phase 1: Fix Migrations (1-2 hours)**
- [ ] Audit database schema (`\d+ jobs`, `\d+ job_applications`, `\d+ companies`)
- [ ] Update migration files with actual column names:
  - `001_dashboard_optimization_indexes.sql`
  - `002_dashboard_materialized_views.sql`
  - `003_dashboard_aggregation_tables.sql`
- [ ] Run migrations and verify
- [ ] Backfill data

**Phase 2: Complete Views (7-9 hours)**
- [ ] Applications View with timeline visualization
- [ ] Analytics View with Chart.js integration
- [ ] Database Schema Visualization
- [ ] Connect Jobs View to real API endpoints

**Phase 3: Real API Integration (2-3 hours)**
- [ ] Create `/api/v2/dashboard/jobs` endpoint
- [ ] Add filtering, sorting, pagination
- [ ] Connect frontend to backend

**Reference:** `TODO.md`

**Total Remaining Work:** ~43-58 hours for full completion

---

### Option 5: Platform Expansion (Greenhouse)
**Worktree:** `task/07-greenhouse-support`
**Priority:** HIGH
**Effort:** 3 weeks

**Objective:** Add Greenhouse ATS platform support (~40% market share in tech)

**Key Tasks:**
- [ ] Research Greenhouse application form structure
- [ ] Create form mappings for common templates
- [ ] Handle OAuth authentication (Google, LinkedIn)
- [ ] Implement EEO question handling
- [ ] Test with 20+ Greenhouse applications

**Prerequisites:**
- ✅ MVP stabilized (COMPLETE)
- ⚠️ Hybrid detection recommended but not required

**Reference:** `modules/application_automation/FUTURE_DEVELOPMENT_PLAN.md` (Phase 4.1)

---

## 📊 Priority Matrix

| Task | Priority | Effort | Business Value | Technical Risk |
|------|----------|--------|----------------|----------------|
| **Actor Separation** | HIGH | 15-20h | High (clean architecture) | Low |
| **Dashboard V2 Fixes** | HIGH | 12-15h | Medium (user-facing) | Low |
| **Hybrid Detection** | HIGH | 3-4 weeks | Very High (platform flexibility) | Medium |
| **Rate Limiting Completion** | MEDIUM | 7-9h | Medium (completeness) | Low |
| **Greenhouse Support** | HIGH | 3 weeks | High (market coverage) | Medium |

---

## 🔧 Technical Context for Next Developer

### Current System State

**Application Automation Module:**
- ✅ MVP Complete (Indeed Quick Apply + Standard Forms)
- ✅ Actor runs on Apify successfully
- ✅ Flask API integration working
- ✅ Screenshot capture implemented
- ✅ Comprehensive testing suite
- ✅ Form mappings for Indeed
- ✅ E2E testing guide complete

**Architecture:**
- Actor communicates with database **ONLY through Flask API** (correct design)
- No database credentials in Actor (security best practice)
- API-first approach validated and working

**Code Quality:**
- All code formatted with Black
- Flake8 compliance
- Comprehensive inline documentation
- Test coverage >80% for core modules

### Environment Setup

**Development Environment:**
- Docker devcontainer with Python 3.11
- Playwright + Chromium installed
- VSCode with Pylance, Black, Flake8
- PostgreSQL database (local_Merlin_3)

**Key Environment Variables:**
```bash
# Flask API
FLASK_API_URL=http://localhost:5000
WEBHOOK_API_KEY=<from .env>

# Apify (for Actor deployment)
APIFY_TOKEN=<from .env>

# Database (auto-detected)
PGPASSWORD=<from .env>
DATABASE_NAME=local_Merlin_3
```

### Repository Structure
```
modules/application_automation/
├── actor_main.py              # Actor entry point
├── form_filler.py             # Form filling logic
├── data_fetcher.py            # Flask API client
├── screenshot_manager.py      # Screenshot capture
├── form_mappings/             # Platform-specific selectors
│   └── indeed.json
├── tests/                     # Test suite
│   ├── test_form_mappings.py
│   ├── test_api_simple.py
│   └── test_integration.py
├── .actor/                    # Apify configuration
│   ├── Dockerfile
│   ├── actor.json
│   └── input_schema.json
├── FUTURE_WORKTREE_TASKS.md   # Task details
├── FUTURE_DEVELOPMENT_PLAN.md # Long-term roadmap
├── E2E_TESTING_GUIDE.md       # Testing procedures
└── DEPLOYMENT_CHECKLIST.md    # Deployment steps
```

---

## 🚦 Getting Started (Next Worktree)

### Step 1: Create New Worktree
```bash
# Recommended for Actor Separation
/tree create task/05-actor-separation "Separate Apify Actor into standalone repository"

# Alternative options
/tree create task/05-rate-limiting-completion "Complete rate limiting endpoint coverage"
/tree create task/05-dashboard-v2-fixes "Fix dashboard migrations and complete views"
/tree create task/06-hybrid-detection "Implement AI-powered form detection"
/tree create task/07-greenhouse-support "Add Greenhouse ATS platform support"
```

### Step 2: Load Context
```bash
# For Actor Separation
cat modules/application_automation/FUTURE_WORKTREE_TASKS.md
cat modules/application_automation/FUTURE_DEVELOPMENT_PLAN.md

# For Rate Limiting
cat FUTURE_TASKS_RATE_LIMITING.md

# For Dashboard V2
cat TODO.md
cat DASHBOARD_V2_HANDOFF.md

# For Platform Expansion
cat modules/application_automation/FUTURE_DEVELOPMENT_PLAN.md  # Phase 4
```

### Step 3: Review Current Implementation
```bash
# Test current MVP
python modules/application_automation/tests/test_api_simple.py
python modules/application_automation/tests/test_form_mappings.py

# Check database schema
psql -h localhost -U postgres -d local_Merlin_3 -c "\d+ jobs"

# Review API endpoints
curl http://localhost:5000/api/health
```

### Step 4: Start Implementation
Follow the task-specific guide from the chosen worktree option above.

---

## 📝 Notes & Recommendations

### For Actor Separation (Recommended Next Task)
- **Clean separation:** Actor has NO database dependencies (by design)
- **API contract stable:** Flask endpoints well-defined and tested
- **Low risk:** Can be done incrementally with rollback option
- **High value:** Improves maintainability and deployment flexibility

### For Hybrid Detection
- **Cost analysis required:** Budget $50-100/month for AI API calls
- **Research phase critical:** Test GPT-4 Vision vs Gemini Vision first
- **High impact:** Enables support for any platform without manual mapping

### For Dashboard V2
- **Blocker must be resolved first:** Database schema audit required
- **User-facing value:** Improves operator experience significantly
- **Integration complexity:** Requires frontend + backend coordination

### General Recommendations
1. **Prioritize Actor Separation** - Clean architecture foundation for future work
2. **Then Hybrid Detection** - Unlocks platform expansion capabilities
3. **Dashboard V2 can be parallel** - Different skillset, no conflicts
4. **Rate Limiting is low-hanging fruit** - Quick completion for 100% coverage

---

## 🔗 Reference Documentation

### Task-Specific Guides
- Actor Separation: `modules/application_automation/FUTURE_WORKTREE_TASKS.md`
- Development Roadmap: `modules/application_automation/FUTURE_DEVELOPMENT_PLAN.md`
- Rate Limiting: `FUTURE_TASKS_RATE_LIMITING.md`
- Dashboard V2: `TODO.md`, `DASHBOARD_V2_HANDOFF.md`

### Testing & Deployment
- E2E Testing: `modules/application_automation/E2E_TESTING_GUIDE.md`
- Deployment: `modules/application_automation/DEPLOYMENT_CHECKLIST.md`

### Architecture & Design
- System Overview: `docs/architecture/system-overview.md`
- Database Schema: `docs/database-connection-guide.md`
- API Documentation: `docs/api/`

### Code Quality
- Standards: `docs/code-quality-standards.md`
- Agent Usage: `docs/agent-usage-guide.md`

---

## ✅ Current Worktree Completion Checklist

**task/04-apply-assistant Status:**
- [x] Application Automation Module MVP complete
- [x] Actor successfully deployed to Apify
- [x] Flask API integration working
- [x] Form filling logic implemented (Indeed Quick Apply + Standard)
- [x] Screenshot capture and storage working
- [x] Comprehensive test suite written
- [x] E2E testing guide created
- [x] Deployment checklist documented
- [x] Future development plan created (6-12 month roadmap)
- [x] Project separation tasks documented
- [x] All code committed to git
- [x] Documentation updated in CLAUDE.md
- [x] Ready for merge to main branch

**Outstanding Work:** Packaged in this document for next worktree cycle

---

## 🎯 Success Metrics (To Track in Next Worktree)

### For Actor Separation
- [ ] Standalone Actor runs in <90s per application
- [ ] 100% API integration tests passing
- [ ] Zero import errors in separated codebase
- [ ] CI/CD pipeline successfully deploying to Apify

### For Hybrid Detection
- [ ] AI detection accuracy >70%
- [ ] Cost per application <$0.50
- [ ] Selector cache hit rate >80%
- [ ] Successfully handles 50+ unknown form types

### For Dashboard V2
- [ ] All migrations run without errors
- [ ] Dashboard loads in <2s
- [ ] Real-time metrics update <5s latency
- [ ] Mobile responsive on all pages

### For Rate Limiting
- [ ] 100% endpoint coverage
- [ ] Test coverage >80%
- [ ] Dashboard integration complete
- [ ] Query analyzer providing cache recommendations

---

**Last Updated:** 2025-10-17
**Branch:** task/04-apply-assistant
**Next Recommended Worktree:** task/05-actor-separation
**Status:** ✅ Ready for handoff

---

**End of Next Worktree Package**
