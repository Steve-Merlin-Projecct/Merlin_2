# Product Requirements Document: Database Table Consolidation
## Job Analysis and Analyzed Jobs Table Merger

**Version:** 1.0  
**Date:** September 12, 2025  
**Author:** AI Analysis System  

## 1. Introduction/Overview

This PRD outlines the consolidation of two redundant database tables (`job_analysis` and `analyzed_jobs`) into a single, unified table structure. Currently, the system maintains two separate tables that store overlapping AI job analysis data, creating unnecessary complexity, potential data inconsistencies, and performance overhead from required table joins.

The goal is to eliminate data redundancy, simplify the codebase, and create a single source of truth for job analysis data while maintaining all existing functionality.

## 2. Goals

1. **Eliminate Data Redundancy**: Merge overlapping fields from both tables into a single, comprehensive table
2. **Simplify Data Access**: Remove the need for joins between `job_analysis` and `analyzed_jobs` tables
3. **Improve Performance**: Reduce query complexity and potential join overhead
4. **Maintain Data Integrity**: Ensure no data loss during the migration process
5. **Preserve Functionality**: All existing features must continue to work without disruption
6. **Reduce Maintenance Overhead**: Simplify database schema management

## 3. User Stories

**As a System Administrator:**
- I want a simplified database schema so that maintenance and troubleshooting are easier
- I want faster query performance so that the application responds more quickly to users

**As a Developer:**
- I want a single table to query for job analysis data so that I don't need to write complex join queries
- I want consistent data access patterns so that the codebase is easier to understand and maintain

**As an AI Analysis System:**
- I want to write analysis results to a single location so that data consistency is guaranteed
- I want to avoid duplicate data storage so that system resources are used efficiently

## 4. Functional Requirements

### 4.1 Schema Consolidation Requirements
1. The system must merge all columns from both `job_analysis` and `analyzed_jobs` tables into the `analyzed_jobs` table structure
2. The system must preserve all existing data types and constraints from both tables
3. The system must handle column name conflicts by using the more descriptive/comprehensive version
4. The system must maintain all foreign key relationships to other tables

### 4.2 Data Migration Requirements
6. The system must handle conflicts where both tables contain data for the same job_id
7. The system must maintain referential integrity across all related tables during migration

### 4.3 Code Migration Requirements
9. The system must update all INSERT operations that currently target `job_analysis` table
10. The system must update all SELECT operations that currently join both tables
11. The system must update all UPDATE operations that modify either table
12. The system must update all foreign key references from other tables

### 4.4 Testing Requirements
13. The system must verify that all existing functionality works after migration
14. The system must validate data integrity across all related operations
15. The system must ensure performance is maintained or improved after consolidation

## 5. Non-Goals (Out of Scope)

1. **Schema Changes**: This migration will not modify the essential data structure or add new analytical capabilities
2. **Performance Optimization Beyond Consolidation**: Advanced query optimization or indexing improvements are out of scope
3. **UI/UX Changes**: No user-facing changes are required for this migration
4. **New Features**: This project focuses solely on consolidation, not adding new functionality
5. **Third-party Integrations**: Changes to external API integrations are not included

## 6. Design Considerations

### 6.1 Target Table Structure
- Use `analyzed_jobs` as the target table (51 columns, actively used)
- Add missing columns from `job_analysis` to `analyzed_jobs`
- Preserve all existing column names and data types
- Maintain all existing indexes and constraints

### 6.2 Migration Strategy
- **Gradual Migration Approach** (Recommended):
  - Phase 1: Add missing columns to `analyzed_jobs`
  - Phase 2: Migrate code to read from `analyzed_jobs` only
  - Phase 3: Migrate code to write to `analyzed_jobs` only
  - Phase 4: Migrate existing data
  - Phase 5: Drop `job_analysis` table

## 7. Technical Considerations

### 7.1 Affected Code Modules
- `modules/ai_job_description_analysis/normalized_db_writer.py` (Primary data writer)
- `modules/workflow/application_orchestrator.py` (Primary data reader)
- `modules/content/document_generation/` (Resume/cover letter generators)
- `modules/scraping/jobs_populator.py` (Duplicate detection logic)
- `modules/matching/preference_matcher.py` (Job matching logic)
- All test files referencing either table (23+ files)

### 7.2 Database Dependencies
- **Foreign Key Relationships**: Multiple tables reference `job_analysis.job_id`
- **Related Tables**: `job_skills`, `job_benefits`, `job_red_flags_details`, `job_ats_keywords`, etc.
- **Indexes**: Preserve existing indexes on both tables during consolidation

### 7.3 Risk Mitigation
- **Complete Data Backup**: Full backup before any changes
- **Rollback Plan**: Ability to restore from backup if issues occur
- **Staging Environment Testing**: Full testing in non-production environment
- **Gradual Deployment**: Phase-by-phase implementation to minimize risk

## 8. Success Metrics

### 8.2 Quality Metrics
- **Functional Integrity**: All existing features must continue to work

### 8.3 Operational Metrics
- **Bug Introduction**: Zero new bugs related to data access

## 10. Open Questions

1. **Data Conflict Resolution**: How should conflicts be handled when both tables contain different values for the same job_id and field?
   answer use data in analyzed_jobs. discard data in job_analysis
3. **Migration Timing**: What is the preferred maintenance window for this migration?
    answer = now, asap.
4. **Backup Retention**: How long should the backup of the original tables be retained?
    answer = no backup required, the data is test data
5. **Performance Testing**: What specific performance benchmarks should be established before migration?
    answer = none
6. **Rollback Criteria**: What specific conditions would trigger a rollback to the original structure?
    answer = none. ignore

## 11. Dependencies

- **Database Access**: Read/write access to production database required
- **Code Deployment**: Ability to deploy code changes in coordinated phases
- **Testing Environment**: Staging environment that mirrors production data structure. No, not required. Ignore.
- **Backup Systems**: Database backup and restore capabilities. No, not required. Ignore.


## 12. Risk Assessment

### High Risk
- **Data Loss**: Potential for data loss during migration. Proceed anyway
- **System Downtime**: Extended downtime if migration encounters issues.  Proceed anyway

### Medium Risk
- **Performance Regression**: Possible performance impacts if not properly tested.  Proceed anyway
- **Code Bugs**: Introduction of bugs in updated data access code.  Proceed anyway

### Low Risk
- **User Impact**: Minimal user-facing impact expected.  Proceed anyway
- **Third-party Integration**: No expected impact on external integrations.  Proceed anyway

---

**Next Steps:**
1. Review and approve this PRD
2. Set up dedicated staging environment for testing
3. Begin Phase 1: Schema Analysis & Preparation
4. Schedule coordination meeting with development team