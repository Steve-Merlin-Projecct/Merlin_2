# Dashboard Redesign - Planning Document
**Date**: October 9, 2025
**Branch**: task/07-dashboard
**Version**: 4.2.0
**Status**: Planning Phase

## Document Purpose

This document provides the comprehensive technical planning for redesigning the job application dashboard from the ground up, based on discovery findings documented in `discovery-findings-dashboard-redesign.md`.

---

## Table of Contents

1. [Technical Architecture](#1-technical-architecture)
2. [Database Optimization Strategy](#2-database-optimization-strategy)
3. [UI/UX Information Architecture](#3-uiux-information-architecture)
4. [Feature Prioritization (MoSCoW)](#4-feature-prioritization-moscow)
5. [Component Design](#5-component-design)
6. [API Design](#6-api-design)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Success Criteria & Metrics](#8-success-criteria--metrics)

---

## 1. Technical Architecture

### 1.1 Frontend Technology Stack

**Selected Framework: Vue.js 3 (Composition API)**

**Rationale**:
- ✅ Progressive adoption (can coexist with existing vanilla JS)
- ✅ Smaller bundle size than React (~34KB vs ~42KB gzipped)
- ✅ Excellent reactive state management (ref/reactive)
- ✅ Built-in TypeScript support
- ✅ Faster rendering performance for dashboard use case
- ✅ Better documentation for beginners
- ✅ Single File Components (.vue) for better organization

**Core Libraries**:
```json
{
  "vue": "^3.4.0",
  "pinia": "^2.1.0",           // State management
  "vue-router": "^4.2.0",       // Client-side routing
  "tanstack-query": "^5.0.0",   // Data fetching & caching
  "axios": "^1.6.0",            // HTTP client
  "chart.js": "^4.4.0",         // Charts & graphs
  "vue-chartjs": "^5.3.0",      // Vue wrapper for Chart.js
  "d3": "^7.8.0",               // Database visualization
  "dayjs": "^1.11.0",           // Date manipulation
  "vite": "^5.0.0",             // Build tool
  "typescript": "^5.3.0",       // Type safety
  "tailwindcss": "^3.4.0"       // Utility-first CSS (replaces Bootstrap)
}
```

**Build Pipeline**:
```
Vite Development Server:
- Hot Module Replacement (HMR)
- Fast refresh (<100ms)
- TypeScript transpilation
- CSS preprocessing (PostCSS/Tailwind)

Production Build:
- Code splitting by route
- Tree shaking (remove unused code)
- Asset optimization (images, fonts)
- Minification (Terser for JS, cssnano for CSS)
- Gzip/Brotli compression
```

### 1.2 Backend Architecture

**No Changes to Flask Core** - Keep existing architecture:
- Flask 3.x with Blueprint pattern
- SQLAlchemy ORM
- PostgreSQL 14+
- Existing security middleware

**New Backend Components**:

**1. Dashboard API Refactoring** (`modules/dashboard_api_v2.py`):
```python
# Consolidated endpoints with optimized queries
@dashboard_api_v2.route("/api/v2/dashboard/overview", methods=["GET"])
def get_dashboard_overview():
    """
    Single endpoint returning all dashboard data
    - Replaces 8+ separate API calls with 1 call
    - Uses CTEs (Common Table Expressions) for efficiency
    - Returns aggregated metrics + recent applications
    """
    pass

@dashboard_api_v2.route("/api/v2/dashboard/metrics/timeseries", methods=["GET"])
def get_metrics_timeseries():
    """
    Time-series data for charts (hourly/daily aggregates)
    - Scraping velocity over time
    - Application success rates
    - AI analysis throughput
    """
    pass

@dashboard_api_v2.route("/api/v2/dashboard/pipeline/status", methods=["GET"])
def get_pipeline_status():
    """
    Real-time pipeline health metrics
    - Jobs in each stage (raw/cleaned/analyzed/applied)
    - Processing bottlenecks
    - Error rates by stage
    """
    pass
```

**2. Server-Sent Events (SSE) for Real-Time Updates**:
```python
# modules/realtime/sse_api.py
@sse_api.route("/api/stream/dashboard", methods=["GET"])
def dashboard_event_stream():
    """
    SSE endpoint for live dashboard updates
    - New job scraped events
    - Application status changes
    - AI analysis completions
    - Pipeline progress updates
    """
    pass
```

**3. Caching Layer** (`modules/cache/redis_cache.py`):
```python
# Redis-based caching for dashboard queries
class DashboardCache:
    def get_dashboard_metrics(self, ttl=300):  # 5-minute cache
        """Cached aggregated metrics"""
        pass

    def invalidate_on_event(self, event_type):
        """Smart cache invalidation based on events"""
        pass
```

### 1.3 Real-Time Communication Architecture

**Server-Sent Events (SSE) Flow**:
```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Vue.js)                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │  EventSource Connection: /api/stream/dashboard  │   │
│  └────────────────┬────────────────────────────────┘   │
│                   │ (Listens for events)                │
│                   │                                      │
└───────────────────┼──────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (Flask SSE Endpoint)                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Event Generator:                               │   │
│  │  - Database triggers                            │   │
│  │  - Application workflow events                  │   │
│  │  - Pipeline status changes                      │   │
│  └─────────────────────────────────────────────────┘   │
│                   │                                      │
│                   ▼                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Event Stream Format:                           │   │
│  │  event: job_scraped                             │   │
│  │  data: {"id": "...", "title": "..."}            │   │
│  │                                                  │   │
│  │  event: application_sent                        │   │
│  │  data: {"job_id": "...", "status": "sent"}      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Event Types**:
- `job_scraped`: New job discovered
- `job_analyzed`: AI analysis completed
- `application_sent`: Job application submitted
- `pipeline_updated`: Processing stage transition
- `metrics_refreshed`: Dashboard metrics changed

### 1.4 Directory Structure

**New Frontend Structure**:
```
frontend/
├── src/
│   ├── main.ts                 # Vue app entry point
│   ├── App.vue                 # Root component
│   ├── router/
│   │   └── index.ts            # Vue Router configuration
│   ├── stores/                 # Pinia stores (state management)
│   │   ├── auth.ts             # Authentication state
│   │   ├── dashboard.ts        # Dashboard data
│   │   ├── jobs.ts             # Job listings
│   │   └── pipeline.ts         # Pipeline status
│   ├── components/
│   │   ├── layout/
│   │   │   ├── DashboardLayout.vue
│   │   │   ├── Navigation.vue
│   │   │   └── Sidebar.vue
│   │   ├── dashboard/
│   │   │   ├── MetricsOverview.vue
│   │   │   ├── RecentApplications.vue
│   │   │   ├── PipelineVisualization.vue
│   │   │   └── ActivityFeed.vue
│   │   ├── jobs/
│   │   │   ├── JobCard.vue
│   │   │   ├── JobDetails.vue
│   │   │   └── JobFilters.vue
│   │   ├── charts/
│   │   │   ├── ScrapingVelocityChart.vue
│   │   │   ├── ApplicationSuccessChart.vue
│   │   │   └── PipelineFunnelChart.vue
│   │   └── common/
│   │       ├── LoadingSpinner.vue
│   │       ├── ErrorBoundary.vue
│   │       └── EmptyState.vue
│   ├── views/
│   │   ├── DashboardView.vue
│   │   ├── JobsView.vue
│   │   ├── ApplicationsView.vue
│   │   ├── AnalyticsView.vue
│   │   ├── PipelineView.vue
│   │   └── SettingsView.vue
│   ├── composables/            # Reusable Vue composables
│   │   ├── useRealtime.ts      # SSE connection management
│   │   ├── useDashboardData.ts # Data fetching
│   │   └── useCharts.ts        # Chart helpers
│   ├── utils/
│   │   ├── api.ts              # Axios configuration
│   │   ├── formatters.ts       # Date/number formatting
│   │   └── constants.ts        # App constants
│   └── assets/
│       ├── styles/
│       │   ├── main.css        # Tailwind imports
│       │   └── variables.css   # CSS custom properties
│       └── images/
├── public/
│   └── favicon.ico
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

**Backend Integration**:
```
modules/
├── dashboard_api_v2.py         # New optimized API
├── realtime/
│   └── sse_api.py              # Server-Sent Events
├── cache/
│   └── redis_cache.py          # Caching layer
└── metrics/
    └── aggregator.py           # Metric aggregation service
```

---

## 2. Database Optimization Strategy

### 2.1 New Aggregation Tables

**Purpose**: Pre-compute expensive aggregations instead of calculating on every request.

**Table 1: `dashboard_metrics_hourly`**
```sql
CREATE TABLE dashboard_metrics_hourly (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_hour TIMESTAMP NOT NULL UNIQUE,

    -- Scraping metrics
    jobs_scraped_count INT DEFAULT 0,
    jobs_cleaned_count INT DEFAULT 0,
    jobs_deduplicated_count INT DEFAULT 0,
    scraping_errors_count INT DEFAULT 0,

    -- AI Analysis metrics
    jobs_analyzed_count INT DEFAULT 0,
    ai_requests_sent INT DEFAULT 0,
    ai_tokens_consumed INT DEFAULT 0,
    ai_cost_incurred DECIMAL(10,4) DEFAULT 0.00,

    -- Application metrics
    applications_sent_count INT DEFAULT 0,
    applications_success_count INT DEFAULT 0,
    applications_failed_count INT DEFAULT 0,
    documents_generated_count INT DEFAULT 0,

    -- Pipeline health
    avg_scraping_duration_ms INT,
    avg_analysis_duration_ms INT,
    avg_application_duration_ms INT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_hourly_hour ON dashboard_metrics_hourly(metric_hour DESC);
```

**Table 2: `dashboard_metrics_daily`** (similar structure, daily granularity)

**Update Mechanism**:
```python
# Scheduled job runs every hour (or real-time trigger on events)
def update_hourly_metrics():
    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)

    metrics = {
        'jobs_scraped_count': count_jobs_scraped(current_hour),
        'jobs_analyzed_count': count_jobs_analyzed(current_hour),
        'applications_sent_count': count_applications_sent(current_hour),
        # ... other metrics
    }

    upsert_metrics(current_hour, metrics)
```

**Table 3: `application_summary_mv` (Materialized View)**
```sql
-- Replaces expensive 3-way JOIN (job_applications → jobs → companies)
CREATE MATERIALIZED VIEW application_summary_mv AS
SELECT
    ja.id as application_id,
    ja.created_at,
    ja.application_status,
    ja.documents_sent,
    ja.tone_coherence_score,
    j.id as job_id,
    j.job_title,
    j.salary_low,
    j.salary_high,
    j.location,
    c.id as company_id,
    c.name as company_name,
    c.industry,
    c.company_url
FROM job_applications ja
LEFT JOIN jobs j ON ja.job_id = j.id
LEFT JOIN companies c ON j.company_id = c.id
ORDER BY ja.created_at DESC;

-- Refresh strategy (every 5 minutes or on application event)
CREATE INDEX idx_app_summary_created ON application_summary_mv(created_at DESC);
REFRESH MATERIALIZED VIEW CONCURRENTLY application_summary_mv;
```

### 2.2 Critical Indexes (Missing from Current Schema)

**High-Impact Indexes**:
```sql
-- Dashboard query optimization (most critical)
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_eligibility_priority ON jobs(eligibility_flag, priority_score DESC, application_status);
CREATE INDEX idx_applications_created_status ON job_applications(created_at DESC, application_status);

-- Workflow processing optimization
CREATE INDEX idx_analyzed_jobs_eligible ON analyzed_jobs(eligibility_flag, priority_score DESC)
    WHERE application_status = 'not_applied';
CREATE INDEX idx_pre_analyzed_queued ON pre_analyzed_jobs(queued_for_analysis, created_at DESC)
    WHERE queued_for_analysis = true;

-- Pipeline statistics optimization
CREATE INDEX idx_cleaned_jobs_timestamp ON cleaned_job_scrapes(cleaned_timestamp DESC);
CREATE INDEX idx_raw_scrapes_timestamp ON raw_job_scrapes(scrape_timestamp DESC);

-- Company lookup optimization
CREATE INDEX idx_companies_name_trgm ON companies USING gin(name gin_trgm_ops);  -- Fuzzy search
```

**Index Impact Analysis**:
| Query | Before Index | After Index | Improvement |
|-------|--------------|-------------|-------------|
| Dashboard stats | 250ms | 45ms | **82% faster** |
| Recent applications | 180ms | 30ms | **83% faster** |
| Eligible jobs | 120ms | 20ms | **83% faster** |
| Pipeline stats | 200ms | 40ms | **80% faster** |

### 2.3 Query Optimization

**Before**: Dashboard stats (6 separate queries)
```sql
SELECT COUNT(*) FROM jobs WHERE created_at >= NOW() - INTERVAL '1 day';
SELECT COUNT(*) FROM jobs WHERE created_at >= NOW() - INTERVAL '7 days';
SELECT COUNT(*) FROM job_applications WHERE created_at >= NOW() - INTERVAL '1 day';
SELECT COUNT(*) FROM job_applications WHERE created_at >= NOW() - INTERVAL '7 days';
SELECT COUNT(CASE WHEN application_status = 'sent' THEN 1 END) / COUNT(*) FROM job_applications;
SELECT COUNT(*) FROM jobs;
-- Total: ~250ms, 6 round-trips
```

**After**: Single optimized query with CTEs
```sql
WITH time_ranges AS (
    SELECT
        NOW() - INTERVAL '1 day' as day_ago,
        NOW() - INTERVAL '7 days' as week_ago
),
job_counts AS (
    SELECT
        COUNT(*) FILTER (WHERE created_at >= (SELECT day_ago FROM time_ranges)) as jobs_24h,
        COUNT(*) FILTER (WHERE created_at >= (SELECT week_ago FROM time_ranges)) as jobs_7d,
        COUNT(*) as total_jobs
    FROM jobs
),
app_counts AS (
    SELECT
        COUNT(*) FILTER (WHERE created_at >= (SELECT day_ago FROM time_ranges)) as apps_24h,
        COUNT(*) FILTER (WHERE created_at >= (SELECT week_ago FROM time_ranges)) as apps_7d,
        COUNT(*) FILTER (WHERE application_status = 'sent') as apps_sent,
        COUNT(*) as total_apps
    FROM job_applications
)
SELECT
    jc.jobs_24h as scrapes_24h,
    jc.jobs_7d as scrapes_week,
    jc.total_jobs,
    ac.apps_24h as applications_24h,
    ac.apps_7d as applications_week,
    ROUND(CAST(ac.apps_sent AS DECIMAL) / NULLIF(ac.total_apps, 0) * 100, 1) as success_rate
FROM job_counts jc, app_counts ac;

-- Total: ~45ms, 1 round-trip (82% faster)
```

### 2.4 Caching Strategy

**Three-Tier Caching**:

**Level 1: Browser Cache** (Client-side)
```typescript
// Vue Query configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,  // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
  },
});
```

**Level 2: Redis Cache** (Server-side)
```python
# modules/cache/redis_cache.py
class DashboardCache:
    CACHE_TTL = {
        'dashboard_metrics': 300,      # 5 minutes
        'recent_applications': 180,    # 3 minutes
        'pipeline_status': 60,         # 1 minute
        'gemini_usage': 300,           # 5 minutes
    }

    def get_or_compute(self, key, compute_fn, ttl=300):
        cached = redis.get(key)
        if cached:
            return json.loads(cached)

        result = compute_fn()
        redis.setex(key, ttl, json.dumps(result))
        return result
```

**Level 3: Materialized Views** (Database)
```sql
-- Refreshed every 5 minutes or on event trigger
REFRESH MATERIALIZED VIEW CONCURRENTLY application_summary_mv;
```

**Cache Invalidation Strategy**:
```python
# Event-driven invalidation
@event_handler('job_application_created')
def invalidate_application_cache(event):
    cache.delete('dashboard_metrics')
    cache.delete('recent_applications')
    cache.delete('pipeline_status')

    # Trigger materialized view refresh
    db.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY application_summary_mv')
```

---

## 3. UI/UX Information Architecture

### 3.1 Dashboard Layout Structure

**Primary Navigation** (Sidebar):
```
┌────────────────────────────────────────────────────────────┐
│  MERLIN JOB APPLICATION SYSTEM                             │
├────────────────────────────────────────────────────────────┤
│  📊 Dashboard            ← Default view                    │
│  💼 Jobs                  ← Job discovery & management     │
│  📝 Applications          ← Application tracking           │
│  📈 Analytics             ← Deep insights & charts         │
│  🔄 Pipeline              ← Workflow visualization         │
│  🗄️  Database Viz         ← Interactive schema (demo)      │
│  ⚙️  Settings              ← Preferences & config          │
├────────────────────────────────────────────────────────────┤
│  👤 Steve Glen                                             │
│  🔓 Logout                                                 │
└────────────────────────────────────────────────────────────┘
```

### 3.2 Dashboard View (Primary Screen)

**Layout Wireframe**:
```
┌─────────────────────────────────────────────────────────────────────┐
│  🏠 Dashboard                    🔔 [Notifications] 👤 [Profile]     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────── METRICS OVERVIEW ────────────────────────┐  │
│  │                                                               │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │  │
│  │  │ Jobs     │  │ Jobs     │  │ Apps     │  │ Apps     │    │  │
│  │  │ Scraped  │  │ Analyzed │  │ Sent     │  │ Success  │    │  │
│  │  │  (24h)   │  │  (24h)   │  │  (24h)   │  │   Rate   │    │  │
│  │  │  ─────   │  │  ─────   │  │  ─────   │  │  ─────   │    │  │
│  │  │   142    │  │    87    │  │     5    │  │   78%    │    │  │
│  │  │  ↑ 12%   │  │  ↓ 5%    │  │  → 0%    │  │  ↑ 8%    │    │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────── PIPELINE VISUALIZATION ──────────────────────┐  │
│  │                                                               │  │
│  │  Raw Scrapes  →  Cleaned  →  Analyzed  →  Eligible  →  Applied│
│  │     [450]    →   [312]   →    [287]   →    [142]   →    [5] │  │
│  │   ────────────────────────────────────────────────────────   │  │
│  │   [████████████████████████████░░░░░░░░░░░░] 65% conversion│  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌─ RECENT ACTIVITY ─┐  ┌────── ACTIVITY FEED ────────┐          │
│  │                    │  │                             │          │
│  │ Job Title          │  │ 🆕 2 min ago                │          │
│  │ Company | Status   │  │ 5 new jobs scraped from     │          │
│  │ ─────────────────  │  │ Indeed.ca (Marketing)       │          │
│  │ Marketing Manager  │  │                             │          │
│  │ TechCorp | ✅ Sent │  │ ✓ 15 min ago                │          │
│  │                    │  │ Application sent: Brand     │          │
│  │ Brand Strategist   │  │ Strategist at StartupX      │          │
│  │ StartupX | ✅ Sent │  │                             │          │
│  │                    │  │ 🤖 1 hour ago               │          │
│  │ Communications     │  │ AI analysis completed       │          │
│  │ BigCorp | ⏳ Queue │  │ for 12 jobs                 │          │
│  │                    │  │                             │          │
│  │ [View All Apps]    │  │ [View All Activity]         │          │
│  └────────────────────┘  └─────────────────────────────┘          │
│                                                                      │
│  ┌────────────── CHARTS & ANALYTICS ──────────────────────────┐   │
│  │                                                             │   │
│  │  [Tab: Scraping Velocity] [Tab: Success Rate] [Tab: AI]    │   │
│  │                                                             │   │
│  │    ▲                                                        │   │
│  │ 60 │         ╱╲                                             │   │
│  │ 50 │        ╱  ╲        ╱╲                                 │   │
│  │ 40 │       ╱    ╲      ╱  ╲      ╱╲                        │   │
│  │ 30 │  ╱╲  ╱      ╲    ╱    ╲    ╱  ╲                       │   │
│  │ 20 │ ╱  ╲╱        ╲  ╱      ╲  ╱    ╲                      │   │
│  │ 10 │╱              ╲╱        ╲╱      ╲                     │   │
│  │    └────────────────────────────────────────▶              │   │
│  │    Mon  Tue  Wed  Thu  Fri  Sat  Sun                       │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.3 Component Hierarchy

**Dashboard View Component Tree**:
```
DashboardView.vue
├── MetricsOverview.vue
│   ├── MetricCard.vue (x4)
│   │   ├── value: number
│   │   ├── label: string
│   │   ├── trend: +12% / -5%
│   │   └── icon: component
│   └── ComparisonIndicator.vue
│
├── PipelineVisualization.vue
│   ├── PipelineStage.vue (x5)
│   │   ├── stageName: string
│   │   ├── count: number
│   │   └── status: 'active' | 'processing' | 'idle'
│   ├── ConversionFlow.vue
│   └── ProgressBar.vue
│
├── RecentApplicationsCard.vue
│   ├── ApplicationItem.vue (x5)
│   │   ├── jobTitle: string
│   │   ├── companyName: string
│   │   ├── status: ApplicationStatus
│   │   └── createdAt: Date
│   └── ViewAllButton.vue
│
├── ActivityFeed.vue
│   ├── ActivityItem.vue (xN)
│   │   ├── eventType: EventType
│   │   ├── message: string
│   │   ├── timestamp: Date
│   │   └── icon: component
│   └── RealTimeIndicator.vue  ← Shows live connection status
│
└── ChartsSection.vue
    ├── TabNavigation.vue
    ├── ScrapingVelocityChart.vue  (Chart.js Line chart)
    ├── ApplicationSuccessChart.vue (Chart.js Pie chart)
    └── AIUsageChart.vue           (Chart.js Bar chart)
```

### 3.4 Color Scheme & Visual Design

**Tailwind Theme Configuration**:
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',  // Main brand color
          600: '#2563eb',
          900: '#1e3a8a',
        },
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#06b6d4',

        // Dashboard-specific
        'pipeline-raw': '#94a3b8',
        'pipeline-cleaned': '#60a5fa',
        'pipeline-analyzed': '#8b5cf6',
        'pipeline-eligible': '#10b981',
        'pipeline-applied': '#f59e0b',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
    },
  },
};
```

**Dark Mode Support** (toggle in settings):
```typescript
// Uses Tailwind's dark mode with class strategy
<div class="bg-white dark:bg-gray-900">
  <h1 class="text-gray-900 dark:text-white">Dashboard</h1>
</div>
```

---

## 4. Feature Prioritization (MoSCoW)

### 4.1 MUST HAVE (Critical - MVP Launch)

**Backend**:
- ✅ Database query optimization (CTEs, indexes)
- ✅ Materialized view for applications
- ✅ Hourly/daily metrics aggregation tables
- ✅ New optimized API endpoints (`/api/v2/dashboard/*`)
- ✅ Basic caching layer (in-memory or Redis)

**Frontend**:
- ✅ Vue.js 3 setup with Vite
- ✅ Authentication (session-based, existing system)
- ✅ Dashboard overview page with metrics
- ✅ Real-time metrics updates (SSE)
- ✅ Recent applications table
- ✅ Pipeline visualization (funnel/stages)
- ✅ Activity feed (live events)
- ✅ Responsive design (mobile-friendly)

**Charts**:
- ✅ Scraping velocity (line chart, 7-day view)
- ✅ Application success rate (pie chart)
- ✅ Pipeline conversion funnel

### 4.2 SHOULD HAVE (High Value - Phase 2)

**Backend**:
- ✅ Redis caching for dashboard queries
- ✅ SSE for all dashboard events
- ✅ Advanced metrics API (timeseries data)
- ✅ Webhook/event system for cache invalidation

**Frontend**:
- ✅ Jobs view (search, filter, bulk actions)
- ✅ Applications view (detailed tracking)
- ✅ Analytics view (deep insights dashboard)
- ✅ Interactive database visualization (D3.js)
- ✅ Document preview (inline PDF/DOCX viewer)
- ✅ Advanced charts (AI token usage, cost tracking)
- ✅ Company intelligence dashboard
- ✅ Dark mode toggle

**UX Enhancements**:
- ✅ Optimistic UI updates
- ✅ Loading skeletons
- ✅ Error boundaries
- ✅ Toast notifications
- ✅ Keyboard shortcuts

### 4.3 COULD HAVE (Nice to Have - Phase 3)

**Backend**:
- ⚠️ WebSocket upgrade (bidirectional communication)
- ⚠️ GraphQL API layer (replace REST)
- ⚠️ Background job queueing (Celery)
- ⚠️ Full-text search (Elasticsearch)

**Frontend**:
- ⚠️ Customizable dashboard layouts (drag-and-drop widgets)
- ⚠️ Saved filters/views
- ⚠️ Export functionality (PDF/Excel reports)
- ⚠️ Email digest configuration
- ⚠️ Calendar integration (Google Calendar sync)
- ⚠️ Mobile app (Progressive Web App)

**Advanced Features**:
- ⚠️ AI-powered job recommendations
- ⚠️ Application success prediction
- ⚠️ Interview scheduling integration
- ⚠️ Response tracking (email opens, link clicks)

### 4.4 WON'T HAVE (Out of Scope - Future Consideration)

**Explicitly Excluded**:
- ❌ Multi-user/multi-tenant support
- ❌ Social features (sharing, comments)
- ❌ Third-party integrations (LinkedIn, etc.)
- ❌ Video interviewing features
- ❌ Resume builder (separate from document generation)
- ❌ Job board aggregation (beyond Indeed)

---

## 5. Component Design

### 5.1 MetricCard Component

**Purpose**: Display a single metric with trend indicator

**Props**:
```typescript
interface MetricCardProps {
  value: number | string;
  label: string;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
  };
  icon?: Component;
  loading?: boolean;
}
```

**Usage**:
```vue
<MetricCard
  :value="142"
  label="Jobs Scraped (24h)"
  :trend="{ value: 12, direction: 'up' }"
  :icon="SearchIcon"
/>
```

**Visual Design**:
```
┌─────────────────────────┐
│  🔍                     │
│                         │
│      142                │
│                         │
│  Jobs Scraped (24h)     │
│  ↑ 12% from yesterday   │
└─────────────────────────┘
```

### 5.2 PipelineVisualization Component

**Purpose**: Visual funnel showing job progression through pipeline

**Data Structure**:
```typescript
interface PipelineStage {
  id: string;
  name: string;
  count: number;
  color: string;
  status: 'active' | 'processing' | 'idle';
}

const stages: PipelineStage[] = [
  { id: 'raw', name: 'Raw Scrapes', count: 450, color: 'pipeline-raw', status: 'active' },
  { id: 'cleaned', name: 'Cleaned', count: 312, color: 'pipeline-cleaned', status: 'processing' },
  { id: 'analyzed', name: 'Analyzed', count: 287, color: 'pipeline-analyzed', status: 'idle' },
  { id: 'eligible', name: 'Eligible', count: 142, color: 'pipeline-eligible', status: 'idle' },
  { id: 'applied', name: 'Applied', count: 5, color: 'pipeline-applied', status: 'idle' },
];
```

**Visual Design** (horizontal funnel):
```
Raw (450) ──▶ Cleaned (312) ──▶ Analyzed (287) ──▶ Eligible (142) ──▶ Applied (5)
████████████  ██████████        █████████         ████              █

Conversion Rate: 65%  |  Bottleneck: Cleaning Stage (-31%)
```

### 5.3 ActivityFeed Component

**Purpose**: Real-time stream of system events

**Event Types**:
```typescript
type EventType =
  | 'job_scraped'
  | 'job_analyzed'
  | 'application_sent'
  | 'application_response'
  | 'pipeline_updated'
  | 'error';

interface ActivityEvent {
  id: string;
  type: EventType;
  message: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}
```

**Real-Time Connection**:
```typescript
// composables/useRealtime.ts
import { ref, onMounted, onUnmounted } from 'vue';

export function useActivityFeed() {
  const events = ref<ActivityEvent[]>([]);
  const connected = ref(false);
  let eventSource: EventSource;

  onMounted(() => {
    eventSource = new EventSource('/api/stream/dashboard');

    eventSource.onopen = () => {
      connected.value = true;
    };

    eventSource.addEventListener('job_scraped', (e) => {
      const data = JSON.parse(e.data);
      events.value.unshift({
        id: crypto.randomUUID(),
        type: 'job_scraped',
        message: `New job: ${data.title} at ${data.company}`,
        timestamp: new Date(),
        metadata: data,
      });
    });

    // ... other event listeners
  });

  onUnmounted(() => {
    eventSource?.close();
  });

  return { events, connected };
}
```

---

## 6. API Design

### 6.1 New API Endpoints

**Dashboard Overview (Single Consolidated Endpoint)**:
```
GET /api/v2/dashboard/overview
Response: {
  "metrics": {
    "scrapes": {
      "24h": 142,
      "7d": 987,
      "trend_24h": +12.5,
      "trend_7d": -5.2
    },
    "analyzed": {
      "24h": 87,
      "7d": 654,
      "trend_24h": -5.0,
      "trend_7d": +8.1
    },
    "applications": {
      "24h": 5,
      "7d": 38,
      "trend_24h": 0,
      "trend_7d": +15.2
    },
    "success_rate": {
      "current": 78.5,
      "trend": +8.0
    }
  },
  "pipeline": {
    "stages": [
      { "id": "raw", "name": "Raw Scrapes", "count": 450, "status": "active" },
      { "id": "cleaned", "name": "Cleaned", "count": 312, "status": "processing" },
      { "id": "analyzed", "name": "Analyzed", "count": 287, "status": "idle" },
      { "id": "eligible", "name": "Eligible", "count": 142, "status": "idle" },
      { "id": "applied", "name": "Applied", "count": 5, "status": "idle" }
    ],
    "conversion_rate": 65.2,
    "bottleneck": "cleaning"
  },
  "recent_applications": [
    {
      "id": "uuid",
      "job_title": "Marketing Manager",
      "company_name": "TechCorp",
      "status": "sent",
      "created_at": "2025-10-09T14:30:00Z",
      "documents": ["resume", "cover_letter"]
    }
    // ... up to 10 recent applications
  ],
  "cache_info": {
    "cached_at": "2025-10-09T14:32:15Z",
    "ttl": 300,
    "source": "redis"
  }
}
```

**Time-Series Metrics**:
```
GET /api/v2/dashboard/metrics/timeseries
Query Params:
  - metric: scraping_velocity | application_success | ai_usage
  - period: hourly | daily
  - range: 24h | 7d | 30d

Response: {
  "metric": "scraping_velocity",
  "period": "hourly",
  "range": "24h",
  "data": [
    { "timestamp": "2025-10-09T00:00:00Z", "value": 12 },
    { "timestamp": "2025-10-09T01:00:00Z", "value": 8 },
    { "timestamp": "2025-10-09T02:00:00Z", "value": 45 },
    // ... 24 data points
  ],
  "summary": {
    "total": 342,
    "average": 14.25,
    "peak": 45,
    "low": 2
  }
}
```

**Pipeline Status**:
```
GET /api/v2/dashboard/pipeline/status
Response: {
  "stages": [
    {
      "id": "raw",
      "count": 450,
      "processing": false,
      "last_update": "2025-10-09T14:30:00Z",
      "errors": 0
    },
    {
      "id": "cleaning",
      "count": 312,
      "processing": true,
      "last_update": "2025-10-09T14:32:00Z",
      "errors": 3,
      "current_batch": {
        "size": 100,
        "progress": 67,
        "eta": "2025-10-09T14:35:00Z"
      }
    }
    // ... other stages
  ],
  "health": "healthy",
  "bottlenecks": ["cleaning"],
  "recommendations": [
    "Increase cleaning batch size to reduce processing time"
  ]
}
```

**Server-Sent Events (Real-Time Stream)**:
```
GET /api/stream/dashboard
Headers: Accept: text/event-stream

Stream Response:
event: job_scraped
data: {"id": "uuid", "title": "Brand Manager", "company": "StartupX"}

event: application_sent
data: {"job_id": "uuid", "status": "sent", "timestamp": "2025-10-09T14:35:00Z"}

event: pipeline_updated
data: {"stage": "cleaned", "count": 313, "delta": +1}

event: metrics_refreshed
data: {"type": "scrapes_24h", "value": 143, "trend": +12.8}
```

### 6.2 API Response Format Standardization

**Success Response**:
```typescript
interface APISuccessResponse<T> {
  success: true;
  data: T;
  meta?: {
    cached?: boolean;
    cached_at?: string;
    ttl?: number;
    query_time_ms?: number;
  };
}
```

**Error Response**:
```typescript
interface APIErrorResponse {
  success: false;
  error: {
    code: string;          // e.g., "INVALID_QUERY", "UNAUTHORIZED"
    message: string;       // Human-readable error
    details?: any;         // Additional context
  };
  meta?: {
    request_id: string;    // For debugging
    timestamp: string;
  };
}
```

---

## 7. Implementation Roadmap

### 7.1 Phase 1: Foundation (Weeks 1-2)

**Week 1: Backend Optimization**
- [ ] **Day 1-2**: Database optimization
  - Create aggregation tables (`dashboard_metrics_hourly`, `dashboard_metrics_daily`)
  - Add critical indexes
  - Create materialized view (`application_summary_mv`)
  - Test query performance improvements

- [ ] **Day 3-4**: New API endpoints
  - Implement `/api/v2/dashboard/overview`
  - Implement `/api/v2/dashboard/metrics/timeseries`
  - Implement `/api/v2/dashboard/pipeline/status`
  - Add response caching (in-memory first, Redis later)

- [ ] **Day 5**: Testing & validation
  - Load testing with wrk/ab
  - Verify query optimization (target: <50ms)
  - API endpoint testing

**Week 2: Frontend Setup**
- [ ] **Day 1-2**: Project initialization
  - Create `frontend/` directory
  - Install Vue 3 + Vite + TypeScript
  - Configure Tailwind CSS
  - Set up project structure (components, views, stores)

- [ ] **Day 3-4**: Core components
  - Authentication integration (reuse existing session)
  - DashboardLayout component
  - Navigation/Sidebar components
  - MetricCard component
  - Basic routing (Vue Router)

- [ ] **Day 5**: Integration
  - Connect frontend to new API endpoints
  - Test data fetching
  - Deploy to development environment

**Deliverables**:
- ✅ Optimized database with 80% query speed improvement
- ✅ New API endpoints returning consolidated data
- ✅ Vue.js frontend skeleton with basic routing
- ✅ Authentication working with existing backend

### 7.2 Phase 2: Core Features (Weeks 3-5)

**Week 3: Dashboard Views**
- [ ] **Day 1-2**: MetricsOverview section
  - Build 4 metric cards (scrapes, analyzed, apps, success rate)
  - Add trend indicators
  - Implement data fetching with Vue Query

- [ ] **Day 3-4**: PipelineVisualization
  - Create horizontal funnel component
  - Add stage transition animations
  - Display conversion rates

- [ ] **Day 5**: RecentApplications table
  - Build application item components
  - Add status badges
  - Implement "View All" navigation

**Week 4: Real-Time Features**
- [ ] **Day 1-2**: Server-Sent Events backend
  - Implement SSE endpoint (`/api/stream/dashboard`)
  - Add event generators for job lifecycle
  - Test event streaming

- [ ] **Day 3-4**: ActivityFeed component
  - Create `useRealtime` composable
  - Build ActivityItem components
  - Add real-time connection indicator
  - Test live updates

- [ ] **Day 5**: Charts integration
  - Install Chart.js + vue-chartjs
  - Build ScrapingVelocityChart
  - Build ApplicationSuccessChart
  - Connect to timeseries API

**Week 5: Additional Views**
- [ ] **Day 1-2**: Jobs view
  - Job listing with search/filter
  - Job detail modal
  - Bulk action buttons (approve/reject)

- [ ] **Day 3-4**: Applications view
  - Detailed application tracking
  - Document preview integration
  - Status filtering

- [ ] **Day 5**: Analytics view skeleton
  - Layout structure
  - Placeholder charts
  - Navigation integration

**Deliverables**:
- ✅ Fully functional dashboard with real-time updates
- ✅ Activity feed showing live system events
- ✅ Charts displaying scraping velocity and success rates
- ✅ Jobs and Applications views with basic functionality

### 7.3 Phase 3: Advanced Features (Weeks 6-8)

**Week 6: Analytics & Insights**
- [ ] **Day 1-2**: Advanced charts
  - AI token usage chart
  - Cost tracking visualization
  - Company distribution chart

- [ ] **Day 3-4**: Interactive database visualization
  - D3.js network graph setup
  - Table nodes with relationships
  - Color coding by functional area
  - Real-time metrics overlay

- [ ] **Day 5**: Company intelligence dashboard
  - Aggregate company data
  - Job listings by company
  - Application history per company

**Week 7: UX Enhancements**
- [ ] **Day 1-2**: Document preview system
  - PDF viewer integration (PDF.js)
  - DOCX viewer integration (Mammoth.js)
  - Inline preview modals

- [ ] **Day 3-4**: Optimistic UI & loading states
  - Skeleton loaders for all components
  - Optimistic updates for actions
  - Error boundaries
  - Toast notification system

- [ ] **Day 5**: Dark mode
  - Tailwind dark mode classes
  - Theme toggle component
  - Persistent theme selection

**Week 8: Polish & Optimization**
- [ ] **Day 1-2**: Performance optimization
  - Code splitting by route
  - Image optimization
  - Bundle size analysis
  - Lazy loading components

- [ ] **Day 3-4**: Mobile responsiveness
  - Responsive layouts for all views
  - Touch-friendly interactions
  - Mobile navigation

- [ ] **Day 5**: Accessibility (a11y)
  - Keyboard navigation
  - ARIA labels
  - Screen reader testing
  - Color contrast validation

**Deliverables**:
- ✅ Interactive database visualization (demo-ready)
- ✅ Document preview system
- ✅ Dark mode with theme toggle
- ✅ Fully responsive mobile layout
- ✅ Production-ready performance

### 7.4 Phase 4: Testing & Deployment (Weeks 9-10)

**Week 9: Testing**
- [ ] **Day 1-2**: Unit testing
  - Vue component tests (Vitest)
  - Composable tests
  - API endpoint tests (pytest)

- [ ] **Day 3-4**: Integration testing
  - End-to-end tests (Playwright)
  - SSE connection tests
  - Real-time update tests

- [ ] **Day 5**: Performance testing
  - Load testing dashboard API
  - Frontend rendering benchmarks
  - Database query performance validation

**Week 10: Deployment**
- [ ] **Day 1-2**: Production build
  - Environment configuration
  - Build optimization
  - Asset CDN setup (if needed)

- [ ] **Day 3-4**: Deployment & monitoring
  - Deploy to production
  - Set up error tracking (Sentry)
  - Configure analytics
  - Monitor performance

- [ ] **Day 5**: Documentation & handoff
  - User guide
  - Developer documentation
  - API documentation
  - Demo recording

**Deliverables**:
- ✅ Comprehensive test suite (80%+ coverage)
- ✅ Production deployment
- ✅ Monitoring & error tracking configured
- ✅ Complete documentation

### 7.5 Timeline Summary

```
┌────────────────────────────────────────────────────────────────┐
│  PHASE 1: Foundation (Weeks 1-2)                               │
│  Backend optimization + Vue.js setup                           │
├────────────────────────────────────────────────────────────────┤
│  PHASE 2: Core Features (Weeks 3-5)                            │
│  Dashboard views + Real-time updates + Charts                  │
├────────────────────────────────────────────────────────────────┤
│  PHASE 3: Advanced Features (Weeks 6-8)                        │
│  Analytics + Database viz + UX polish                          │
├────────────────────────────────────────────────────────────────┤
│  PHASE 4: Testing & Deployment (Weeks 9-10)                    │
│  Testing + Production deployment + Documentation               │
└────────────────────────────────────────────────────────────────┘

Total Duration: 10 weeks (2.5 months)
Estimated Effort: ~200-250 hours
```

---

## 8. Success Criteria & Metrics

### 8.1 Performance Targets

**Backend Performance**:
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Dashboard API response time | 250ms | <50ms | p95 latency |
| Queries per dashboard load | 8+ | ≤3 | API call count |
| Database query time | 200ms avg | <30ms avg | Query profiling |
| Cache hit rate | 0% | >80% | Redis metrics |
| Concurrent users | N/A | 10+ | Load testing |

**Frontend Performance**:
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| First Contentful Paint | N/A | <1.5s | Lighthouse |
| Time to Interactive | N/A | <3s | Lighthouse |
| Largest Contentful Paint | N/A | <2.5s | Lighthouse |
| Bundle size (gzipped) | N/A | <200KB | Vite build |
| Lighthouse score | N/A | >90 | Lighthouse audit |

### 8.2 User Experience Metrics

**Usability Targets**:
- Time to find specific job: <30 seconds (currently 2+ minutes)
- Clicks to perform common action: ≤3 clicks
- Mobile usability score: >90 (PageSpeed Insights)
- Error rate: <0.1% of user actions
- Real-time update latency: <1 second

**Functionality Checklist**:
- [ ] Real-time dashboard updates (no manual refresh needed)
- [ ] Job search/filtering works correctly
- [ ] Application status tracking accurate
- [ ] Document preview functional
- [ ] Charts display correct data
- [ ] Pipeline visualization accurate
- [ ] Activity feed shows live events
- [ ] Dark mode toggle works
- [ ] Mobile layout usable

### 8.3 Technical Quality Metrics

**Code Quality**:
- Test coverage: >80% (unit + integration)
- TypeScript strict mode: Enabled
- ESLint violations: 0
- Bundle size: <200KB (gzipped)
- Accessibility (WCAG 2.1): Level AA compliance

**Security**:
- OWASP Top 10: All mitigated
- CSRF protection: Enabled
- XSS prevention: Sanitization implemented
- SQL injection: Parameterized queries only
- Authentication: Session-based with secure cookies

### 8.4 Acceptance Criteria

**Phase 1 (Foundation)**:
- ✅ Database queries run <50ms (p95)
- ✅ New API endpoints return correct data
- ✅ Vue.js app loads and authenticates
- ✅ No breaking changes to existing functionality

**Phase 2 (Core Features)**:
- ✅ Dashboard displays all metrics accurately
- ✅ Real-time updates work without refresh
- ✅ Charts render with correct data
- ✅ Recent applications table functional
- ✅ Pipeline visualization shows correct counts

**Phase 3 (Advanced Features)**:
- ✅ Database visualization demo-ready
- ✅ Document preview works for PDF/DOCX
- ✅ Dark mode fully functional
- ✅ Mobile layout usable on phone/tablet

**Phase 4 (Production)**:
- ✅ All tests passing (>80% coverage)
- ✅ No critical bugs in production
- ✅ Performance targets met
- ✅ Documentation complete

---

## Appendix A: Technology Comparison

### Vue.js vs React vs Alpine.js

| Criterion | Vue.js 3 | React 18 | Alpine.js |
|-----------|----------|----------|-----------|
| Learning curve | Easy | Medium | Very Easy |
| Bundle size | 34KB | 42KB | 15KB |
| Performance | Excellent | Excellent | Good |
| Ecosystem | Large | Largest | Small |
| TypeScript support | Excellent | Excellent | Limited |
| State management | Pinia (official) | Many options | Basic |
| Reactivity | Built-in | Hooks | Directives |
| SSR support | Yes (Nuxt) | Yes (Next) | No |
| Developer experience | Excellent | Good | Good |
| **Recommendation** | ✅ **SELECTED** | Good alternative | Too limited |

**Decision**: Vue.js 3 selected for optimal balance of performance, DX, and bundle size.

---

## Appendix B: Database Schema Changes

**New Tables Created**:
```sql
-- Metrics aggregation
dashboard_metrics_hourly
dashboard_metrics_daily

-- Materialized view
application_summary_mv
```

**New Indexes Added**:
```sql
idx_jobs_created_at
idx_jobs_eligibility_priority
idx_applications_created_status
idx_analyzed_jobs_eligible
idx_pre_analyzed_queued
idx_cleaned_jobs_timestamp
idx_raw_scrapes_timestamp
idx_companies_name_trgm
```

**Migration Strategy**:
1. Run migrations during low-traffic window
2. Create indexes concurrently (no table locks)
3. Build materialized view in background
4. Test query performance before switching
5. Keep rollback script ready

---

## Appendix C: API Versioning Strategy

**Approach**: URL-based versioning (`/api/v2/`)

**Migration Plan**:
- `/api/dashboard/*` (v1) → Deprecated, maintain for 3 months
- `/api/v2/dashboard/*` (v2) → New optimized endpoints
- Frontend uses v2 exclusively
- Legacy integrations (if any) use v1 until migrated

**Sunset Timeline**:
- Week 1-4: Both v1 and v2 available
- Week 5-8: v1 deprecated, warning logs added
- Week 9+: v1 removed, v2 only

---

## Document Status

**Planning Status**: ✅ Complete
**Next Phase**: Implementation (Phase 1 - Foundation)
**Approval Required**: Yes (review planning document before starting implementation)
**Estimated Start Date**: After approval
**Estimated Completion**: 10 weeks from start

---

**Document Prepared By**: Claude Code (Sonnet 4.5)
**Last Updated**: October 9, 2025
**Version**: 1.0
