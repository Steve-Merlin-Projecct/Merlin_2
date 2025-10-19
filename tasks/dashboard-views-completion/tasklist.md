# Task List: Complete Dashboard Views

## Parent Task 1: Applications View Backend ✅
- [x] 1.1: Create `/api/v2/dashboard/applications` endpoint in dashboard_api_v2.py
- [x] 1.2: Query application_summary_mv with filters (status, company, date)
- [x] 1.3: Implement pagination logic (20 per page)
- [x] 1.4: Add sorting support (date, company, status)
- [x] 1.5: Test endpoint with curl/Postman

## Parent Task 2: Applications View Frontend ✅
- [x] 2.1: Create route `/dashboard/applications` in app_modular.py
- [x] 2.2: Enhance dashboard_applications.html with Alpine.js logic
- [x] 2.3: Add filter controls (status dropdown, company search, date range)
- [x] 2.4: Implement sorting UI (clickable headers)
- [x] 2.5: Add pagination controls
- [x] 2.6: Test in browser with real data

## Parent Task 3: Analytics View Backend ✅
- [x] 3.1: Verify `/api/v2/dashboard/metrics/timeseries` endpoint works
- [x] 3.2: Add aggregation endpoint `/api/v2/dashboard/analytics/summary` for chart data
- [x] 3.3: Query dashboard_metrics_daily table for charts
- [x] 3.4: Format data for Chart.js consumption
- [x] 3.5: Test endpoints return proper JSON

## Parent Task 4: Analytics View Frontend ✅
- [x] 4.1: Create route `/dashboard/analytics` in app_modular.py
- [x] 4.2: Enhance dashboard_analytics.html with Chart.js integration
- [x] 4.3: Implement Scraping Velocity line chart
- [x] 4.4: Implement Application Success Rate line chart
- [x] 4.5: Implement Pipeline Conversion funnel chart
- [x] 4.6: Implement AI Usage area chart
- [x] 4.7: Add time range selector (7d/30d/90d)
- [x] 4.8: Test charts render with real data

## Parent Task 5: Schema View ✅
- [x] 5.1: Create route `/dashboard/schema` in app_modular.py
- [x] 5.2: Copy database_schema.html to dashboard_schema.html
- [x] 5.3: Add navigation bar matching other dashboard pages
- [x] 5.4: Make responsive for dashboard layout
- [x] 5.5: Test schema view displays correctly

## Parent Task 6: Navigation & Integration ✅
- [x] 6.1: Add Schema link to navigation in all dashboard templates
- [x] 6.2: Update active state highlighting for all nav links
- [x] 6.3: Ensure consistent styling across all views
- [x] 6.4: Test navigation flow between all pages

## Parent Task 7: Testing & Documentation
- [x] 7.1: Test all views with empty database
- [x] 7.2: Test all views with real data
- [x] 7.3: Test mobile responsiveness
- [x] 7.4: Document new endpoints in code
- [ ] 7.5: Update task context and PURPOSE.md
