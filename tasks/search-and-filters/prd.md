---
title: "Prd"
type: technical_doc
component: general
status: draft
tags: []
---

# PRD: Search & Filters Enhancement

## Overview
Add comprehensive search and filtering capabilities to the dashboard. Enhance existing views (Jobs, Applications) with real-time search, advanced filters, and state persistence.

## Current State
- Jobs view: Basic filter dropdown (all/eligible/not_eligible/applied)
- Applications view: Status, company, date range filters
- No global search functionality
- No filter state persistence
- Basic filtering implementation

## Requirements

### 1. Global Search Functionality
**Search Targets:**
- Jobs: Search by title, company, location, description keywords
- Applications: Search by job title, company name

**Features:**
- Real-time search with debouncing (500ms)
- Search across multiple fields simultaneously
- Case-insensitive matching
- Partial match support
- Clear search button

### 2. Advanced Filtering - Jobs View
**Existing Filters (Enhance):**
- Status: all/eligible/not_eligible/applied

**New Filters to Add:**
- Salary range (min/max sliders)
- Location (dropdown with autocomplete)
- Remote options (on-site/hybrid/remote)
- Job type (full-time/part-time/contract)
- Seniority level (junior/mid/senior/lead)
- Posted date (last 24h/7d/30d/all)

### 3. Advanced Filtering - Applications View
**Existing Filters (Keep):**
- Status: all/sent/pending/failed
- Company: text search
- Date range: from/to

**New Filters to Add:**
- Coherence score range (slider 0-10)
- Document count (has documents/no documents)
- Sort by additional fields (coherence score)

### 4. Filter State Persistence
**Requirements:**
- Save filter state to localStorage
- Restore filters on page load
- Clear all filters button
- Filter state survives page refresh
- Per-view filter state (jobs vs applications)

### 5. UI/UX Enhancements
**Search Bar:**
- Prominent placement in header
- Search icon indicator
- Clear button when text entered
- Loading indicator during search
- Results count display

**Filter Panel:**
- Collapsible filter panel
- Active filters badge count
- Clear individual filters
- Apply/Reset buttons

## Technical Implementation

### Backend Changes
**Enhance Existing Endpoints:**
- `/api/v2/dashboard/jobs` - Add search parameter
- `/api/v2/dashboard/applications` - Add search parameter

**New Query Parameters:**
- `search`: Full-text search string
- `salary_min`, `salary_max`: Salary range
- `remote_options`: Filter by remote/hybrid/onsite
- `job_type`: Filter by employment type
- `seniority_level`: Filter by experience level
- `posted_within`: Filter by recency (24h/7d/30d)
- `score_min`, `score_max`: Coherence score range

### Frontend Changes
**Jobs View (`dashboard_jobs.html`):**
- Add search bar to header
- Expand filter panel with new controls
- Implement debounced search
- Add localStorage persistence
- Update Alpine.js state

**Applications View (`dashboard_applications.html`):**
- Add search bar to header
- Add coherence score filter
- Implement debounced search
- Add localStorage persistence

### Performance Considerations
- Debounce search input (500ms)
- Use ILIKE for case-insensitive search (PostgreSQL)
- Index commonly searched fields
- Limit search results to prevent overload
- Client-side debouncing to reduce API calls

## Success Criteria
- Search returns results within 200ms
- Debouncing prevents excessive API calls
- Filters work in combination
- Filter state persists across page refreshes
- Clear all filters resets to default state
- No performance degradation with complex queries
- Mobile responsive filter UI

## Out of Scope
- Full-text search indexing (use simple ILIKE/LIKE)
- Search suggestions/autocomplete
- Advanced query syntax (AND/OR operators)
- Search history
- Saved filter presets
- Search analytics

## Implementation Notes
- Use existing materialized views where possible
- Follow Alpine.js patterns from existing views
- Maintain consistent styling with dashboard theme
- Add inline comments for complex filter logic
- Test with large datasets (1000+ records)
