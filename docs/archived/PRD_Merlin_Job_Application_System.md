---
title: Merlin PRD - Automated Job Application System
version: '2.0'
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: archived
status: archived
tags:
- merlin
- application
- system
---

# Merlin PRD - Automated Job Application System
**Owner**: Steve Glen  
**Date**: 2025-07-05  
**Version**: 2.0 (Pre-Refactoring)

## 1. Overview
> This machine automates the complete process of applying for Marketing Manager positions in Edmonton, Alberta. The system scrapes job postings, analyzes them with AI, generates personalized application materials, and tracks application success to maximize interview opportunities.

## 2. Goals
> - **Primary**: Increase interviews to 4+ per month (from current baseline)
> - **Secondary**: Reduce time spent applying to jobs down to 0 within 6 months
> - **Tertiary**: Achieve 15%+ application-to-interview conversion rate
> - **Long-term**: Automate 100% of job application workflow with intelligent targeting

## 3. User Stories
> ### Primary User: Steve Glen (Job Seeker)
> - As a job seeker, I want recruiters to call me so that I can interview for Marketing Manager positions
> - As a busy professional, I want the system to apply to relevant jobs automatically so I can focus on interview preparation
> - As a strategic candidate, I want personalized application materials that address specific employer needs
> - As a data-driven person, I want analytics on application performance to optimize my strategy

> ### Secondary Users: System Administrators
> - As a system admin, I want comprehensive monitoring so I can ensure the system runs reliably
> - As a security-conscious operator, I want protection against LLM injection attacks and data breaches

## 4. Features

### Feature A: Intelligent Job Discovery & Scraping
> - **Description**: Automatically discovers and scrapes job postings from multiple sources using contextual preference packages
> - **Sub-features**:
>   - Multi-source job scraping (Indeed, LinkedIn, company websites)
>   - Intelligent search generation based on user preferences  
>   - Duplicate detection and deduplication across sources
>   - Two-stage processing pipeline (raw → cleaned → processed)
>   - Cost-effective Apify integration with usage monitoring
> - **Acceptance Criteria**: 
>   - [ ] System scrapes 50+ relevant jobs per day from Indeed
>   - [ ] Duplicate detection achieves 95%+ accuracy
>   - [ ] Processing pipeline handles 1000+ jobs without errors
>   - [ ] Monthly scraping costs stay under $50

### Feature B: Advanced AI Job Analysis  
> - **Description**: Analyzes job descriptions using Google Gemini to extract insights and optimize applications
> - **Sub-features**:
>   - Skills extraction with importance rankings (1-10 scale)
>   - Job authenticity validation and credibility scoring
>   - Industry classification and seniority level detection
>   - **NEW**: Implicit requirements analysis (leadership, adaptability, cross-functional)
>   - **NEW**: ATS optimization with 5-15 keyword extraction
>   - **NEW**: Cover letter insights identifying employer pain points
>   - LLM injection protection with military-grade security
> - **Acceptance Criteria**:
>   - [ ] AI analysis completes within 30 seconds per job batch
>   - [ ] Accuracy rate of 90%+ for skills extraction
>   - [ ] Security system blocks 100% of injection attempts
>   - [ ] Free tier usage stays within 1,500 requests/day limit

### Feature C: Contextual Job Matching & Filtering
> - **Description**: Intelligent filtering based on multiple preference packages considering location, salary, and context
> - **Sub-features**:
>   - Multiple preference packages per user (Local, Regional, Remote)
>   - Contextual salary logic (higher pay for longer commutes)
>   - Location-aware filtering with distance calculations
>   - Industry and company size preferences
>   - Work arrangement matching (remote/hybrid/onsite)
> - **Acceptance Criteria**:
>   - [ ] Preference matching accuracy of 85%+ for relevant jobs
>   - [ ] System processes 3 different preference packages simultaneously
>   - [ ] Salary expectations adjust correctly based on location context
>   - [ ] False positive rate under 10% for job matching

### Feature D: Personalized Document Generation
> - **Description**: Generates customized resumes and cover letters tailored to specific job requirements
> - **Sub-features**:
>   - Harvard MCS template-based resume generation
>   - Professional cover letter creation with business formatting
>   - ATS-optimized keyword integration
>   - Employer pain point addressing in cover letters
>   - Document metadata with professional properties
>   - Cloud storage with Replit Object Storage
> - **Acceptance Criteria**:
>   - [ ] Document generation completes within 15 seconds
>   - [ ] Generated documents pass ATS scanning with 90%+ keyword match
>   - [ ] Documents maintain professional formatting across all templates
>   - [ ] Storage costs remain under $10/month

### Feature E: Automated Application Submission
> - **Description**: Submits applications through multiple channels with tracking and follow-up
> - **Sub-features**:
>   - Email-based application submission with attachments
>   - Portal-based applications (future enhancement)
>   - Application tracking with unique identifiers
>   - Follow-up scheduling and reminders
>   - Success rate monitoring and analytics
> - **Acceptance Criteria**:
>   - [ ] Email applications submit successfully 98%+ of the time
>   - [ ] All applications tracked with unique identifiers
>   - [ ] Follow-up reminders sent after 1 week automatically
>   - [ ] Success metrics available in real-time dashboard

### Feature F: Performance Analytics & Optimization
> - **Description**: Comprehensive analytics dashboard showing application performance and optimization insights
> - **Sub-features**:
>   - Real-time application statistics and success rates
>   - A/B testing for different application approaches
>   - Interview conversion tracking
>   - ROI analysis and cost optimization
>   - Performance alerts and recommendations
> - **Acceptance Criteria**:
>   - [ ] Dashboard updates in real-time with new applications
>   - [ ] Conversion tracking accuracy of 95%+
>   - [ ] Monthly cost analysis with optimization recommendations
>   - [ ] Alert system triggers within 5 minutes of issues

### Feature G: Security & Compliance
> - **Description**: Enterprise-grade security protecting against attacks and ensuring data privacy
> - **Sub-features**:
>   - LLM injection protection with input sanitization
>   - Response validation and anomaly detection
>   - Rate limiting and DDoS protection
>   - Secure credential management
>   - GDPR-compliant data handling
> - **Acceptance Criteria**:
>   - [ ] Security score of 95%+ maintained
>   - [ ] Zero successful injection attacks
>   - [ ] Rate limiting blocks 100% of abuse attempts
>   - [ ] Data encryption in transit and at rest

## 5. Technical Specs
> - **Database**: PostgreSQL with 8 specialized tables
> - **AI**: Google Gemini 2.0 Flash (free tier) with Gemini 2.5 Flash upgrade path
> - **Storage**: Replit Object Storage for document management
> - **APIs**: 
>   - New `/api/ai/analyze-jobs` for batch job analysis
>   - Enhanced `/api/intelligent-scrape` for contextual job discovery
>   - Upgraded `/resume` and `/cover-letter` endpoints for document generation
> - **Security**: Military-grade LLM protection with 35+ security token integrations
> - **Monitoring**: Real-time dashboards with usage tracking and performance metrics

## 6. Phases
> ### Phase 1 (MVP - COMPLETED)
> - ✅ Create and send resume by email
> - ✅ Basic job scraping from Indeed
> - ✅ Simple document generation

> ### Phase 2 (COMPLETED)  
> - ✅ Scrape job descriptions and customize resumes
> - ✅ AI-powered job analysis with Gemini
> - ✅ Automated email submission with tracking

> ### Phase 3 (CURRENT - ENHANCEMENT)
> - ✅ Multi-source job scraping with deduplication
> - ✅ Advanced AI analysis with implicit requirements
> - ✅ Contextual preference packages
> - ✅ Security hardening with injection protection
> - 🔄 **NEXT**: Code refactoring and architecture optimization

> ### Phase 4 (FUTURE)
> - 🎯 Portal-based application submission
> - 🎯 LinkedIn integration for enhanced targeting
> - 🎯 Interview scheduling automation
> - 🎯 Performance optimization with machine learning

## 7. Success Metrics
> - **Interview Rate**: 4+ interviews per month
> - **Application Volume**: 100+ applications per month
> - **Conversion Rate**: 15%+ application-to-interview ratio
> - **Time Savings**: 40+ hours per month recovered
> - **Cost Efficiency**: Under $100/month total operating costs
> - **System Reliability**: 99.5%+ uptime

## 8. Risk Mitigation
> - **AI Costs**: Free tier monitoring with automatic alerts at 80% usage
> - **Security**: Multiple layers of protection against LLM injection attacks
> - **Compliance**: Educational disclaimers for all scraping activities
> - **Quality**: Comprehensive testing suite with 95%+ code coverage
> - **Scalability**: Cloud-native architecture with horizontal scaling capability

## 9. Dependencies
> - **External APIs**: Google Gemini, Apify (misceres/indeed-scraper)
> - **Infrastructure**: Replit hosting, PostgreSQL database, Object Storage
> - **Third-party Services**: Email delivery, document processing
> - **Regulatory**: Compliance with website Terms of Service and applicable laws

---
**Document Status**: Ready for Functional Requirements and Technical Design  
**Next Steps**: Create FRD, Technical Design Document, and Testing Plan