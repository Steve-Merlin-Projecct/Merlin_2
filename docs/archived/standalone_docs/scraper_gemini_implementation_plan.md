---
title: Scraper API and Gemini API Implementation Plan
status: completed
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: archived
tags:
- scraper
- gemini
- implementation
- plan
---

# Scraper API and Gemini API Implementation Plan

**Date:** July 24, 2025  
**Project Version:** 2.16  
**Priority:** High - Core AI Processing Pipeline  
**Status:** Updated with V2.16 Implementation Plan Integration  

## Current Status Assessment

### ✅ Components Already Implemented

1. **Scraper Infrastructure**
   - `ApifyJobScraper` - Misceres/Indeed scraper integration
   - `ScrapeDataPipeline` - Raw to cleaned data processing
   - `IntelligentScraper` - Preference-based targeted scraping
   - `JobsPopulator` - Transfer from cleaned scrapes to jobs table

2. **AI Analysis Infrastructure**
   - `JobAnalysisManager` - Google Gemini integration
   - `BatchAnalyzer` - Batch processing with rate limiting
   - `NormalizedAnalysisWriter` - Structured data storage
   - `AIIntegrationRoutes` - REST API endpoints

3. **Database Schema**
   - 32 normalized tables with proper relationships
   - Complete AI analysis storage structure
   - Job scraping pipeline tables

### ⚠️ Issues Requiring Immediate Attention

1. **Security**: Weak WEBHOOK_API_KEY (20 chars) - needs regeneration
2. **Import Errors**: Missing dependency imports in several modules
3. **API Integration**: Need to verify complete end-to-end functionality
4. **Secret Management**: Missing APIFY_TOKEN for scraper operations

## Implementation Plan

### Phase 1: Security and Dependencies (30 minutes)

#### 1.1 Fix Security Issues
- [x] Regenerate WEBHOOK_API_KEY with 64-character secure key
- [ ] Update all modules using the webhook key
- [ ] Verify security audit passes

#### 1.2 Resolve Import Dependencies
- [ ] Fix `dependency_manager` imports in `ai_analyzer.py`
- [ ] Fix `intelligent_scraper` imports in `app_modular.py`
- [ ] Fix missing module imports across the system
- [ ] Update path references for module reorganization

#### 1.3 Secret Configuration
- [ ] Request APIFY_TOKEN from user for scraper operations
- [ ] Verify GEMINI_API_KEY is properly configured
- [ ] Test all API connections

### Phase 2: Scraper API Implementation (45 minutes)

#### 2.1 Core Scraper Functionality
- [ ] **ApifyJobScraper Completion**
  - Verify misceres/indeed-scraper integration
  - Test job search parameter handling
  - Implement error handling and retry logic
  - Add usage tracking and cost monitoring

#### 2.2 Pipeline Integration
- [ ] **ScrapeDataPipeline Verification**
  - Test raw data processing
  - Verify confidence scoring system
  - Validate duplicate detection
  - Test data normalization

#### 2.3 API Endpoints
- [ ] **Create Scraper REST API** (`/api/scraping/`)
  - `POST /api/scraping/start-scrape` - Trigger targeted scraping
  - `GET /api/scraping/status` - Check scraping status
  - `GET /api/scraping/results` - Retrieve scraping results
  - `POST /api/scraping/manual-scrape` - Manual job search parameters

#### 2.4 Intelligent Targeting
- [ ] **IntelligentScraper Enhancement**
  - Fix preference package integration
  - Implement smart search strategy selection
  - Add geographic targeting optimization
  - Integrate with user preference profiles

### Phase 3: Gemini AI Implementation (45 minutes)

#### 3.1 Core AI Analysis
- [ ] **JobAnalysisManager Completion**
  - Fix dependency loading issues
  - Verify Google Gemini API integration
  - Test military-grade security token system
  - Validate prompt injection protection

#### 3.2 Batch Processing
- [ ] **BatchAnalyzer System**
  - Test batch job analysis (10-20 jobs per call)
  - Verify rate limiting (1,500 requests/day free tier)
  - Implement usage tracking and alerts
  - Add cost monitoring ($2.50 daily limit)

#### 3.3 Analysis Storage
- [ ] **NormalizedAnalysisWriter**
  - Test normalized database storage
  - Verify all 8 analysis tables populated
  - Validate data integrity constraints
  - Test complex query performance

#### 3.4 Enhanced Analysis Features
- [ ] **Advanced Analysis Components**
  - Skills extraction with importance ranking
  - Job authenticity validation
  - Industry classification
  - Implicit requirements analysis
  - ATS optimization keywords
  - Cover letter insights

### Phase 4: API Integration and Testing (30 minutes)

#### 4.1 End-to-End Pipeline
- [ ] **Complete Pipeline Test**
  - Scraping → Cleaning → Transfer → AI Analysis
  - Test `/api/integration/full-pipeline` endpoint
  - Verify data flow between all components
  - Test error handling and rollback

#### 4.2 API Endpoint Completion
- [ ] **AI Integration Routes** (`/api/ai/`)
  - `POST /api/ai/analyze-jobs` - Trigger AI analysis
  - `GET /api/ai/usage-stats` - Monitor API usage
  - `GET /api/ai/batch-status` - Check analysis progress
  - `POST /api/ai/reset-usage` - Reset usage counters
  - `GET /api/ai/health` - Check AI system health

#### 4.3 Authentication and Security
- [ ] **Security Implementation**
  - Verify all endpoints require authentication
  - Test rate limiting on all AI endpoints
  - Validate input sanitization
  - Test prompt injection protection

## Technical Requirements

### Scraper API Requirements

1. **Apify Integration**
   - Actor: `misceres/indeed-scraper`
   - Cost: $5/1000 results
   - Geographic targeting: Canadian Indeed (ca.indeed.com)
   - Data fields: 20+ job attributes including company logos

2. **Search Strategy**
   - Preference package-based targeting
   - Smart location radius adjustment
   - Salary range optimization
   - Industry-specific keyword enhancement

3. **Data Pipeline**
   - Raw scrape storage with complete metadata
   - Confidence scoring (0.0-1.0 range)
   - Duplicate detection and merging
   - Data normalization and validation

### Gemini AI Requirements

1. **Google Gemini Integration**
   - Model: `gemini-2.5-flash` (cost-effective)
   - Free tier: 1,500 requests/day, 15 requests/minute
   - Paid tier: $0.30/$2.50 per million tokens (input/output)
   - Security: Military-grade prompt injection protection

2. **Analysis Capabilities**
   - Skills extraction (5-15 skills with importance ranking)
   - Job authenticity validation (red flag detection)
   - Industry classification with confidence scores
   - Compensation analysis with currency detection
   - Work arrangement classification (remote/hybrid/onsite)

3. **Batch Processing**
   - 10-20 jobs per API call for efficiency
   - Queue-based processing with priority management
   - Usage tracking with spending limits
   - Automatic retry with exponential backoff

## Success Metrics

### Scraper API Success Criteria
- [ ] Successfully scrape 50+ jobs in single request
- [ ] Confidence scoring accuracy >80%
- [ ] Duplicate detection rate >95%
- [ ] API response time <30 seconds for 50 jobs
- [ ] Cost efficiency: <$0.10 per qualified job

### Gemini AI Success Criteria
- [ ] Analysis accuracy >90% for skills extraction
- [ ] Response time <10 seconds for 10-job batch
- [ ] Security: 0 successful prompt injection attempts
- [ ] Cost efficiency: <$0.05 per job analysis
- [ ] Free tier utilization: >90% of daily limits

## Dependencies and Prerequisites

### External Services
- **Apify Account**: Token required for job scraping
- **Google AI Studio**: Gemini API key (already configured)
- **PostgreSQL**: Database properly normalized (✅ complete)

### Internal Dependencies
- **Database Manager**: Connection pooling and health checks
- **Security Manager**: Input validation and sanitization
- **Content Manager**: Template-based document generation

## Risk Mitigation

### Scraper Risks
1. **Rate Limiting**: Implement respectful scraping with delays
2. **Data Quality**: Multiple validation layers and confidence scoring
3. **Cost Control**: Usage tracking with automatic stops
4. **Legal Compliance**: Educational purpose disclaimers

### AI Analysis Risks
1. **Prompt Injection**: Military-grade security token system
2. **Cost Overrun**: Daily spending limits and monitoring
3. **Rate Limits**: Queue management and retry logic
4. **Data Privacy**: No PII storage in analysis results

## Timeline

### Total Estimated Time: 2.5 hours

- **Phase 1** (Security/Dependencies): 30 minutes
- **Phase 2** (Scraper API): 45 minutes
- **Phase 3** (Gemini AI): 45 minutes
- **Phase 4** (Integration/Testing): 30 minutes

## Next Steps

1. **Immediate**: Fix security issues and import errors
2. **Short-term**: Complete scraper API implementation
3. **Medium-term**: Finalize Gemini AI integration
4. **Long-term**: Optimize performance and cost efficiency

This plan ensures comprehensive implementation of both systems with proper security, error handling, and cost management while maintaining the existing database normalization and authentication systems.