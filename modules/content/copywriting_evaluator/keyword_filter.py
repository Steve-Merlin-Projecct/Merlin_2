#!/usr/bin/env python3
"""
Keyword Filter - Stage 1 Processing

Filters sentences based on brand alignment keywords before expensive LLM processing.
Implements case-insensitive matching against keyword database.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import logging
import re
from typing import Dict, List, Set, Optional
from datetime import datetime

# Database integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class KeywordFilter:
    """
    Stage 1: Keyword filtering for brand alignment
    
    Features:
    - Case-insensitive keyword matching
    - Word boundary detection to avoid partial matches
    - Database-driven keyword management
    - Comprehensive logging and statistics
    - Batch processing optimization
    """
    
    def __init__(self):
        """Initialize keyword filter"""
        self.db = DatabaseManager()
        self._cached_keywords: Optional[Set[str]] = None
        self._cache_updated: Optional[datetime] = None
        self._cache_duration_minutes = 60  # Cache keywords for 1 hour
        
        logger.info("Keyword filter initialized")
    
    def _get_active_keywords(self) -> Set[str]:
        """
        Get active keywords from database with caching
        
        Returns:
            Set of active keywords (lowercase for case-insensitive matching)
        """
        # Check if cache is valid
        if (self._cached_keywords is not None and 
            self._cache_updated is not None and
            (datetime.now() - self._cache_updated).total_seconds() < (self._cache_duration_minutes * 60)):
            return self._cached_keywords
        
        try:
            # Fetch active keywords from database
            query = "SELECT keyword FROM keyword_filters WHERE status = 'active'"
            results = self.db.execute_query(query, ())
            
            # Convert to lowercase set for case-insensitive matching
            keywords = {row[0].lower().strip() for row in results if row[0] and row[0].strip()}
            
            # Update cache
            self._cached_keywords = keywords
            self._cache_updated = datetime.now()
            
            logger.info(f"Loaded {len(keywords)} active keywords: {sorted(keywords)}")
            return keywords
            
        except Exception as e:
            logger.error(f"Failed to load keywords from database: {str(e)}")
            # Return empty set on error to avoid blocking processing
            return set()
    
    def _contains_keyword(self, text: str, keywords: Set[str]) -> tuple[bool, List[str]]:
        """
        Check if text contains any of the specified keywords
        
        Args:
            text: Text to search
            keywords: Set of keywords to search for (should be lowercase)
            
        Returns:
            Tuple of (found_keywords_exist, list_of_found_keywords)
        """
        if not text or not keywords:
            return False, []
        
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in keywords:
            # Use word boundaries to ensure exact word matches
            # This prevents matching "meticulous" within "unmeticulous" etc.
            pattern = r'\b' + re.escape(keyword) + r'\b'
            
            if re.search(pattern, text_lower):
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    def process_sentence(self, sentence: Dict, keywords: Set[str], session_id: str) -> Dict:
        """
        Process a single sentence through keyword filtering
        
        Args:
            sentence: Sentence dictionary with content and metadata
            keywords: Set of active keywords
            session_id: Session identifier for tracking
            
        Returns:
            Processing result dictionary
        """
        try:
            content_text = sentence.get('content_text', '').strip()
            sentence_id = sentence.get('id')
            table_name = sentence.get('table_name')
            
            if not content_text:
                logger.warning(f"Empty content_text for sentence {sentence_id}")
                return {
                    'id': sentence_id,
                    'table_name': table_name,
                    'status': 'rejected',
                    'rejection_reason': 'empty_content',
                    'processing_stage': 'keyword_filter',
                    'keywords_found': [],
                    'content_length': 0
                }
            
            # Check for keyword matches
            has_keywords, found_keywords = self._contains_keyword(content_text, keywords)
            
            # Determine status based on keyword presence
            if has_keywords:
                status = 'approved'
                logger.debug(f"Sentence {sentence_id} APPROVED - found keywords: {found_keywords}")
            else:
                status = 'rejected'
                logger.debug(f"Sentence {sentence_id} REJECTED - no brand alignment keywords found")
            
            return {
                'id': sentence_id,
                'table_name': table_name,
                'status': status,
                'rejection_reason': 'no_brand_keywords' if status == 'rejected' else None,
                'processing_stage': 'keyword_filter',
                'keywords_found': found_keywords,
                'content_length': len(content_text),
                'content_preview': content_text[:100] + '...' if len(content_text) > 100 else content_text
            }
            
        except Exception as e:
            logger.error(f"Error processing sentence {sentence.get('id')}: {str(e)}")
            return {
                'id': sentence.get('id'),
                'table_name': sentence.get('table_name'),
                'status': 'error',
                'error_message': str(e),
                'processing_stage': 'keyword_filter',
                'keywords_found': [],
                'content_length': 0
            }
    
    async def process_batch(self, sentences: List[Dict], session_id: str) -> List[Dict]:
        """
        Process batch of sentences through keyword filtering
        
        Args:
            sentences: List of sentence dictionaries to process
            session_id: Session identifier for tracking
            
        Returns:
            List of processing result dictionaries
        """
        if not sentences:
            logger.info("No sentences to process in keyword filter")
            return []
        
        logger.info(f"Processing {len(sentences)} sentences through keyword filter (session: {session_id})")
        
        try:
            # Load active keywords
            keywords = self._get_active_keywords()
            
            if not keywords:
                logger.warning("No active keywords found - all sentences will be rejected")
            
            # Process each sentence
            results = []
            approved_count = 0
            rejected_count = 0
            error_count = 0
            
            for sentence in sentences:
                result = self.process_sentence(sentence, keywords, session_id)
                results.append(result)
                
                # Track statistics
                if result['status'] == 'approved':
                    approved_count += 1
                elif result['status'] == 'rejected':
                    rejected_count += 1
                else:
                    error_count += 1
            
            # Log batch statistics
            logger.info(f"Keyword filter batch complete: {approved_count} approved, "
                       f"{rejected_count} rejected, {error_count} errors")
            
            return results
            
        except Exception as e:
            logger.error(f"Keyword filter batch processing failed: {str(e)}")
            # Return error results for all sentences
            return [
                {
                    'id': sentence.get('id'),
                    'table_name': sentence.get('table_name'),
                    'status': 'error',
                    'error_message': f"Batch processing error: {str(e)}",
                    'processing_stage': 'keyword_filter',
                    'keywords_found': [],
                    'content_length': 0
                }
                for sentence in sentences
            ]
    
    def get_filter_statistics(self) -> Dict:
        """
        Get keyword filter statistics and status
        
        Returns:
            Dictionary with filter statistics
        """
        try:
            keywords = self._get_active_keywords()
            
            return {
                'active_keywords_count': len(keywords),
                'active_keywords': sorted(keywords),
                'cache_status': 'valid' if self._cached_keywords is not None else 'empty',
                'cache_updated': self._cache_updated.isoformat() if self._cache_updated else None,
                'cache_duration_minutes': self._cache_duration_minutes
            }
            
        except Exception as e:
            logger.error(f"Failed to get filter statistics: {str(e)}")
            return {
                'error': str(e),
                'active_keywords_count': 0,
                'active_keywords': [],
                'cache_status': 'error'
            }
    
    def refresh_keyword_cache(self) -> Dict:
        """
        Force refresh of keyword cache
        
        Returns:
            Cache refresh result
        """
        try:
            self._cached_keywords = None
            self._cache_updated = None
            
            keywords = self._get_active_keywords()
            
            return {
                'success': True,
                'message': f'Keyword cache refreshed: {len(keywords)} keywords loaded',
                'keywords_count': len(keywords),
                'keywords': sorted(keywords)
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh keyword cache: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Utility functions for external integration

def process_sentences_through_keyword_filter(sentences: List[Dict], session_id: Optional[str] = None) -> List[Dict]:
    """
    Convenience function to process sentences through keyword filtering
    
    Args:
        sentences: List of sentence dictionaries
        session_id: Optional session identifier
        
    Returns:
        List of processing results
    """
    import asyncio
    
    if session_id is None:
        session_id = f"keyword_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    filter_instance = KeywordFilter()
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(filter_instance.process_batch(sentences, session_id))
    finally:
        loop.close()

def get_keyword_filter_status() -> Dict:
    """Get keyword filter status and statistics"""
    filter_instance = KeywordFilter()
    return filter_instance.get_filter_statistics()