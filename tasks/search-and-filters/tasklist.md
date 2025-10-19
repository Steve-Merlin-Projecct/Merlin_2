# Task List: Search & Filters Implementation

## Parent Task 1: Backend - Jobs Search Enhancement ✅
- [x] 1.1: Add search parameter to `/api/v2/dashboard/jobs` endpoint
- [x] 1.2: Implement full-text search across title, company, location
- [x] 1.3: Add salary range filters (salary_min, salary_max)
- [x] 1.4: Add remote_options filter (on-site/hybrid/remote)
- [x] 1.5: Add job_type and seniority_level filters
- [x] 1.6: Add posted_within filter (date recency)
- [x] 1.7: Test all filters work individually and combined

## Parent Task 2: Backend - Applications Search Enhancement ✅
- [x] 2.1: Add search parameter to `/api/v2/dashboard/applications` endpoint
- [x] 2.2: Implement search across job_title and company_name
- [x] 2.3: Add coherence score range filter (score_min, score_max)
- [x] 2.4: Test search and filters

## Parent Task 3: Frontend - Jobs View Enhancement
- [ ] 3.1: Add search bar to jobs view header
- [ ] 3.2: Implement debounced search (500ms delay)
- [ ] 3.3: Add salary range sliders
- [ ] 3.4: Add remote options dropdown
- [ ] 3.5: Add job type and seniority filters
- [ ] 3.6: Add posted date filter
- [ ] 3.7: Implement localStorage persistence
- [ ] 3.8: Add clear all filters button
- [ ] 3.9: Show active filter count badge

## Parent Task 4: Frontend - Applications View Enhancement
- [ ] 4.1: Add search bar to applications view header
- [ ] 4.2: Implement debounced search (500ms delay)
- [ ] 4.3: Add coherence score range slider
- [ ] 4.4: Implement localStorage persistence
- [ ] 4.5: Update clear filters to include new fields

## Parent Task 5: Testing & Polish
- [ ] 5.1: Test search with empty query
- [ ] 5.2: Test filter combinations
- [ ] 5.3: Test localStorage persistence
- [ ] 5.4: Test mobile responsiveness
- [ ] 5.5: Performance test with 1000+ records
- [ ] 5.6: Browser compatibility testing
