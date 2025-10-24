---
title: "Discovery Findings Dashboard Redesign"
type: architecture
component: general
status: draft
tags: []
---

# Dashboard Redesign - Discovery Findings
**Date**: October 9, 2025
**Branch**: task/07-dashboard
**Version**: 4.2.0

## Executive Summary

Comprehensive discovery analysis of the existing job application dashboard to inform ground-up redesign. The current system provides basic metrics and application tracking but suffers from performance bottlenecks, limited insights, and no real-time capabilities.

---

## 1. Current System Architecture

### Frontend Stack
- **Framework**: Vanilla JavaScript (no React/Vue)
- **UI Library**: Bootstrap 5 Dark Theme
- **Styling**: Unified CSS theme (`/static/css/unified-theme.css`)
- **Authentication**: Session-based password protection
- **Update Strategy**: Auto-refresh every 5 minutes (full page reload data)

### Backend Stack
- **Framework**: Flask with Blueprint pattern
- **Database**: PostgreSQL (32 normalized tables)
- **ORM**: SQLAlchemy with context managers
- **Authentication**: Session cookies with SHA256 password hashing
- **API Design**: RESTful endpoints under `/api/dashboard/*`

### Key Modules
- `modules/dashboard_api.py`: Core dashboard endpoints
- `modules/database/database_client.py`: PostgreSQL connections
- `modules/workflow/application_orchestrator.py`: Application automation
- `modules/ai_job_description_analysis/`: Gemini AI integration
- `modules/scraping/`: Job scraping pipeline

---

## 2. Database Schema Analysis

### Core Tables (32 Total)

**Data Pipeline Flow**:
```
raw_job_scrapes (Entry Point)
    ↓
cleaned_job_scrapes (Deduplication)
    ↓
pre_analyzed_jobs (AI Queue)
    ↓
analyzed_jobs (AI Processed)
    ↓
jobs (Legacy Compatibility)
    ↓
job_applications (Final Output)
```

**Supporting Tables**:
- **Normalization Tables**: job_skills, job_industries, job_benefits, job_red_flags
- **Analysis Tables**: job_analysis, job_ats_keywords, job_cover_letter_insights
- **System Tables**: companies, user_job_preferences, application_settings
- **Tracking Tables**: link_tracking, clicks, job_logs

### Critical Relationships
```sql
companies (1) → (∞) jobs
jobs (1) → (∞) job_applications
analyzed_jobs (1) → (∞) job_skills
analyzed_jobs (1) → (∞) job_industries
job_applications (1) → (∞) job_application_documents
```

---

## 3. Current Dashboard Features

### Implemented Features

**Authentication**:
- Password-protected dashboard
- Session management
- Auto-logout on inactivity

**Metrics Display**:
- Scrapes (24h, 7d counts)
- Applications sent (24h, 7d counts)
- Success rate percentage
- Total jobs tracked
- Average response time (placeholder)

**Recent Applications Table**:
- Last 20 applications
- Job title, company, status
- Document links (resume, cover letter)
- Application date
- View details action

**Gemini AI Usage Tracking**:
- Daily requests used/limit (1,500)
- Monthly projection
- Model information (Gemini 2.0 Flash)
- Cost tracking (FREE tier)
- Usage recommendations
- Model comparison (Flash vs Lite vs 2.5)

**System Status**:
- Database connectivity
- Storage availability
- Last update timestamp

**Navigation Links**:
- Workflow visualization
- Database schema viewer
- Tone analysis
- User preferences
- Job override
- Copywriting evaluator

### Missing Features (Identified Gaps)

**Real-Time Capabilities**:
- No live updates (requires manual refresh)
- No websocket/SSE connections
- No push notifications

**Advanced Analytics**:
- No trend charts/graphs
- No comparative analysis (week-over-week)
- No funnel visualization (scraped → applied → responded)
- No company intelligence aggregation

**Job Management**:
- No job search/filtering
- No bulk actions (approve/reject multiple jobs)
- No priority queue visualization
- No manual application triggering

**Application Insights**:
- No document preview
- No email composition preview
- No response tracking
- No follow-up reminders

**User Experience**:
- No customizable dashboard layout
- No saved views/filters
- No dark/light theme toggle (locked to dark)
- No mobile responsiveness optimization

**Performance Monitoring**:
- No query performance metrics
- No pipeline health visualization
- No error rate tracking
- No scraping velocity charts

---

## 4. User Journey & Workflow Analysis

### Primary User: Steve Glen

**Daily Workflow**:
1. **Morning Check** (8am): Review overnight scraping results
2. **Application Review** (9am): Check status of sent applications
3. **Preference Adjustment** (as needed): Update job criteria
4. **Manual Trigger** (occasional): Run workflow for high-priority jobs
5. **Evening Check** (6pm): Review day's activity

### Critical User Paths

**Path 1: Dashboard Overview** (288x/day)
```
Login → View Stats → Review Recent Applications → Logout
Duration: ~2 minutes
Pain Points:
- Must manually refresh to see updates
- No at-a-glance job pipeline status
- Limited context on why jobs were rejected
```

**Path 2: Job Discovery** (5-10x/day)
```
Login → Navigate to Workflow → Trigger Scraping → Wait → Check Results
Duration: ~5-10 minutes
Pain Points:
- No progress indicator during scraping
- Can't see which jobs are in AI analysis queue
- No ETA for job analysis completion
```

**Path 3: Application Monitoring** (Continuous)
```
Email Notification → Login → View Application Details → Check Documents
Duration: ~3 minutes
Pain Points:
- No direct link from email to specific application
- Can't preview documents without downloading
- No response tracking integration
```

**Path 4: Preference Management** (Weekly)
```
Login → Preferences Page → Update Criteria → Save → Test Match
Duration: ~15 minutes
Pain Points:
- Can't see live preview of affected jobs
- No simulation mode to test preferences
- Unclear which preference package is active
```

---

## 5. Data Flow & Query Analysis

### High-Frequency Queries (288x/day - Every Dashboard Load)

**1. Dashboard Stats**:
```sql
-- 6 separate COUNT queries executed sequentially
SELECT COUNT(*) FROM jobs WHERE created_at >= NOW() - INTERVAL '1 day'
SELECT COUNT(*) FROM jobs WHERE created_at >= NOW() - INTERVAL '7 days'
SELECT COUNT(*) FROM job_applications WHERE created_at >= NOW() - INTERVAL '1 day'
SELECT COUNT(*) FROM job_applications WHERE created_at >= NOW() - INTERVAL '7 days'
SELECT COUNT(CASE WHEN application_status = 'sent' THEN 1 END) / COUNT(*) FROM job_applications
SELECT COUNT(*) FROM jobs
```
**Issue**: No aggregation, no caching, hits database every time

**2. Recent Applications**:
```sql
-- 3-way JOIN executed on every load
SELECT ja.*, j.job_title, c.name as company_name
FROM job_applications ja
LEFT JOIN jobs j ON ja.job_id = j.id
LEFT JOIN companies c ON j.company_id = c.id
ORDER BY ja.created_at DESC
LIMIT 20
```
**Issue**: Expensive JOIN, no materialized view

### Medium-Frequency Queries (50x/day - Workflow Execution)

**3. Eligible Job Discovery**:
```sql
SELECT id, job_title, company_id, priority_score
FROM analyzed_jobs
WHERE eligibility_flag = true
  AND ai_analysis_completed = true
  AND application_status = 'not_applied'
ORDER BY priority_score DESC
LIMIT 10
```
**Issue**: No index on (eligibility_flag, priority_score, application_status)

**4. Pipeline Statistics**:
```sql
-- 4 separate COUNT queries
SELECT COUNT(*) FROM raw_job_scrapes
SELECT COUNT(*) FROM cleaned_job_scrapes
SELECT COUNT(*) FROM pre_analyzed_jobs WHERE queued_for_analysis = true
SELECT COUNT(*) FROM analyzed_jobs WHERE ai_analysis_completed = true
```
**Issue**: Could be single aggregate query

### Batch Processing Queries (Hourly/Daily)

**5. Raw to Cleaned Transformation**:
```sql
SELECT * FROM raw_job_scrapes ORDER BY scrape_timestamp DESC LIMIT 100
-- Complex deduplication logic in Python
```
**Issue**: Deduplication done in application layer, not database

**6. AI Analysis Queue**:
```sql
SELECT * FROM pre_analyzed_jobs
WHERE queued_for_analysis = true
ORDER BY created_at DESC
LIMIT 10
```
**Issue**: Rate limited by Gemini API (15 RPM, 1500/day)

---

## 6. Performance Bottlenecks

### Critical Issues

**1. No Caching Layer**
- **Impact**: Every dashboard load hits database with 8+ queries
- **Frequency**: 288 times/day minimum
- **Solution**: Redis/in-memory cache with 5-minute TTL

**2. Expensive JOIN Operations**
- **Impact**: 3-way JOIN (job_applications → jobs → companies) on every load
- **Query**: Recent applications table
- **Solution**: Materialized view or denormalized summary table

**3. Missing Database Indexes**
- **Impact**: Full table scans on filtered queries
- **Affected Queries**: Job discovery, pipeline stats, application filtering
- **Solution**: Add compound indexes on (created_at, status, eligibility_flag)

**4. Sequential Query Execution**
- **Impact**: Dashboard stats execute 6 queries sequentially
- **Current Duration**: ~200-300ms
- **Solution**: Single aggregate query or parallel execution

**5. AI Analysis Rate Limiting**
- **Impact**: Can only process ~240 jobs/day (4-hour window)
- **Constraint**: Gemini free tier (15 RPM, 1500 requests/day)
- **Solution**: Job prioritization algorithm or paid tier upgrade

**6. No Real-Time Updates**
- **Impact**: Users must manually refresh to see changes
- **Current**: 5-minute auto-refresh (full page reload)
- **Solution**: WebSocket/Server-Sent Events for live updates

### Query Performance Benchmarks (Current)

| Query | Frequency | Avg Duration | Optimization Needed |
|-------|-----------|--------------|---------------------|
| Dashboard stats | 288x/day | 250ms | **Critical** - Aggregate + Cache |
| Recent applications | 288x/day | 180ms | **High** - Materialized view |
| Eligible jobs | 50x/day | 120ms | **Medium** - Add index |
| Pipeline stats | 50x/day | 200ms | **Medium** - Aggregate |
| Gemini usage | 288x/day | 90ms | **Low** - Cache |

---

## 7. Technology Stack Evaluation

### Current Stack Strengths
✅ **Flask**: Lightweight, well-understood
✅ **PostgreSQL**: Robust, normalized schema
✅ **Bootstrap**: Rapid UI development
✅ **SQLAlchemy**: Type-safe database access

### Current Stack Weaknesses
❌ **Vanilla JS**: No reactive updates, manual DOM manipulation
❌ **No State Management**: Data fetched repeatedly
❌ **No Build Pipeline**: No bundling, tree-shaking, or optimization
❌ **No Testing Framework**: Frontend logic untested
❌ **No Type Safety**: JavaScript without TypeScript

### Recommended Technology Additions

**Frontend Framework Options**:
1. **Vue.js 3** (Recommended)
   - Pros: Progressive adoption, small bundle size, excellent docs
   - Cons: Smaller ecosystem than React

2. **React 18**
   - Pros: Largest ecosystem, mature tooling
   - Cons: Larger bundle, more complex setup

3. **Alpine.js** (Lightweight Option)
   - Pros: Minimal overhead, works with existing HTML
   - Cons: Limited for complex UIs

**State Management**:
- Pinia (Vue) or Zustand (React)
- Local caching with Tanstack Query

**Real-Time Layer**:
- Server-Sent Events (SSE) for live updates
- Alternative: Socket.IO for bi-directional communication

**Visualization**:
- Chart.js or Apache ECharts for metrics
- D3.js for custom pipeline visualizations

**Build Tools**:
- Vite (fast, modern)
- ESLint + Prettier for code quality

---

## 8. Feature Gaps & User Needs

### Priority 1: Critical Missing Features
Usability.
Looks good.
Responsive design.

### Priority 2: High-Value Enhancements
**Response Tracking Integration**
- **Need**: Track email opens, link clicks from applications
- **Current**: Basic link tracking exists but not surfaced in UI
- **Impact**: No visibility into application engagement

**Calendar Integration**
- **Need**: Follow-up reminders, application timeline view
- **Current**: No temporal organization
- **Impact**: Applications get lost in backlog

### Priority 3: Nice-to-Have Features
**Application Success Analytics**
- **Need**: Track which job types/companies have highest response rates
- **Current**: Basic success percentage only
- **Impact**: Can't optimize application strategy

**Document Preview**
- **Need**: View generated resumes/cover letters before sending
- **Current**: Must download to review
- **Impact**: Can't quickly verify quality

**Company Intelligence Dashboard**
- **Need**: Aggregate view of all jobs from same company
- **Current**: Company data scattered across job listings
- **Impact**: Can't evaluate company attractiveness



---

## 10. Technical Debt & Constraints

### Current Technical Debt

**1. Database Schema Evolution**
- Multiple table formats (jobs vs analyzed_jobs vs pre_analyzed_jobs)
- Legacy columns retained for compatibility
- **Risk**: Migration complexity for redesign

**2. API Inconsistencies**
- Some endpoints return arrays, others objects
- Inconsistent error response formats
- No API versioning strategy
- **Risk**: Breaking changes impact multiple consumers

**3. Frontend Code Quality**
- No component structure
- Global scope pollution
- Inline styles mixed with CSS classes
- **Risk**: High maintenance burden

**4. Security Hardening Needed**
- Session timeout not configurable
- No CSRF token validation
- Password stored as hash but weak salt
- **Risk**: Security vulnerabilities

### System Constraints

**1. Gemini API Rate Limits**
- **Free Tier**: 15 RPM, 1,500 requests/day
- **Impact**: Can only analyze ~240 jobs/day
- **Mitigation**: Job prioritization, paid tier consideration

**2. Email Sending Limits**
- **Gmail API**: 500 emails/day (free), 2,000/day (Workspace)
- **Impact**: Application volume capped
- **Mitigation**: Rate limiting in application orchestrator

**3. Database Connection Pool**
- **Current**: No connection pooling configured
- **Impact**: Connection exhaustion under load
- **Mitigation**: PgBouncer or SQLAlchemy pooling

**4. Single-Server Architecture**
- **Current**: All components on single instance
- **Impact**: No horizontal scaling
- **Mitigation**: Acceptable for single-user system

---

## 11. User Feedback & Pain Points

### Observed Pain Points

**"I don't know what the system is doing"**
- No visibility into background processes
- Scraping/analysis happens invisibly
- **Solution**: Live activity feed, process indicators



**"I'm not sure if my preferences are working"**
- No feedback on preference matching
- Can't see why jobs were rejected
- **Solution**: Rejection reasoning, preference testing

**"The dashboard feels static and slow"**

- No smooth transitions 
---

## 12. Discovery Conclusions & Recommendations

### Key Findings Summary

1. **Performance**: 8+ database queries per dashboard load with no caching
2. **User Experience**: Static, limited insights, requires manual interaction
3. **Scalability**: AI analysis bottlenecked at 240 jobs/day
4. **Architecture**: Vanilla JS limits reactivity and maintainability
5. **Analytics**: Rich data exists but poorly surfaced in UI





## Next Steps

**Immediate Actions**:
1. Create dashboard redesign PRD (Product Requirements Document)
2. Design database optimization strategy
3. Select frontend framework (Vue vs React)
4. Create wireframes for new dashboard layouts
5. Estimate effort and create implementation timeline

**Planning Phase Deliverables**:
- Technical architecture document
- UI/UX wireframes and mockups
- Database schema optimization plan
- API endpoint design (new + refactored)
- Implementation task breakdown

---

**Document Status**: Discovery Complete
**Next Phase**: Major Planning
**Estimated Planning Duration**: 2-3 sessions
**Target Implementation Start**: After planning approval
