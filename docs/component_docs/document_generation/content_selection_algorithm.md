# Content Selection Algorithm for Document Generation

**Version:** 2.16.7  
**Updated:** July 29, 2025  
**Status:** Implementation Phase - Based on Cohere Summary Analysis

## Overview

This document outlines the updated intelligent content selection algorithm for resume and cover letter generation. The algorithm has been redesigned to remove sentence strength scoring and implement a sophisticated skill matching and keyword matching approach based on mathematical optimization principles.

## Algorithm Changes Summary

### **REMOVED COMPONENTS:**
- ❌ **Base Score**: Sentence strength rating (1-10 scale) - REMOVED
- ❌ **Industry Matching**: Whether job industry appears in sentence tags - REMOVED  
- ❌ **Career Path Matching**: Whether career path matches sentence tags - REMOVED

### **NEW COMPONENTS:**
- ✅ **Skill Matching**: Number of job skills matching sentence tags - ENHANCED
- ✅ **Keyword Matching**: New comprehensive keyword matching system
- ✅ **Composite Scoring**: Weighted combination of skill + keyword scores

## Natural Language Algorithm Framework

Based on university-level mathematical analysis, the algorithm follows these core principles:

### **1. Ranking Scope: Individual Section Optimization**

**Approach**: Prioritize individual section ranking for optimal content selection per section.

**Implementation Steps**:
1. **Section-Specific Scoring** for each sentence:
   - **Skill Match Score**: Alignment with required section skills
   - **Keyword Match Score**: Presence/frequency of job keywords
   - **Section Relevance**: Categorical matching (resume/workexp, coverletter/opening)

2. **Scoring Formula**:
   ```
   Section Score = (Skill Match × w1) + (Keyword Match × w2) + (Section Relevance × w3)
   Where: w1 = 0.5, w2 = 0.3, w3 = 0.2
   ```

### **2. Skill Repetition Management**

**Tiered Approach**:
1. **Section-Level Limits**: Maximum skill occurrences per section
2. **Document-Level Limits**: Global limits for high-importance skills
3. **Importance-Based Thresholds**: Adjust limits based on job skill importance

**Implementation Strategy**:
- PostgreSQL tracking of skill occurrences by section and document
- Real-time checking during sentence selection
- Decay factor for skill importance (more repetitions for critical skills)

### **3. Weighted Scoring System**

**Current Implementation** (ContentManager):
- **Skill Weight**: 0.7 (70% - Primary importance)
- **Keyword Weight**: 0.3 (30% - Secondary relevance)

**Scoring Components**:
```python
composite_score = (normalized_skill_score × 0.7) + (normalized_keyword_score × 0.3)
```

## Current Implementation Status

### **Phase 1 - COMPLETED**:
- ✅ Removed `sentence_strength` from `_calculate_relevance_score`
- ✅ Implemented `_calculate_composite_score` method
- ✅ Added `_calculate_skill_match_score` with case-insensitive matching
- ✅ Added `_calculate_keyword_match_score` with text analysis
- ✅ Updated resume and cover letter content selection methods
- ✅ Normalized scores to 0-1 scale for consistency

### **Phase 2 - PLANNED**:
- 🔄 **Section-Specific Optimization**: Implement per-section skill relevance
- 🔄 **Skill Repetition Limits**: Add section and document-level tracking
- 🔄 **Advanced Keyword Analysis**: Enhanced phrase and context matching
- 🔄 **Configuration System**: Externalize weights and limits to config files

## Technical Implementation Details

### **Updated Methods**:

1. **`_select_resume_content(job_skills, job_keywords)`**:
   - Removed industry and career path parameters
   - Added job_keywords parameter for keyword matching
   - Uses composite scoring for sentence selection

2. **`_calculate_composite_score(sentence, job_skills, job_keywords)`**:
   - Replaces old `_calculate_relevance_score`
   - Implements weighted skill + keyword matching
   - Returns normalized 0-1 composite score

3. **`_calculate_skill_match_score(sentence, job_skills)`**:
   - Case-insensitive exact skill matching
   - Ratio-based scoring (matches / total_job_skills)
   - Handles empty inputs gracefully

4. **`_calculate_keyword_match_score(sentence, job_keywords)`**:
   - Text-based keyword presence detection
   - Ratio-based scoring (matched_keywords / total_keywords)
   - Supports phrase and word-level matching

## Integration Points

### **Database Requirements**:
- `sentence_bank_resume` table: Contains approved resume content with tags
- `sentence_bank_cover_letter` table: Contains approved cover letter content
- Both tables support skill tagging and category classification

### **Job Data Requirements**:
- `skills_required`: List of job-specific skills for matching
- `keywords`: List of job keywords and phrases for relevance scoring
- Categories for cover letters: Opening, Alignment, Achievement, Closing

## Performance Considerations

- **Scoring Efficiency**: Pre-normalized scores minimize computation
- **Database Optimization**: Single queries for approved content retrieval  
- **Memory Management**: Lightweight scoring calculations with minimal overhead
- **Scalability**: Algorithm supports ~30 sentences per skill/destination type

## Testing Strategy

- **Unit Tests**: Individual scoring method validation
- **Integration Tests**: End-to-end content selection verification  
- **Performance Tests**: Scoring algorithm efficiency measurement
- **Quality Tests**: Human evaluation of selected content relevance

---

**Next Steps**: Implement Phase 2 enhancements based on user feedback and system performance analysis.