# PRD: Complete Dashboard Views (Applications, Analytics, Schema)

## Overview
Complete the remaining dashboard views (Applications, Analytics, Schema) with full functionality including filtering, sorting, charts, and database visualization. Use existing API endpoints in dashboard_api_v2.py and Alpine.js for interactivity.

## Current State
- Dashboard V2 main view: ✅ Complete (dashboard_v2.html)
- Jobs view: ✅ Complete (dashboard_jobs.html with API endpoint)
- Applications view: 🟡 Partial (template exists, needs backend routes + functionality)
- Analytics view: 🟡 Partial (template exists, needs charts + backend)
- Schema view: ❌ Missing (need to create route + visualization)

## Requirements

### 1. Applications View
**Route:** `/dashboard/applications`
**Template:** `dashboard_applications.html` (exists, needs enhancement)
**API Endpoint:** Create `/api/v2/dashboard/applications` in dashboard_api_v2.py

**Features:**
- Display all job applications with filtering
- Filters: status (all/sent/pending/failed), date range, company
- Sorting: date, company, status
- Pagination (20 per page)
- Use materialized view `application_summary_mv` for performance
- Show: job title, company, status, documents sent, coherence score, date

**Alpine.js State:**
```javascript
{
  applications: [],
  filters: { status: 'all', company: '', dateFrom: '', dateTo: '' },
  sort: { field: 'created_at', direction: 'desc' },
  pagination: { page: 1, perPage: 20, total: 0 }
}
```

### 2. Analytics View
**Route:** `/dashboard/analytics`
**Template:** `dashboard_analytics.html` (exists, needs charts)
**API Endpoints:** Use existing `/api/v2/dashboard/metrics/timeseries`

**Charts to Implement:**
1. **Scraping Velocity** (Line chart)
   - Jobs scraped over time (7d/30d)
   - Daily granularity

2. **Application Success Rate** (Line chart)
   - Success rate over time
   - Applications sent vs successful

3. **Pipeline Conversion Funnel** (Bar chart)
   - Raw → Cleaned → Analyzed → Eligible → Applied
   - Show drop-off at each stage

4. **AI Analysis Usage** (Area chart)
   - AI requests over time
   - Token usage if available

**Chart.js Integration:**
- Use Chart.js (already loaded)
- Dark theme compatible colors
- Responsive canvas sizing
- Interactive tooltips

### 3. Schema View
**Route:** `/dashboard/schema`
**Template:** Create `dashboard_schema.html`
**Source:** Use existing `frontend_templates/database_schema.html` as base

**Features:**
- Display database schema visualization
- Table relationships diagram
- Table details (columns, types, relationships)
- Search/filter tables
- Responsive layout

## Technical Constraints
- Flask runs on port 5001
- Database at host.docker.internal:5432
- Use materialized views for performance
- Follow existing code patterns in dashboard_api_v2.py
- Alpine.js for frontend state management
- Chart.js for visualizations
- No authentication required (auto-auth in debug mode)

## Success Criteria
- All three routes accessible and working
- Applications view shows data with working filters
- Analytics view displays all 4 charts with real data
- Schema view shows database structure
- No performance degradation (<100ms response time)
- Mobile responsive design
- No console errors

## Out of Scope
- Real-time updates (Phase 2 already has SSE)
- Export functionality (Phase 4)
- Advanced search (Phase 3)
- User authentication changes
